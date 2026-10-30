from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class RiskFactorDetail(BaseModel):
    name: str
    impact: str  # POSITIVE, NEGATIVE, NEUTRAL
    weight: float
    description: str

class ExpectedFinancialImpact(BaseModel):
    expected_delivered_margin: float
    expected_rto_loss: float
    net_expected_value: float
    prevented_rto_savings: float
    cac_risk_exposure: float
    recommendation_rationale: str

class OrderBase(BaseModel):
    order_id: str
    customer_name: str
    phone: Optional[str] = None
    address: str
    city: Optional[str] = "Unknown"
    state: Optional[str] = "Unknown"
    pincode: Optional[str] = None
    order_value: float = 649.0
    items: Optional[str] = "Hair Serum 50ml"
    num_items: int = 1
    customer_prior_orders: int = 0
    customer_prior_rto: int = 0
    utm_source: Optional[str] = "direct"
    courier: Optional[str] = "Delhivery"
    payment_method: Optional[str] = "COD"

class OrderCreate(OrderBase):
    order_datetime: Optional[datetime] = None

class OrderResponse(OrderBase):
    order_datetime: datetime
    final_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DecisionResponse(BaseModel):
    order_id: str
    risk_score: float
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    action: str      # SHIP_AS_IS, SHIP_AFTER_CONFIRMATION, NUDGE_TO_PREPAID, HOLD_OR_CANCEL
    reason: str
    risk_factors: List[RiskFactorDetail]
    expected_financial_impact: ExpectedFinancialImpact
    next_step: str
    explanation_source: str  # LLM or DETERMINISTIC_RULES
    evaluated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class OrderDetailResponse(OrderResponse):
    decision: Optional[DecisionResponse] = None

class SystemSettingsSchema(BaseModel):
    threshold_low_risk: float = Field(0.20, ge=0.0, le=1.0)
    threshold_medium_risk: float = Field(0.45, ge=0.0, le=1.0)
    threshold_high_risk: float = Field(0.68, ge=0.0, le=1.0)
    threshold_cancel_risk: float = Field(0.68, ge=0.0, le=1.0)
    min_pincode_sample_size: int = Field(5, ge=1, le=100)
    prepaid_discount_percent: float = Field(8.0, ge=0.0, le=30.0)
    confirmation_timeout_hours: int = Field(24, ge=1, le=72)
    
    default_aov: float = 649.0
    gross_margin_pct: float = 0.62
    forward_shipping_cost: float = 65.0
    return_shipping_cost: float = 65.0
    packaging_handling_cost: float = 25.0
    damage_probability: float = 0.08
    product_cost: float = 180.0
    direct_rto_loss: float = 169.40
    cac: float = 300.0

    model_config = ConfigDict(from_attributes=True)

class WhatsAppMessageItem(BaseModel):
    sender: str  # "SYSTEM", "CUSTOMER", "BOT"
    text: str
    timestamp: datetime
    message_type: str = "text"  # "text", "button", "interactive_link"

class WhatsAppConversationResponse(BaseModel):
    conversation_id: str
    order_id: str
    workflow_type: str
    current_state: str
    messages: List[Dict[str, Any]]
    discount_offered: float
    simulated_current_time: datetime
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class WhatsAppActionRequest(BaseModel):
    action: str  # "REPLY", "ADVANCE_TIME", "PAY_ONLINE", "RESET"
    text: Optional[str] = None
    advance_hours: Optional[int] = None

class DashboardSummaryResponse(BaseModel):
    total_orders: int
    total_revenue: float
    delivered_orders: int
    rto_orders: int
    in_transit_orders: int
    overall_rto_rate: float
    
    # Decisions breakdown
    decisions_count: Dict[str, int]
    risk_levels_count: Dict[str, int]
    
    # Financial metrics
    baseline_direct_rto_loss: float
    prevented_rto_savings: float
    lost_genuine_order_margin: float
    net_economic_benefit: float
    delivered_gross_profit: float
    roi_multiple: float
    
    # Category splits
    courier_stats: List[Dict[str, Any]]
    channel_stats: List[Dict[str, Any]]
    address_tier_stats: List[Dict[str, Any]]
