from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import json

from backend.database import get_db
from backend.services.whatsapp_service import WhatsAppSimulatorService
from backend.schemas import WhatsAppActionRequest

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Simulator"])

@router.post("/start")
def start_whatsapp_flow(
    order_id: str = Body(..., embed=True),
    workflow_type: str = Body("CONFIRMATION", embed=True),
    discount_pct: float = Body(8.0, embed=True),
    db: Session = Depends(get_db)
):
    """
    Initializes a WhatsApp conversation simulation for a given order.
    """
    service = WhatsAppSimulatorService(db)
    try:
        conv = service.start_conversation(order_id, workflow_type, discount_pct)
        return {
            "conversation_id": conv.conversation_id,
            "order_id": conv.order_id,
            "workflow_type": conv.workflow_type,
            "current_state": conv.current_state,
            "messages": json.loads(conv.messages or "[]"),
            "discount_offered": conv.discount_offered,
            "simulated_current_time": conv.simulated_current_time,
            "expires_at": conv.expires_at
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{conversation_id}")
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """
    Retrieves current message stream and state for a conversation.
    """
    service = WhatsAppSimulatorService(db)
    conv = (
        service.db.query(service.db.models.WhatsAppConversation if hasattr(service.db, 'models') else None)
    )
    # direct query
    from backend.models import WhatsAppConversation
    conv = db.query(WhatsAppConversation).filter(WhatsAppConversation.conversation_id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail=f"Conversation '{conversation_id}' not found.")

    return {
        "conversation_id": conv.conversation_id,
        "order_id": conv.order_id,
        "workflow_type": conv.workflow_type,
        "current_state": conv.current_state,
        "messages": json.loads(conv.messages or "[]"),
        "discount_offered": conv.discount_offered,
        "simulated_current_time": conv.simulated_current_time,
        "expires_at": conv.expires_at
    }

@router.post("/{conversation_id}/reply")
def reply_to_conversation(
    conversation_id: str,
    text: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Submits a simulated customer reply to the conversation.
    """
    service = WhatsAppSimulatorService(db)
    try:
        conv = service.process_customer_reply(conversation_id, text)
        return {
            "conversation_id": conv.conversation_id,
            "current_state": conv.current_state,
            "messages": json.loads(conv.messages or "[]")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{conversation_id}/advance-time")
def advance_conversation_time(
    conversation_id: str,
    hours: int = Body(1, embed=True),
    db: Session = Depends(get_db)
):
    """
    Advances simulated clock to test 24-hour timeout and SLA actions.
    """
    service = WhatsAppSimulatorService(db)
    try:
        conv = service.advance_time(conversation_id, hours=hours)
        return {
            "conversation_id": conv.conversation_id,
            "current_state": conv.current_state,
            "simulated_current_time": conv.simulated_current_time,
            "messages": json.loads(conv.messages or "[]")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{conversation_id}/simulate-payment")
def simulate_prepaid_payment(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """
    Simulates payment link completion in Workflow B (Nudge to Prepaid).
    """
    service = WhatsAppSimulatorService(db)
    try:
        conv = service.simulate_payment_success(conversation_id)
        return {
            "conversation_id": conv.conversation_id,
            "current_state": conv.current_state,
            "messages": json.loads(conv.messages or "[]")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
