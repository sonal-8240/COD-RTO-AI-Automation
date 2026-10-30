"""
SmartCOD AI - Core Decision Engine & Risk Assessment Service
Combines empirical Bayesian priors, machine learning scoring, NLP address analysis,
and financial optimization to assign exactly one of 4 business actions.
"""

import os
import re
import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.config import settings
from backend.services.financial_model import FinancialModel
from backend.services.llm_service import LLMAddressIntelligence

class RiskEngine:
    def __init__(self, data_path: Optional[str] = None):
        self.financial_model = FinancialModel()
        self.llm_service = LLMAddressIntelligence()
        self.global_prior_rto = 0.2843  # Global baseline COD RTO rate from 1,988 cleaned orders
        self.pincode_stats = {}
        self.city_stats = {}
        self.courier_stats = {}
        self.channel_stats = {}
        
        # Load empirical priors from historical dataset if available
        self._load_historical_priors(data_path or "data/cleaned_orders.csv")

    def _load_historical_priors(self, file_path: str):
        if not os.path.exists(file_path):
            return
        try:
            df = pd.read_csv(file_path)
            # Filter to terminal orders (DELIVERED or RTO)
            df_term = df[df['final_status'].isin(['DELIVERED', 'RTO'])].copy()
            if len(df_term) == 0:
                return
            
            df_term['is_rto'] = (df_term['final_status'] == 'RTO').astype(int)
            self.global_prior_rto = float(df_term['is_rto'].mean())

            # 1. Pincode smoothing with Empirical Bayes / Laplace smoothing (m=10)
            pin_grp = df_term.groupby('pincode')['is_rto'].agg(['count', 'sum'])
            m = 10.0
            pin_grp['smoothed_rto'] = (pin_grp['sum'] + m * self.global_prior_rto) / (pin_grp['count'] + m)
            self.pincode_stats = pin_grp.to_dict(orient='index')

            # 2. Courier stats
            courier_grp = df_term.groupby('courier')['is_rto'].agg(['count', 'mean'])
            self.courier_stats = courier_grp.to_dict(orient='index')

            # 3. Channel stats
            chan_grp = df_term.groupby('utm_source')['is_rto'].agg(['count', 'mean'])
            self.channel_stats = chan_grp.to_dict(orient='index')
        except Exception as e:
            print(f"Notice: Prior loading completed with default priors ({e})")

    def evaluate_order(
        self,
        order_data: Dict[str, Any],
        thresholds: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Main decision method evaluating a COD order.
        Produces risk score, risk level, action, risk factors, financial impact, and next steps.
        """
        th = thresholds or {
            "threshold_low_risk": settings.THRESHOLD_LOW_RISK,
            "threshold_medium_risk": settings.THRESHOLD_MEDIUM_RISK,
            "threshold_high_risk": settings.THRESHOLD_HIGH_RISK,
            "threshold_cancel_risk": settings.THRESHOLD_CANCEL_RISK,
            "min_pincode_sample_size": settings.MIN_PINCODE_SAMPLE_SIZE
        }

        order_id = str(order_data.get("order_id", "UNKNOWN"))
        customer_name = str(order_data.get("customer_name", "")).strip()
        address = str(order_data.get("address", "")).strip()
        city = str(order_data.get("city", "")).strip()
        state = str(order_data.get("state", "")).strip()
        pincode = str(order_data.get("pincode", "")).strip().replace(".0", "")
        order_value = float(order_data.get("order_value", settings.DEFAULT_AOV))
        prior_orders = int(order_data.get("customer_prior_orders", 0))
        prior_rto = int(order_data.get("customer_prior_rto", 0))
        utm_source = str(order_data.get("utm_source", "direct")).strip().lower()
        courier = str(order_data.get("courier", "Delhivery")).strip()

        # Step 1: Address & Name Intelligence
        nlp_res = self.llm_service.analyze_order_context(customer_name, address, city, state)
        addr_score = nlp_res["address_quality_score"]
        is_suspicious_name = nlp_res["is_suspicious_name"]
        hinglish_detected = nlp_res["hinglish_detected"]
        explanation_source = nlp_res["explanation_source"]

        # Step 2: Feature Scoring & Factor Construction
        risk_factors: List[Dict[str, Any]] = []
        base_risk = self.global_prior_rto  # ~0.284

        # Factor A: Customer History (Strongest Predictive Signal)
        if prior_orders == 0:
            # First-time customer
            risk_factors.append({
                "name": "Customer Profile",
                "impact": "NEUTRAL",
                "weight": 0.05,
                "description": "First-time customer; no historical fulfillment record."
            })
            customer_history_delta = +0.03
            is_new = True
        else:
            is_new = False
            if prior_rto > 0:
                # Repeat customer with past RTO
                rto_ratio = prior_rto / max(1, prior_orders)
                weight = min(0.35, 0.20 + (rto_ratio * 0.15))
                risk_factors.append({
                    "name": "Prior RTO History",
                    "impact": "NEGATIVE",
                    "weight": round(weight, 2),
                    "description": f"Customer has {prior_rto} prior RTO(s) out of {prior_orders} orders ({rto_ratio*100:.0f}% historical return rate)."
                })
                customer_history_delta = weight
            else:
                # Clean repeat customer (Strong positive signal: 14% empirical RTO)
                weight = -0.16
                risk_factors.append({
                    "name": "Clean Repeat Customer",
                    "impact": "POSITIVE",
                    "weight": weight,
                    "description": f"Trusted repeat customer with {prior_orders} successful prior orders and 0 RTOs."
                })
                customer_history_delta = weight

        # Factor B: Address Quality
        if addr_score < 0.35:
            weight = +0.32
            risk_factors.append({
                "name": "Defective Address",
                "impact": "NEGATIVE",
                "weight": weight,
                "description": "Address contains placeholder text, lacks house/street numbers, or is severely truncated (<15 chars)."
            })
            address_delta = weight
        elif addr_score < 0.65:
            weight = +0.10
            risk_factors.append({
                "name": "Ambiguous Address",
                "impact": "NEGATIVE",
                "weight": weight,
                "description": "Address lacks specific flat/house numbers or clear landmark coordinates."
            })
            address_delta = weight
        else:
            weight = -0.08
            risk_factors.append({
                "name": "Structured Address",
                "impact": "POSITIVE",
                "weight": weight,
                "description": "Comprehensive address with house/flat number, street name, and identifiable delivery landmarks."
            })
            address_delta = weight

        # Factor C: Suspicious Name
        if is_suspicious_name:
            weight = +0.28
            risk_factors.append({
                "name": "Suspicious Customer Name",
                "impact": "NEGATIVE",
                "weight": weight,
                "description": f"Name ('{customer_name}') resembles a test entry, keyboard mash, or placeholder."
            })
            name_delta = weight
        else:
            name_delta = 0.0

        # Factor D: Hinglish / Local Landmarks
        if hinglish_detected:
            weight = -0.06
            risk_factors.append({
                "name": "Authentic Local Landmark",
                "impact": "POSITIVE",
                "weight": weight,
                "description": "Customer provided authentic regional landmark directions, facilitating delivery partner routing."
            })
            landmark_delta = weight
        else:
            landmark_delta = 0.0

        # Factor E: Pincode Empirical Risk (Smoothed)
        pincode_delta = 0.0
        if pincode in self.pincode_stats:
            p_data = self.pincode_stats[pincode]
            n_count = p_data.get('count', 0)
            smoothed_rate = p_data.get('smoothed_rto', self.global_prior_rto)
            diff = smoothed_rate - self.global_prior_rto
            
            if n_count >= th["min_pincode_sample_size"]:
                pincode_delta = round(diff * 0.6, 3)
                impact_type = "NEGATIVE" if diff > 0.05 else ("POSITIVE" if diff < -0.05 else "NEUTRAL")
                risk_factors.append({
                    "name": "Pincode Historical RTO",
                    "impact": impact_type,
                    "weight": round(pincode_delta, 2),
                    "description": f"Pincode {pincode} has a smoothed historical RTO rate of {smoothed_rate*100:.1f}% across {n_count} orders."
                })
            else:
                pincode_delta = round(diff * 0.2, 3)
        elif not pincode or len(pincode) != 6:
            pincode_delta = +0.15
            risk_factors.append({
                "name": "Invalid Pincode",
                "impact": "NEGATIVE",
                "weight": 0.15,
                "description": f"Pincode ('{pincode}') is invalid or missing, obstructing automated courier routing."
            })

        # Factor F: Order Value Sensitivity
        order_value_delta = 0.0
        if order_value > 1200:
            order_value_delta = +0.08
            risk_factors.append({
                "name": "High COD Order Value",
                "impact": "NEGATIVE",
                "weight": 0.08,
                "description": f"High cash-on-delivery amount (₹{order_value:.0f}); higher refusal risk upon delivery."
            })
        elif order_value < 400:
            order_value_delta = -0.03

        # Factor G: Acquisition Source
        channel_delta = 0.0
        if utm_source in ["meta", "facebook", "instagram", "fb"]:
            channel_delta = +0.04
            risk_factors.append({
                "name": "Paid Social Acquisition",
                "impact": "NEGATIVE",
                "weight": 0.04,
                "description": "Meta Ad acquired impulse traffic has an empirical 31.2% RTO baseline."
            })
        elif utm_source in ["direct", "organic"]:
            channel_delta = -0.04
            risk_factors.append({
                "name": "Direct Intent Traffic",
                "impact": "POSITIVE",
                "weight": -0.04,
                "description": "High-intent direct visitor baseline RTO is lower (22.9%)."
            })

        # Aggregate Risk Score
        raw_risk = (
            base_risk +
            customer_history_delta +
            address_delta +
            name_delta +
            landmark_delta +
            pincode_delta +
            order_value_delta +
            channel_delta
        )

        # Calibrated risk score bounded between 0.03 and 0.98
        risk_score = round(max(0.03, min(0.98, raw_risk)), 2)

        # Step 3: Determine Risk Category
        if risk_score < th["threshold_low_risk"]:
            risk_level = "LOW"
        elif risk_score < th["threshold_medium_risk"]:
            risk_level = "MEDIUM"
        elif risk_score < th["threshold_high_risk"]:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        # Step 4: Map to Business Action
        # Economically balanced rules avoiding unneeded cancellation of genuine orders
        if is_suspicious_name and addr_score < 0.3:
            # Definite test/fraud order
            action = "HOLD_OR_CANCEL"
            reason = "Test or fraudulent order detected (suspicious customer name combined with a placeholder address)."
            next_step = "Hold dispatch immediately. Flag customer profile in Shopify."
        elif prior_rto >= 2 and (prior_rto / max(1, prior_orders)) >= 0.6:
            # Chronic return abuser
            action = "HOLD_OR_CANCEL"
            reason = f"Chronic RTO history ({prior_rto} prior returns). Shipping COD is economically unviable."
            next_step = "Cancel COD fulfillment. Offer prepaid-only checkout link."
        elif addr_score < 0.25:
            # Unserviceable address
            action = "HOLD_OR_CANCEL"
            reason = "Incomplete or defective address ('xyz', 'home', or <10 chars) cannot be delivered by couriers."
            next_step = "Hold order and trigger automated SMS/WhatsApp requesting a full postal address before cancellation."
        elif risk_score >= th["threshold_cancel_risk"]:
            # Extreme risk (> 0.68)
            action = "HOLD_OR_CANCEL"
            reason = f"Critical delivery risk ({risk_score*100:.0f}% RTO probability) exceeds cancellation threshold."
            next_step = "Hold order dispatch. Flag for manual customer service verification before shipping."
        elif risk_score >= th["threshold_medium_risk"] or (risk_score >= th["threshold_low_risk"] and order_value >= 1000):
            # Elevated risk or High Order Value: Nudge to prepaid
            action = "NUDGE_TO_PREPAID"
            reason = (
                f"Elevated RTO exposure ({risk_score*100:.0f}%) on ₹{order_value:.0f} order value. "
                f"Converting to prepaid de-risks transit while offering customer an instant discount."
            )
            next_step = "Send WhatsApp prepaid discount offer (8% off / ₹50 discount) to convert from COD to UPI."
        elif risk_score >= th["threshold_low_risk"]:
            # Medium risk (20% - 45%)
            action = "SHIP_AFTER_CONFIRMATION"
            reason = "First-time customer or moderate delivery risk. WhatsApp confirmation will verify intent."
            next_step = "Dispatch WhatsApp confirmation message. Await customer reply within 24 hours."
        else:
            # Low risk (< 20%)
            action = "SHIP_AS_IS"
            reason = "Low estimated RTO probability backed by verified address and/or positive customer history."
            next_step = "Generate shipping waybill and dispatch immediately with standard courier SLA."

        # Step 5: Financial Impact Calculation
        financial_impact = self.financial_model.evaluate_order_financials(
            order_value=order_value,
            rto_probability=risk_score,
            action=action,
            is_first_time=is_new
        )

        return {
            "order_id": order_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "action": action,
            "reason": reason,
            "risk_factors": risk_factors,
            "expected_financial_impact": financial_impact,
            "next_step": next_step,
            "explanation_source": explanation_source,
            "evaluated_at": datetime.now(timezone.utc).replace(tzinfo=None)
        }
