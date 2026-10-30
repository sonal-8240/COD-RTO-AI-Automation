import pytest
from backend.services.risk_engine import RiskEngine
from backend.services.financial_model import FinancialModel

@pytest.fixture
def risk_engine():
    return RiskEngine()

def test_financial_constants():
    fin = FinancialModel()
    # Check exact assignment direct RTO formula: 65 + 65 + 25 + (0.08 * 180) = 169.40
    assert fin.direct_rto_loss == 169.40
    # Delivered gross profit on default ₹649 order at 62% margin: ₹402.38
    assert fin.delivered_gross_profit == 402.38

def test_ship_as_is_for_clean_repeat_customer(risk_engine):
    order = {
        "order_id": "TEST_AS_IS_01",
        "customer_name": "Priya Sharma",
        "address": "Flat 402, Sunshine Heights, MG Road, Indiranagar",
        "city": "Bengaluru",
        "state": "Karnataka",
        "pincode": "560038",
        "order_value": 649.0,
        "customer_prior_orders": 3,
        "customer_prior_rto": 0,
        "utm_source": "direct",
        "courier": "Delhivery"
    }
    res = risk_engine.evaluate_order(order)
    assert res["action"] == "SHIP_AS_IS"
    assert res["risk_level"] == "LOW"
    assert res["risk_score"] < 0.20
    assert any(f["name"] == "Clean Repeat Customer" for f in res["risk_factors"])

def test_ship_after_confirmation_for_first_time_customer(risk_engine):
    order = {
        "order_id": "TEST_CONFIRM_01",
        "customer_name": "Rahul Verma",
        "address": "House 12, Sector 15, Near City Hospital",
        "city": "Gurgaon",
        "state": "Haryana",
        "pincode": "122001",
        "order_value": 649.0,
        "customer_prior_orders": 0,
        "customer_prior_rto": 0,
        "utm_source": "google",
        "courier": "Delhivery"
    }
    res = risk_engine.evaluate_order(order)
    assert res["action"] == "SHIP_AFTER_CONFIRMATION"
    assert res["risk_score"] >= 0.20
    assert "confirm" in res["next_step"].lower()

def test_nudge_to_prepaid_for_high_value_elevated_risk(risk_engine):
    order = {
        "order_id": "TEST_PREPAID_01",
        "customer_name": "Aman Patel",
        "address": "Opposite Railway Station, Station Road",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "pincode": "380001",
        "order_value": 1499.0,  # High value order
        "customer_prior_orders": 0,
        "customer_prior_rto": 0,
        "utm_source": "meta",
        "courier": "Shadowfax"
    }
    res = risk_engine.evaluate_order(order)
    assert res["action"] == "NUDGE_TO_PREPAID"
    assert res["risk_level"] in ["MEDIUM", "HIGH"]
    assert "prepaid" in res["next_step"].lower()

def test_hold_or_cancel_for_defective_address(risk_engine):
    order = {
        "order_id": "TEST_CANCEL_01",
        "customer_name": "Amit Kumar",
        "address": "xyz",  # Defective placeholder address
        "city": "Delhi",
        "state": "Delhi",
        "pincode": "110001",
        "order_value": 649.0,
        "customer_prior_orders": 0,
        "customer_prior_rto": 0,
        "utm_source": "meta",
        "courier": "Delhivery"
    }
    res = risk_engine.evaluate_order(order)
    assert res["action"] == "HOLD_OR_CANCEL"
    assert res["risk_level"] in ["HIGH", "CRITICAL"]
    assert any("Defective" in f["name"] or "Address" in f["name"] for f in res["risk_factors"])

def test_hold_or_cancel_for_chronic_rto_abuser(risk_engine):
    order = {
        "order_id": "TEST_CANCEL_02",
        "customer_name": "Suresh Raina",
        "address": "Plot 54, Gandhi Nagar Colony",
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "pincode": "226001",
        "order_value": 649.0,
        "customer_prior_orders": 4,
        "customer_prior_rto": 3,  # 75% prior return rate!
        "utm_source": "meta",
        "courier": "Delhivery"
    }
    res = risk_engine.evaluate_order(order)
    assert res["action"] == "HOLD_OR_CANCEL"
    assert any("Prior RTO" in f["name"] for f in res["risk_factors"])

def test_hinglish_landmark_recognition(risk_engine):
    order = {
        "order_id": "TEST_HINGLISH_01",
        "customer_name": "Rohan Gupta",
        "address": "Makan No 44, Gali No 2, Peepal ke ped ke samne, Doodh dairy ke pass",
        "city": "Jaipur",
        "state": "Rajasthan",
        "pincode": "302001",
        "order_value": 649.0,
        "customer_prior_orders": 0,
        "customer_prior_rto": 0,
        "utm_source": "direct",
        "courier": "Delhivery"
    }
    res = risk_engine.evaluate_order(order)
    assert any("Landmark" in f["name"] for f in res["risk_factors"])
