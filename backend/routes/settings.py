from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

from backend.database import get_db
from backend.models import SystemSettings
from backend.schemas import SystemSettingsSchema
from backend.config import settings as app_config

router = APIRouter(prefix="/settings", tags=["Settings"])

def get_or_create_settings(db: Session) -> SystemSettings:
    s = db.query(SystemSettings).filter(SystemSettings.id == 1).first()
    if not s:
        s = SystemSettings(
            id=1,
            threshold_low_risk=app_config.THRESHOLD_LOW_RISK,
            threshold_medium_risk=app_config.THRESHOLD_MEDIUM_RISK,
            threshold_high_risk=app_config.THRESHOLD_HIGH_RISK,
            threshold_cancel_risk=app_config.THRESHOLD_CANCEL_RISK,
            min_pincode_sample_size=app_config.MIN_PINCODE_SAMPLE_SIZE,
            prepaid_discount_percent=app_config.PREPAID_DISCOUNT_PERCENT,
            confirmation_timeout_hours=app_config.CONFIRMATION_TIMEOUT_HOURS,
            default_aov=app_config.DEFAULT_AOV,
            gross_margin_pct=app_config.GROSS_MARGIN_PCT,
            forward_shipping_cost=app_config.FORWARD_SHIPPING_COST,
            return_shipping_cost=app_config.RETURN_SHIPPING_COST,
            packaging_handling_cost=app_config.PACKAGING_HANDLING_COST,
            damage_probability=app_config.DAMAGE_PROBABILITY,
            product_cost=app_config.PRODUCT_COST,
            direct_rto_loss=app_config.DIRECT_RTO_LOSS,
            cac=app_config.CUSTOMER_ACQUISITION_COST,
            updated_at=utc_now()
        )
        db.add(s)
        db.commit()
        db.refresh(s)
    return s

@router.get("", response_model=SystemSettingsSchema)
def get_settings(db: Session = Depends(get_db)):
    return get_or_create_settings(db)

@router.put("", response_model=SystemSettingsSchema)
def update_settings(payload: SystemSettingsSchema, db: Session = Depends(get_db)):
    # Validate threshold relationships
    if payload.threshold_low_risk > payload.threshold_medium_risk:
        raise HTTPException(
            status_code=400,
            detail="Low risk threshold cannot be higher than medium risk threshold."
        )
    if payload.threshold_medium_risk > payload.threshold_high_risk:
        raise HTTPException(
            status_code=400,
            detail="Medium risk threshold cannot be higher than high risk threshold."
        )

    s = get_or_create_settings(db)
    s.threshold_low_risk = payload.threshold_low_risk
    s.threshold_medium_risk = payload.threshold_medium_risk
    s.threshold_high_risk = payload.threshold_high_risk
    s.threshold_cancel_risk = payload.threshold_cancel_risk
    s.min_pincode_sample_size = payload.min_pincode_sample_size
    s.prepaid_discount_percent = payload.prepaid_discount_percent
    s.confirmation_timeout_hours = payload.confirmation_timeout_hours

    s.default_aov = payload.default_aov
    s.gross_margin_pct = payload.gross_margin_pct
    s.forward_shipping_cost = payload.forward_shipping_cost
    s.return_shipping_cost = payload.return_shipping_cost
    s.packaging_handling_cost = payload.packaging_handling_cost
    s.damage_probability = payload.damage_probability
    s.product_cost = payload.product_cost
    
    # Recalculate direct RTO loss
    s.direct_rto_loss = (
        payload.forward_shipping_cost +
        payload.return_shipping_cost +
        payload.packaging_handling_cost +
        (payload.damage_probability * payload.product_cost)
    )
    s.cac = payload.cac
    s.updated_at = utc_now()

    db.commit()
    db.refresh(s)
    return s
