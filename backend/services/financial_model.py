"""
SmartCOD AI - Financial Modeling & Unit Economics Service
Calculates expected value, direct RTO loss, CAC impact, and optimal discount thresholds.
"""

from typing import Dict, Any

class FinancialModel:
    def __init__(
        self,
        aov: float = 649.0,
        gross_margin_pct: float = 0.62,
        forward_shipping: float = 65.0,
        return_shipping: float = 65.0,
        packaging_handling: float = 25.0,
        damage_prob: float = 0.08,
        product_cost: float = 180.0,
        cac: float = 300.0,
        prepaid_rto_rate: float = 0.04
    ):
        self.aov = aov
        self.gross_margin_pct = gross_margin_pct
        self.forward_shipping = forward_shipping
        self.return_shipping = return_shipping
        self.packaging_handling = packaging_handling
        self.damage_prob = damage_prob
        self.product_cost = product_cost
        self.cac = cac
        self.prepaid_rto_rate = prepaid_rto_rate

    @property
    def direct_rto_loss(self) -> float:
        """
        Direct cash loss when a COD order returns to origin:
        Forward shipping (₹65) + Return shipping (₹65) + Packaging/handling (₹25) +
        Expected damage loss (8% * ₹180 = ₹14.40) = ₹169.40
        """
        return (
            self.forward_shipping +
            self.return_shipping +
            self.packaging_handling +
            (self.damage_prob * self.product_cost)
        )

    @property
    def delivered_gross_profit(self) -> float:
        """
        Gross profit generated if an order delivers successfully:
        AOV * Gross Margin % (₹649 * 0.62 = ₹402.38)
        """
        return round(self.aov * self.gross_margin_pct, 2)

    def evaluate_order_financials(
        self,
        order_value: float,
        rto_probability: float,
        action: str,
        is_first_time: bool = True
    ) -> Dict[str, Any]:
        """
        Calculates granular financial trade-offs between shipping, confirming, nudging, or cancelling.
        """
        order_gross_profit = round(order_value * self.gross_margin_pct, 2)
        direct_rto_loss = self.direct_rto_loss
        p_rto = max(0.01, min(0.99, rto_probability))
        p_delivered = 1.0 - p_rto

        # Status Quo COD Expected Value:
        # E[V] = (P_delivered * Gross Profit) - (P_rto * Direct RTO Loss)
        ev_cod = (p_delivered * order_gross_profit) - (p_rto * direct_rto_loss)

        # Financial impact by action
        if action == "SHIP_AS_IS":
            expected_delivered = round(p_delivered * order_gross_profit, 2)
            expected_loss = round(p_rto * direct_rto_loss, 2)
            net_ev = round(ev_cod, 2)
            prevented_savings = 0.0
            cac_exposure = 0.0
            rationale = (
                f"Low RTO risk ({p_rto*100:.1f}%). Expected gross margin of ₹{expected_delivered:.2f} "
                f"far exceeds expected direct RTO loss of ₹{expected_loss:.2f}. Safe to ship immediately."
            )

        elif action == "SHIP_AFTER_CONFIRMATION":
            # Confirmation filters out ~40-60% of potential RTOs by identifying uncommitted buyers
            # Confirmed orders have an estimated 65% reduction in RTO probability
            confirmed_p_rto = p_rto * 0.35
            confirmed_p_del = 1.0 - confirmed_p_rto
            expected_delivered = round(confirmed_p_del * order_gross_profit, 2)
            expected_loss = round(confirmed_p_rto * direct_rto_loss, 2)
            net_ev = round((confirmed_p_del * order_gross_profit) - (confirmed_p_rto * direct_rto_loss), 2)
            prevented_savings = round((p_rto - confirmed_p_rto) * direct_rto_loss, 2)
            cac_exposure = 0.0  # Customer gets a chance to confirm, not arbitrarily cancelled
            rationale = (
                f"Moderate risk ({p_rto*100:.1f}%). WhatsApp confirmation prevents an estimated ₹{prevented_savings:.2f} "
                f"in wasted reverse logistics while preserving customer acquisition."
            )

        elif action == "NUDGE_TO_PREPAID":
            # If customer converts to prepaid, RTO drops from p_rto to ~4% (prepaid baseline)
            # Company offers an optimal 8% discount to incentivize prepayment
            discount_amount = round(order_value * 0.08, 2)
            post_discount_margin = order_gross_profit - discount_amount
            prepaid_loss = round(self.prepaid_rto_rate * direct_rto_loss, 2)
            expected_delivered = round((1.0 - self.prepaid_rto_rate) * post_discount_margin, 2)
            expected_loss = prepaid_loss
            net_ev = round(expected_delivered - expected_loss, 2)
            # RTO savings: difference between COD RTO loss and prepaid RTO loss
            prevented_savings = round((p_rto - self.prepaid_rto_rate) * direct_rto_loss, 2)
            cac_exposure = 0.0
            rationale = (
                f"Elevated risk ({p_rto*100:.1f}%). Converting to prepaid reduces RTO risk to {self.prepaid_rto_rate*100:.0f}%, "
                f"saving ₹{prevented_savings:.2f} in return expenses against a ₹{discount_amount:.2f} discount incentive."
            )

        elif action == "HOLD_OR_CANCEL":
            # Cancel: Direct RTO loss avoided = p_rto * direct_rto_loss
            # But if the customer was genuine (p_delivered), company loses gross profit + sunk CAC
            prevented_savings = round(p_rto * direct_rto_loss, 2)
            lost_potential_margin = round(p_delivered * order_gross_profit, 2)
            cac_loss = round(self.cac if is_first_time else 0.0, 2)
            net_ev = round(prevented_savings - lost_potential_margin, 2)
            expected_delivered = 0.0
            expected_loss = 0.0
            cac_exposure = cac_loss
            rationale = (
                f"Critical risk ({p_rto*100:.1f}%). Direct RTO cash saving of ₹{prevented_savings:.2f} outweighs "
                f"unreliable fulfillment probability. Address or customer profile is invalid/fraudulent."
            )
        else:
            expected_delivered = round(p_delivered * order_gross_profit, 2)
            expected_loss = round(p_rto * direct_rto_loss, 2)
            net_ev = round(ev_cod, 2)
            prevented_savings = 0.0
            cac_exposure = 0.0
            rationale = "Standard evaluation"

        return {
            "expected_delivered_margin": expected_delivered,
            "expected_rto_loss": expected_loss,
            "net_expected_value": net_ev,
            "prevented_rto_savings": prevented_savings,
            "cac_risk_exposure": cac_exposure,
            "recommendation_rationale": rationale
        }

    def calculate_optimal_discount(self, order_value: float, rto_prob: float) -> Dict[str, float]:
        """
        Calculates the maximum break-even discount and recommended discount percentage.
        Break-even discount = (p_rto - p_prepaid) * Direct RTO Loss
        """
        p_diff = max(0.0, rto_prob - self.prepaid_rto_rate)
        max_breakeven_rupees = round(p_diff * self.direct_rto_loss, 2)
        max_breakeven_pct = round((max_breakeven_rupees / order_value) * 100, 1) if order_value > 0 else 0.0
        
        # Recommended sweet spot: 50-70% of break-even, bounded between 5% and 12%
        recommended_pct = min(12.0, max(5.0, round(max_breakeven_pct * 0.6, 1)))
        recommended_rupees = round(order_value * (recommended_pct / 100.0), 2)
        
        return {
            "max_breakeven_rupees": max_breakeven_rupees,
            "max_breakeven_pct": max_breakeven_pct,
            "recommended_discount_pct": recommended_pct,
            "recommended_discount_rupees": recommended_rupees,
            "net_merchant_savings": round(max_breakeven_rupees - recommended_rupees, 2)
        }
