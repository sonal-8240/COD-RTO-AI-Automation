from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import json
from datetime import datetime, timezone

from backend.database import get_db
from backend.models import Order, DecisionRecord
from backend.schemas import (
    OrderCreate,
    OrderResponse,
    OrderDetailResponse,
    DecisionResponse,
    OrderBase
)
from backend.services.risk_engine import RiskEngine
from backend.routes.settings import get_or_create_settings

router = APIRouter(prefix="/orders", tags=["Orders"])
risk_engine = RiskEngine()

@router.post("/evaluate", response_model=DecisionResponse)
def evaluate_order_payload(
    order: OrderBase,
    db: Session = Depends(get_db)
):
    """
    Evaluates an arbitrary order payload in real-time.
    Uses dynamic thresholds from database settings.
    """
    settings = get_or_create_settings(db)
    thresholds = {
        "threshold_low_risk": settings.threshold_low_risk,
        "threshold_medium_risk": settings.threshold_medium_risk,
        "threshold_high_risk": settings.threshold_high_risk,
        "threshold_cancel_risk": settings.threshold_cancel_risk,
        "min_pincode_sample_size": settings.min_pincode_sample_size
    }

    result = risk_engine.evaluate_order(order.model_dump(), thresholds=thresholds)
    return result

@router.get("", response_model=Dict[str, Any])
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: Optional[str] = None,
    action: Optional[str] = None,
    risk_level: Optional[str] = None,
    final_status: Optional[str] = None,
    courier: Optional[str] = None,
    utm_source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lists orders with search, filters, and pagination.
    Masks customer phone and full address for privacy compliance.
    """
    query = db.query(Order).outerjoin(DecisionRecord, Order.order_id == DecisionRecord.order_id)

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            (Order.order_id.ilike(s)) |
            (Order.customer_name.ilike(s)) |
            (Order.pincode.ilike(s)) |
            (Order.city.ilike(s))
        )

    if action:
        query = query.filter(DecisionRecord.action == action)

    if risk_level:
        query = query.filter(DecisionRecord.risk_level == risk_level)

    if final_status:
        query = query.filter(Order.final_status == final_status)

    if courier:
        query = query.filter(Order.courier == courier)

    if utm_source:
        query = query.filter(Order.utm_source == utm_source)

    total = query.count()
    orders = (
        query.order_by(Order.order_datetime.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    results = []
    for o in orders:
        dec_dict = None
        if o.decision:
            dec_dict = {
                "order_id": o.decision.order_id,
                "risk_score": o.decision.risk_score,
                "risk_level": o.decision.risk_level,
                "action": o.decision.action,
                "reason": o.decision.reason,
                "risk_factors": json.loads(o.decision.risk_factors or "[]"),
                "expected_financial_impact": json.loads(o.decision.expected_financial_impact or "{}"),
                "next_step": o.decision.next_step,
                "explanation_source": o.decision.explanation_source,
                "evaluated_at": o.decision.evaluated_at
            }

        # Privacy masking for PII compliance
        masked_phone = o.phone
        if o.phone and len(str(o.phone)) >= 10:
            p_str = str(o.phone).replace(".0", "")
            masked_phone = f"{p_str[:2]}******{p_str[-2:]}"

        results.append({
            "order_id": o.order_id,
            "order_datetime": o.order_datetime,
            "customer_name": o.customer_name,
            "phone": masked_phone,
            "address": o.address,
            "city": o.city,
            "state": o.state,
            "pincode": o.pincode,
            "order_value": o.order_value,
            "items": o.items,
            "num_items": o.num_items,
            "customer_prior_orders": o.customer_prior_orders,
            "customer_prior_rto": o.customer_prior_rto,
            "utm_source": o.utm_source,
            "courier": o.courier,
            "payment_method": o.payment_method,
            "final_status": o.final_status,
            "decision": dec_dict
        })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
        "items": results
    }

@router.get("/{order_id}")
def get_order_by_id(order_id: str, db: Session = Depends(get_db)):
    """
    Fetches full detail for a single order including decision and WhatsApp status.
    """
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found.")

    dec_dict = None
    if order.decision:
        dec_dict = {
            "order_id": order.decision.order_id,
            "risk_score": order.decision.risk_score,
            "risk_level": order.decision.risk_level,
            "action": order.decision.action,
            "reason": order.decision.reason,
            "risk_factors": json.loads(order.decision.risk_factors or "[]"),
            "expected_financial_impact": json.loads(order.decision.expected_financial_impact or "{}"),
            "next_step": order.decision.next_step,
            "explanation_source": order.decision.explanation_source,
            "evaluated_at": order.decision.evaluated_at
        }

    # WhatsApp conversations
    conversations = []
    for c in order.whatsapp_conversations:
        conversations.append({
            "conversation_id": c.conversation_id,
            "workflow_type": c.workflow_type,
            "current_state": c.current_state,
            "messages": json.loads(c.messages or "[]"),
            "discount_offered": c.discount_offered,
            "simulated_current_time": c.simulated_current_time,
            "expires_at": c.expires_at
        })

    p_str = str(order.phone).replace(".0", "") if order.phone else ""
    masked_phone = f"{p_str[:2]}******{p_str[-2:]}" if len(p_str) >= 10 else p_str

    return {
        "order_id": order.order_id,
        "order_datetime": order.order_datetime,
        "customer_name": order.customer_name,
        "phone": masked_phone,
        "address": order.address,
        "city": order.city,
        "state": order.state,
        "pincode": order.pincode,
        "order_value": order.order_value,
        "items": order.items,
        "num_items": order.num_items,
        "customer_prior_orders": order.customer_prior_orders,
        "customer_prior_rto": order.customer_prior_rto,
        "utm_source": order.utm_source,
        "courier": order.courier,
        "payment_method": order.payment_method,
        "final_status": order.final_status,
        "decision": dec_dict,
        "whatsapp_conversations": conversations
    }

@router.post("", response_model=Dict[str, Any])
def create_and_evaluate_order(payload: OrderCreate, db: Session = Depends(get_db)):
    """
    Submits a new live COD order, saves it, and evaluates it.
    """
    existing = db.query(Order).filter(Order.order_id == payload.order_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Order '{payload.order_id}' already exists.")

    new_order = Order(
        order_id=payload.order_id,
        order_datetime=payload.order_datetime or datetime.now(timezone.utc).replace(tzinfo=None),
        customer_name=payload.customer_name,
        phone=payload.phone,
        address=payload.address,
        city=payload.city,
        state=payload.state,
        pincode=payload.pincode,
        order_value=payload.order_value,
        items=payload.items,
        num_items=payload.num_items,
        customer_prior_orders=payload.customer_prior_orders,
        customer_prior_rto=payload.customer_prior_rto,
        utm_source=payload.utm_source,
        courier=payload.courier,
        payment_method=payload.payment_method or "COD",
        final_status="PENDING"
    )
    db.add(new_order)
    db.commit()

    # Evaluate
    settings = get_or_create_settings(db)
    thresholds = {
        "threshold_low_risk": settings.threshold_low_risk,
        "threshold_medium_risk": settings.threshold_medium_risk,
        "threshold_high_risk": settings.threshold_high_risk,
        "threshold_cancel_risk": settings.threshold_cancel_risk,
        "min_pincode_sample_size": settings.min_pincode_sample_size
    }
    decision = risk_engine.evaluate_order(payload.model_dump(), thresholds=thresholds)

    dec_rec = DecisionRecord(
        order_id=new_order.order_id,
        risk_score=decision["risk_score"],
        risk_level=decision["risk_level"],
        action=decision["action"],
        reason=decision["reason"],
        risk_factors=json.dumps(decision["risk_factors"]),
        expected_financial_impact=json.dumps(decision["expected_financial_impact"]),
        next_step=decision["next_step"],
        explanation_source=decision["explanation_source"],
        evaluated_at=decision["evaluated_at"]
    )
    db.add(dec_rec)
    db.commit()

    return {
        "order": payload.model_dump(),
        "decision": decision
    }
