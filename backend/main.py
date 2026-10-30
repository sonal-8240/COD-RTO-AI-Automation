import os
import json
import pandas as pd
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

from backend.config import settings
from backend.database import engine, Base, SessionLocal
from backend.models import Order, DecisionRecord, SystemSettings
from backend.services.risk_engine import RiskEngine
from backend.routes.orders import router as orders_router
from backend.routes.dashboard import router as dashboard_router
from backend.routes.settings import router as settings_router
from backend.routes.whatsapp import router as whatsapp_router
from backend.routes.analysis import router as analysis_router

def seed_database_if_empty():
    db = SessionLocal()
    try:
        # 1. Initialize default settings if missing
        s = db.query(SystemSettings).filter(SystemSettings.id == 1).first()
        if not s:
            s = SystemSettings(
                id=1,
                threshold_low_risk=settings.THRESHOLD_LOW_RISK,
                threshold_medium_risk=settings.THRESHOLD_MEDIUM_RISK,
                threshold_high_risk=settings.THRESHOLD_HIGH_RISK,
                threshold_cancel_risk=settings.THRESHOLD_CANCEL_RISK,
                min_pincode_sample_size=settings.MIN_PINCODE_SAMPLE_SIZE,
                prepaid_discount_percent=settings.PREPAID_DISCOUNT_PERCENT,
                confirmation_timeout_hours=settings.CONFIRMATION_TIMEOUT_HOURS,
                default_aov=settings.DEFAULT_AOV,
                gross_margin_pct=settings.GROSS_MARGIN_PCT,
                forward_shipping_cost=settings.FORWARD_SHIPPING_COST,
                return_shipping_cost=settings.RETURN_SHIPPING_COST,
                packaging_handling_cost=settings.PACKAGING_HANDLING_COST,
                damage_probability=settings.DAMAGE_PROBABILITY,
                product_cost=settings.PRODUCT_COST,
                direct_rto_loss=settings.DIRECT_RTO_LOSS,
                cac=settings.CUSTOMER_ACQUISITION_COST,
                updated_at=utc_now()
            )
            db.add(s)
            db.commit()

        # 2. Check if orders already populated
        order_count = db.query(Order).count()
        if order_count > 0:
            print(f"Database already populated with {order_count} orders.")
            return

        cleaned_csv = "data/cleaned_orders.csv"
        if not os.path.exists(cleaned_csv):
            print(f"File {cleaned_csv} not found for initial seeding.")
            return

        print(f"Seeding database from {cleaned_csv}...")
        df = pd.read_csv(cleaned_csv)
        risk_engine = RiskEngine(cleaned_csv)

        orders_to_add = []
        decisions_to_add = []

        thresholds = {
            "threshold_low_risk": s.threshold_low_risk,
            "threshold_medium_risk": s.threshold_medium_risk,
            "threshold_high_risk": s.threshold_high_risk,
            "threshold_cancel_risk": s.threshold_cancel_risk,
            "min_pincode_sample_size": s.min_pincode_sample_size
        }

        for _, row in df.iterrows():
            o_id = str(row['order_id'])
            
            # Parse datetime
            dt = utc_now()
            if pd.notna(row.get('order_datetime')):
                try:
                    dt = pd.to_datetime(row['order_datetime']).to_pydatetime()
                except Exception:
                    pass

            pincode_str = str(row.get('pincode_clean', row.get('pincode', ''))).replace('.0', '').strip()
            phone_str = str(row.get('phone', '')).replace('.0', '').strip()

            order_obj = Order(
                order_id=o_id,
                order_datetime=dt,
                customer_name=str(row.get('customer_name', 'Valued Customer')),
                phone=phone_str,
                address=str(row.get('address', '')),
                city=str(row.get('city', 'Unknown')),
                state=str(row.get('state', 'Unknown')),
                pincode=pincode_str,
                order_value=float(row.get('order_value', 649.0)),
                items=str(row.get('items', 'Haircare Product')),
                num_items=int(row.get('num_items', 1)),
                customer_prior_orders=int(row.get('customer_prior_orders', 0)),
                customer_prior_rto=int(row.get('customer_prior_rto', 0)),
                utm_source=str(row.get('utm_source', 'direct')),
                courier=str(row.get('courier', 'Delhivery')),
                payment_method=str(row.get('payment_method', 'COD')),
                final_status=str(row.get('final_status', 'DELIVERED')).upper()
            )
            orders_to_add.append(order_obj)

            # Evaluate order
            order_dict = {
                "order_id": o_id,
                "customer_name": order_obj.customer_name,
                "address": order_obj.address,
                "city": order_obj.city,
                "state": order_obj.state,
                "pincode": order_obj.pincode,
                "order_value": order_obj.order_value,
                "customer_prior_orders": order_obj.customer_prior_orders,
                "customer_prior_rto": order_obj.customer_prior_rto,
                "utm_source": order_obj.utm_source,
                "courier": order_obj.courier
            }
            dec = risk_engine.evaluate_order(order_dict, thresholds=thresholds)

            dec_obj = DecisionRecord(
                order_id=o_id,
                risk_score=dec["risk_score"],
                risk_level=dec["risk_level"],
                action=dec["action"],
                reason=dec["reason"],
                risk_factors=json.dumps(dec["risk_factors"]),
                expected_financial_impact=json.dumps(dec["expected_financial_impact"]),
                next_step=dec["next_step"],
                explanation_source=dec["explanation_source"],
                evaluated_at=dt
            )
            decisions_to_add.append(dec_obj)

        db.bulk_save_objects(orders_to_add)
        db.commit()

        db.bulk_save_objects(decisions_to_add)
        db.commit()

        print(f"Successfully seeded and evaluated {len(orders_to_add)} orders.")
    except Exception as e:
        db.rollback()
        print(f"Seeding error: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    seed_database_if_empty()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent COD Risk & RTO Prevention System for D2C Brands",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(orders_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(settings_router, prefix=settings.API_PREFIX)
app.include_router(whatsapp_router, prefix=settings.API_PREFIX)
app.include_router(analysis_router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs",
        "api_prefix": settings.API_PREFIX
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
