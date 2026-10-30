import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartCOD AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = "sqlite:///./smartcod.db"
    
    # Financial Constants (from Assignment Specification)
    DEFAULT_AOV: float = 649.0
    GROSS_MARGIN_PCT: float = 0.62  # 62% delivered gross margin
    FORWARD_SHIPPING_COST: float = 65.0
    RETURN_SHIPPING_COST: float = 65.0
    PACKAGING_HANDLING_COST: float = 25.0
    DAMAGE_PROBABILITY: float = 0.08  # 8% damage risk on returned units
    PRODUCT_COST: float = 180.0
    DIRECT_RTO_LOSS: float = 169.40  # 65 + 65 + 25 + (0.08 * 180)
    CUSTOMER_ACQUISITION_COST: float = 300.0  # Meta CAC
    
    # Default Risk Thresholds (Configurable via Settings UI)
    THRESHOLD_LOW_RISK: float = 0.20        # <= 0.20: SHIP_AS_IS
    THRESHOLD_MEDIUM_RISK: float = 0.45     # 0.20 - 0.45: SHIP_AFTER_CONFIRMATION
    THRESHOLD_HIGH_RISK: float = 0.68       # 0.45 - 0.68: NUDGE_TO_PREPAID
    THRESHOLD_CANCEL_RISK: float = 0.68     # >= 0.68: HOLD_OR_CANCEL
    
    MIN_PINCODE_SAMPLE_SIZE: int = 5
    PREPAID_DISCOUNT_PERCENT: float = 8.0   # 8% or flat discount
    CONFIRMATION_TIMEOUT_HOURS: int = 24
    
    # AI / LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    USE_MOCK_LLM_IF_NO_KEY: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()
