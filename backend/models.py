from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database import Base

def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, index=True)
    order_datetime = Column(DateTime, default=utc_now, index=True)
    customer_name = Column(String, nullable=False)
    phone = Column(String, index=True)
    address = Column(Text, nullable=False)
    city = Column(String, index=True)
    state = Column(String)
    pincode = Column(String, index=True)
    order_value = Column(Float, nullable=False)
    items = Column(String)
    num_items = Column(Integer, default=1)
    customer_prior_orders = Column(Integer, default=0)
    customer_prior_rto = Column(Integer, default=0)
    utm_source = Column(String, index=True)
    courier = Column(String, index=True)
    payment_method = Column(String, default="COD")
    final_status = Column(String, default="PENDING", index=True)  # DELIVERED, RTO, IN_TRANSIT, PENDING, CONFIRMED, CANCELLED
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    decision = relationship("DecisionRecord", back_populates="order", uselist=False)
    whatsapp_conversations = relationship("WhatsAppConversation", back_populates="order")

class DecisionRecord(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, ForeignKey("orders.order_id"), unique=True, index=True)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    action = Column(String, nullable=False, index=True)  # SHIP_AS_IS, SHIP_AFTER_CONFIRMATION, NUDGE_TO_PREPAID, HOLD_OR_CANCEL
    reason = Column(Text, nullable=False)
    risk_factors = Column(Text, default="[]")  # JSON-serialized list of factor dicts
    expected_financial_impact = Column(Text, default="{}")  # JSON-serialized dict
    next_step = Column(Text, nullable=False)
    explanation_source = Column(String, default="DETERMINISTIC_RULES")  # LLM or DETERMINISTIC_RULES
    evaluated_at = Column(DateTime, default=utc_now, index=True)

    order = relationship("Order", back_populates="decision")

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, default=1)
    threshold_low_risk = Column(Float, default=0.20)
    threshold_medium_risk = Column(Float, default=0.45)
    threshold_high_risk = Column(Float, default=0.68)
    threshold_cancel_risk = Column(Float, default=0.68)
    min_pincode_sample_size = Column(Integer, default=5)
    prepaid_discount_percent = Column(Float, default=8.0)
    confirmation_timeout_hours = Column(Integer, default=24)
    
    # Financial parameters
    default_aov = Column(Float, default=649.0)
    gross_margin_pct = Column(Float, default=0.62)
    forward_shipping_cost = Column(Float, default=65.0)
    return_shipping_cost = Column(Float, default=65.0)
    packaging_handling_cost = Column(Float, default=25.0)
    damage_probability = Column(Float, default=0.08)
    product_cost = Column(Float, default=180.0)
    direct_rto_loss = Column(Float, default=169.40)
    cac = Column(Float, default=300.0)
    
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class WhatsAppConversation(Base):
    __tablename__ = "whatsapp_conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String, unique=True, index=True)
    order_id = Column(String, ForeignKey("orders.order_id"), index=True)
    workflow_type = Column(String, nullable=False)  # CONFIRMATION, PREPAID_NUDGE
    current_state = Column(String, default="PENDING_REPLY", index=True)  # PENDING_REPLY, CONFIRMED, CANCELLED, TIMEOUT, CONVERTED_PREPAID, OFFER_DECLINED
    messages = Column(Text, default="[]")  # JSON list of message objects
    discount_offered = Column(Float, default=0.0)
    simulated_current_time = Column(DateTime, default=utc_now)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    order = relationship("Order", back_populates="whatsapp_conversations")
