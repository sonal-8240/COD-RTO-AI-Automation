"""
SmartCOD AI - WhatsApp Confirmation & Prepaid Nudge Simulator Service
Implements conversational state machine for both Workflow A (Confirmation) and Workflow B (Prepaid Conversion),
including natural language handling, payment simulation, and time progression.
"""

import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.models import WhatsAppConversation, Order
from backend.services.financial_model import FinancialModel

def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class WhatsAppSimulatorService:
    def __init__(self, db: Session):
        self.db = db
        self.financial_model = FinancialModel()

    def start_conversation(
        self,
        order_id: str,
        workflow_type: str = "CONFIRMATION",  # "CONFIRMATION" or "PREPAID_NUDGE"
        discount_pct: float = 8.0
    ) -> WhatsAppConversation:
        """
        Initializes a new WhatsApp conversation for an order.
        """
        order = self.db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            raise ValueError(f"Order '{order_id}' not found.")

        # Check if active conversation exists
        existing = (
            self.db.query(WhatsAppConversation)
            .filter(
                WhatsAppConversation.order_id == order_id,
                WhatsAppConversation.workflow_type == workflow_type
            )
            .first()
        )
        if existing:
            return existing

        now = utc_now()
        expires_at = now + timedelta(hours=24)
        conv_id = f"WA_{order_id}_{uuid.uuid4().hex[:6].upper()}"

        # Build initial template message
        messages: List[Dict[str, Any]] = []

        if workflow_type == "CONFIRMATION":
            welcome_text = (
                f"Hi {order.customer_name}! 👋 Thank you for shopping with our haircare store.\n\n"
                f"Please confirm your Cash on Delivery order *#{order.order_id}* for *₹{order.order_value:.0f}* "
                f"({order.items or 'Haircare Essentials'}).\n\n"
                f"Reply *YES* to confirm dispatch, or *NO* to cancel this order."
            )
            discount_offered = 0.0
        else:
            # Prepaid Nudge
            discount_amt = round(order.order_value * (discount_pct / 100.0), 0)
            pay_amt = order.order_value - discount_amt
            welcome_text = (
                f"Hi {order.customer_name}! 🌟 Great news regarding your order *#{order.order_id}*!\n\n"
                f"Pay online right now via UPI / GPay / Card and get an instant *₹{discount_amt:.0f} DISCOUNT* "
                f"({discount_pct:.0f}% OFF) + *FREE Priority Shipping*! 🚀\n\n"
                f"Pay only *₹{pay_amt:.0f}* instead of ₹{order.order_value:.0f}.\n\n"
                f"Reply *PAY* to get your secure payment link, or reply *KEEP* to stay on Cash on Delivery."
            )
            discount_offered = discount_amt

        messages.append({
            "sender": "BOT",
            "text": welcome_text,
            "timestamp": now.isoformat(),
            "message_type": "text"
        })

        conv = WhatsAppConversation(
            conversation_id=conv_id,
            order_id=order_id,
            workflow_type=workflow_type,
            current_state="PENDING_REPLY",
            messages=json.dumps(messages),
            discount_offered=discount_offered,
            simulated_current_time=now,
            expires_at=expires_at,
            created_at=now,
            updated_at=now
        )

        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def process_customer_reply(
        self,
        conversation_id: str,
        user_reply_text: str
    ) -> WhatsAppConversation:
        """
        Handles incoming customer responses and triggers appropriate transitions.
        """
        conv = (
            self.db.query(WhatsAppConversation)
            .filter(WhatsAppConversation.conversation_id == conversation_id)
            .first()
        )
        if not conv:
            raise ValueError(f"Conversation '{conversation_id}' not found.")

        order = self.db.query(Order).filter(Order.order_id == conv.order_id).first()
        messages: List[Dict[str, Any]] = json.loads(conv.messages or "[]")
        now = conv.simulated_current_time or utc_now()

        # Check if expired
        if conv.expires_at and now > conv.expires_at and conv.current_state == "PENDING_REPLY":
            conv.current_state = "TIMEOUT"
            if order and order.final_status == "PENDING":
                order.final_status = "ON_HOLD"
            self.db.commit()
            return conv

        clean_text = user_reply_text.strip().lower()

        # Record customer message
        messages.append({
            "sender": "CUSTOMER",
            "text": user_reply_text,
            "timestamp": now.isoformat(),
            "message_type": "text"
        })

        # Process by workflow
        if conv.workflow_type == "CONFIRMATION":
            self._handle_confirmation_reply(conv, order, clean_text, messages, now)
        else:
            self._handle_prepaid_reply(conv, order, clean_text, messages, now)

        conv.messages = json.dumps(messages)
        conv.updated_at = now
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def _handle_confirmation_reply(
        self,
        conv: WhatsAppConversation,
        order: Optional[Order],
        text: str,
        messages: List[Dict[str, Any]],
        now: datetime
    ):
        yes_keywords = ["yes", "ha", "haan", "confirm", "bhejo", "ok", "deliver", "sure", "yep", "1"]
        no_keywords = ["no", "na", "nahi", "cancel", "mat bhejo", "don't send", "stop", "2"]

        if any(kw in text for kw in yes_keywords):
            conv.current_state = "CONFIRMED"
            bot_reply = (
                f"✅ Thank you for confirming! Your order *#{conv.order_id}* has been verified "
                f"and prioritized for courier dispatch today. We'll share your tracking link soon!"
            )
            if order:
                order.final_status = "CONFIRMED"
        elif any(kw in text for kw in no_keywords):
            conv.current_state = "CANCELLED"
            bot_reply = (
                f"🛑 We understand! Your order *#{conv.order_id}* has been cancelled as requested. "
                f"No package will be dispatched. If you change your mind, we're always here!"
            )
            if order:
                order.final_status = "CANCELLED"
        else:
            # Ambiguous input - ask clarification
            bot_reply = (
                f"We didn't quite catch that. Please reply with:\n"
                f"• *YES* to confirm delivery of order #{conv.order_id}\n"
                f"• *NO* to cancel order #{conv.order_id}"
            )

        messages.append({
            "sender": "BOT",
            "text": bot_reply,
            "timestamp": now.isoformat(),
            "message_type": "text"
        })

    def _handle_prepaid_reply(
        self,
        conv: WhatsAppConversation,
        order: Optional[Order],
        text: str,
        messages: List[Dict[str, Any]],
        now: datetime
    ):
        pay_keywords = ["pay", "upi", "discount", "link", "online", "convert", "card", "gpay", "yes"]
        keep_keywords = ["keep", "cod", "no", "cash", "nahi", "standard"]
        paid_confirm_keywords = ["paid", "done", "success", "completed"]

        if any(kw in text for kw in pay_keywords):
            conv.current_state = "AWAITING_PAYMENT"
            order_val = order.order_value if order else 649.0
            discounted = order_val - conv.discount_offered
            payment_token = f"sim_{uuid.uuid4().hex[:8]}"
            payment_link = f"https://pay.smartcod.ai/checkout/{conv.order_id}?t={payment_token}"
            
            bot_reply = (
                f"🎉 Awesome! Here is your secure one-click checkout link with *₹{conv.discount_offered:.0f} discount applied*:\n\n"
                f"👉 {payment_link}\n\n"
                f"Amount to pay: *₹{discounted:.0f}* (via UPI / GPay / Card).\n"
                f"_(Click the link or click 'Simulate Successful Payment' below to complete)._"
            )
            messages.append({
                "sender": "BOT",
                "text": bot_reply,
                "timestamp": now.isoformat(),
                "message_type": "interactive_link"
            })
        elif any(kw in text for kw in paid_confirm_keywords) and conv.current_state == "AWAITING_PAYMENT":
            self.simulate_payment_success(conv.conversation_id)
        elif any(kw in text for kw in keep_keywords):
            conv.current_state = "OFFER_DECLINED"
            bot_reply = (
                f"Got it! We'll keep order *#{conv.order_id}* on Cash on Delivery for ₹{order.order_value if order else 649:.0f}. "
                f"Please ensure exact cash is available at the time of delivery."
            )
            messages.append({
                "sender": "BOT",
                "text": bot_reply,
                "timestamp": now.isoformat(),
                "message_type": "text"
            })
        else:
            bot_reply = (
                f"Please let us know how you'd like to proceed with order #{conv.order_id}:\n"
                f"• Reply *PAY* to get the ₹{conv.discount_offered:.0f} prepaid discount link\n"
                f"• Reply *KEEP* to stay on Cash on Delivery"
            )
            messages.append({
                "sender": "BOT",
                "text": bot_reply,
                "timestamp": now.isoformat(),
                "message_type": "text"
            })

    def simulate_payment_success(self, conversation_id: str) -> WhatsAppConversation:
        """
        Simulates customer completing UPI / online payment.
        Converts order to Prepaid, changes status, and adds confirmation message.
        """
        conv = (
            self.db.query(WhatsAppConversation)
            .filter(WhatsAppConversation.conversation_id == conversation_id)
            .first()
        )
        if not conv:
            raise ValueError(f"Conversation '{conversation_id}' not found.")

        order = self.db.query(Order).filter(Order.order_id == conv.order_id).first()
        messages: List[Dict[str, Any]] = json.loads(conv.messages or "[]")
        now = conv.simulated_current_time or utc_now()

        conv.current_state = "CONVERTED_PREPAID"
        if order:
            order.payment_method = "PREPAID"
            order.final_status = "CONFIRMED"

        bot_reply = (
            f"🎉 Payment Confirmed! We received ₹{(order.order_value - conv.discount_offered) if order else 599:.0f} via UPI.\n\n"
            f"Order *#{conv.order_id}* is upgraded to *PREPAID* with *Priority Courier Dispatch*! 📦✨\n"
            f"RTO Risk eliminated. Thank you for shopping with us!"
        )
        messages.append({
            "sender": "BOT",
            "text": bot_reply,
            "timestamp": now.isoformat(),
            "message_type": "text"
        })

        conv.messages = json.dumps(messages)
        conv.updated_at = now
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def advance_time(self, conversation_id: str, hours: int = 1) -> WhatsAppConversation:
        """
        Advances the simulated clock for this conversation.
        If advanced past expires_at (24h) and still PENDING_REPLY, triggers TIMEOUT state.
        """
        conv = (
            self.db.query(WhatsAppConversation)
            .filter(WhatsAppConversation.conversation_id == conversation_id)
            .first()
        )
        if not conv:
            raise ValueError(f"Conversation '{conversation_id}' not found.")

        current = conv.simulated_current_time or utc_now()
        new_time = current + timedelta(hours=hours)
        conv.simulated_current_time = new_time

        messages: List[Dict[str, Any]] = json.loads(conv.messages or "[]")

        # Check for timeout transition
        if conv.expires_at and new_time >= conv.expires_at and conv.current_state in ["PENDING_REPLY", "AWAITING_PAYMENT"]:
            conv.current_state = "TIMEOUT"
            order = self.db.query(Order).filter(Order.order_id == conv.order_id).first()
            if order and order.final_status in ["PENDING", ""]:
                order.final_status = "ON_HOLD"

            timeout_msg = (
                f"⏰ [SIMULATED TIMEOUT - {hours}h elapsed]\n"
                f"Confirmation window of 24 hours expired without response. Order *#{conv.order_id}* has been placed ON HOLD to protect against RTO loss."
            )
            messages.append({
                "sender": "SYSTEM",
                "text": timeout_msg,
                "timestamp": new_time.isoformat(),
                "message_type": "text"
            })

        conv.messages = json.dumps(messages)
        self.db.commit()
        self.db.refresh(conv)
        return conv
