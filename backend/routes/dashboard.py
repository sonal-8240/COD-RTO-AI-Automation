from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
import json
import pandas as pd

from backend.database import get_db
from backend.models import Order, DecisionRecord, SystemSettings
from backend.routes.settings import get_or_create_settings
from backend.services.financial_model import FinancialModel

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
def get_dashboard_summary(
    date_filter: str = Query("all", description="all, yesterday, last_7_days, last_30_days"),
    db: Session = Depends(get_db)
):
    """
    Computes comprehensive founder-level KPIs, 4 decision bucket distributions,
    and financial savings vs false-positive loss trade-offs.
    """
    settings = get_or_create_settings(db)
    fin_model = FinancialModel(
        aov=settings.default_aov,
        gross_margin_pct=settings.gross_margin_pct,
        forward_shipping=settings.forward_shipping_cost,
        return_shipping=settings.return_shipping_cost,
        packaging_handling=settings.packaging_handling_cost,
        damage_prob=settings.damage_probability,
        product_cost=settings.product_cost,
        cac=settings.cac
    )

    query = db.query(Order).outerjoin(DecisionRecord, Order.order_id == DecisionRecord.order_id)

    # Date filtering
    # Check max date in DB to support historical dataset dates realistically
    latest_order = db.query(Order).order_by(Order.order_datetime.desc()).first()
    anchor_date = latest_order.order_datetime if latest_order and latest_order.order_datetime else datetime.now(timezone.utc).replace(tzinfo=None)

    if date_filter == "yesterday":
        # Day prior to anchor date
        start_date = (anchor_date - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        query = query.filter(Order.order_datetime >= start_date, Order.order_datetime < end_date)
    elif date_filter == "last_7_days":
        start_date = anchor_date - timedelta(days=7)
        query = query.filter(Order.order_datetime >= start_date)
    elif date_filter == "last_30_days":
        start_date = anchor_date - timedelta(days=30)
        query = query.filter(Order.order_datetime >= start_date)

    orders = query.all()
    total_orders = len(orders)

    if total_orders == 0:
        return {
            "total_orders": 0,
            "delivered_orders": 0,
            "rto_orders": 0,
            "in_transit_orders": 0,
            "rto_rate": 0.0,
            "total_revenue": 0.0,
            "decisions_count": {
                "SHIP_AS_IS": 0,
                "SHIP_AFTER_CONFIRMATION": 0,
                "NUDGE_TO_PREPAID": 0,
                "HOLD_OR_CANCEL": 0
            },
            "financials": {
                "baseline_rto_losses": 0.0,
                "prevented_rto_savings": 0.0,
                "lost_genuine_order_margin": 0.0,
                "net_economic_benefit": 0.0,
                "gross_profit_delivered": 0.0
            },
            "courier_breakdown": [],
            "channel_breakdown": [],
            "daily_trends": []
        }

    delivered_count = sum(1 for o in orders if o.final_status == "DELIVERED")
    rto_count = sum(1 for o in orders if o.final_status == "RTO")
    in_transit_count = sum(1 for o in orders if o.final_status in ["IN_TRANSIT", "PENDING", "CONFIRMED", "ON_HOLD"])
    total_revenue = sum(o.order_value for o in orders)

    rto_rate = round((rto_count / (delivered_count + rto_count)) * 100, 2) if (delivered_count + rto_count) > 0 else 0.0

    # Decision Buckets
    dec_counts = {
        "SHIP_AS_IS": 0,
        "SHIP_AFTER_CONFIRMATION": 0,
        "NUDGE_TO_PREPAID": 0,
        "HOLD_OR_CANCEL": 0
    }
    risk_level_counts = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0
    }

    prevented_rto_savings = 0.0
    lost_genuine_margin = 0.0
    direct_rto_loss_unit = fin_model.direct_rto_loss  # ₹169.40
    gross_profit_unit = fin_model.delivered_gross_profit  # ₹402.38

    for o in orders:
        if o.decision:
            act = o.decision.action
            dec_counts[act] = dec_counts.get(act, 0) + 1
            risk_level_counts[o.decision.risk_level] = risk_level_counts.get(o.decision.risk_level, 0) + 1

            # Financial estimation based on assignment math
            if act == "HOLD_OR_CANCEL":
                # If ground truth was RTO, this was a successful catch saving ₹169.40
                if o.final_status == "RTO":
                    prevented_rto_savings += direct_rto_loss_unit
                elif o.final_status == "DELIVERED":
                    # Mistakenly held/cancelled genuine order: Lost margin + Sunk CAC
                    lost_genuine_margin += (gross_profit_unit + (settings.cac if o.customer_prior_orders == 0 else 0.0))
            elif act == "SHIP_AFTER_CONFIRMATION":
                # Empirical confirmation prevents ~60% of potential RTO cancellations
                if o.final_status == "RTO":
                    prevented_rto_savings += (direct_rto_loss_unit * 0.60)
            elif act == "NUDGE_TO_PREPAID":
                # Converting COD to Prepaid drops RTO rate from 28% to 4%
                if o.final_status == "RTO":
                    prevented_rto_savings += (direct_rto_loss_unit * 0.85)

    baseline_rto_losses = round(rto_count * direct_rto_loss_unit, 2)
    prevented_rto_savings = round(prevented_rto_savings, 2)
    lost_genuine_margin = round(lost_genuine_margin, 2)
    net_economic_benefit = round(prevented_rto_savings - lost_genuine_margin, 2)

    # Courier breakdown
    courier_dict = {}
    for o in orders:
        c = o.courier or "Unknown"
        if c not in courier_dict:
            courier_dict[c] = {"name": c, "total": 0, "delivered": 0, "rto": 0}
        courier_dict[c]["total"] += 1
        if o.final_status == "DELIVERED":
            courier_dict[c]["delivered"] += 1
        elif o.final_status == "RTO":
            courier_dict[c]["rto"] += 1

    courier_breakdown = []
    for c, stats in courier_dict.items():
        denom = stats["delivered"] + stats["rto"]
        rate = round((stats["rto"] / denom) * 100, 1) if denom > 0 else 0.0
        courier_breakdown.append({
            "courier": c,
            "total_orders": stats["total"],
            "rto_orders": stats["rto"],
            "delivered_orders": stats["delivered"],
            "rto_rate": rate
        })

    # Channel breakdown
    chan_dict = {}
    for o in orders:
        ch = o.utm_source or "direct"
        if ch not in chan_dict:
            chan_dict[ch] = {"channel": ch, "total": 0, "rto": 0}
        chan_dict[ch]["total"] += 1
        if o.final_status == "RTO":
            chan_dict[ch]["rto"] += 1

    channel_breakdown = []
    for ch, stats in chan_dict.items():
        rate = round((stats["rto"] / stats["total"]) * 100, 1) if stats["total"] > 0 else 0.0
        channel_breakdown.append({
            "channel": ch,
            "total_orders": stats["total"],
            "rto_orders": stats["rto"],
            "rto_rate": rate
        })

    # Daily trend grouping
    daily_dict = {}
    for o in orders:
        if o.order_datetime:
            d_str = o.order_datetime.strftime("%Y-%m-%d")
            if d_str not in daily_dict:
                daily_dict[d_str] = {"date": d_str, "total": 0, "delivered": 0, "rto": 0}
            daily_dict[d_str]["total"] += 1
            if o.final_status == "DELIVERED":
                daily_dict[d_str]["delivered"] += 1
            elif o.final_status == "RTO":
                daily_dict[d_str]["rto"] += 1

    daily_trends = sorted(daily_dict.values(), key=lambda x: x["date"])
    for dt in daily_trends:
        denom = dt["delivered"] + dt["rto"]
        dt["rto_rate"] = round((dt["rto"] / denom) * 100, 1) if denom > 0 else 0.0

    return {
        "anchor_date": anchor_date.strftime("%Y-%m-%d"),
        "date_filter": date_filter,
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "delivered_orders": delivered_count,
        "rto_orders": rto_count,
        "in_transit_orders": in_transit_count,
        "rto_rate": rto_rate,
        "decisions_count": dec_counts,
        "risk_levels_count": risk_level_counts,
        "financials": {
            "direct_rto_loss_unit": direct_rto_loss_unit,
            "gross_profit_delivered_unit": gross_profit_unit,
            "baseline_rto_losses": baseline_rto_losses,
            "prevented_rto_savings": prevented_rto_savings,
            "lost_genuine_order_margin": lost_genuine_margin,
            "net_economic_benefit": net_economic_benefit,
            "gross_profit_delivered": round(delivered_count * gross_profit_unit, 2)
        },
        "courier_breakdown": courier_breakdown,
        "channel_breakdown": channel_breakdown,
        "daily_trends": daily_trends
    }
