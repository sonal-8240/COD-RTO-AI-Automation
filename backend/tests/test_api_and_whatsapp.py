import pytest
import uuid

def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_get_settings(client):
    res = client.get("/api/settings")
    assert res.status_code == 200
    data = res.json()
    assert "threshold_low_risk" in data
    assert "direct_rto_loss" in data
    assert data["direct_rto_loss"] == 169.40

def test_settings_validation_rejects_invalid_order(client):
    # low risk > medium risk should return 400
    bad_payload = {
        "threshold_low_risk": 0.50,
        "threshold_medium_risk": 0.20,
        "threshold_high_risk": 0.70,
        "threshold_cancel_risk": 0.70,
        "min_pincode_sample_size": 5,
        "prepaid_discount_percent": 8.0,
        "confirmation_timeout_hours": 24,
        "default_aov": 649.0,
        "gross_margin_pct": 0.62,
        "forward_shipping_cost": 65.0,
        "return_shipping_cost": 65.0,
        "packaging_handling_cost": 25.0,
        "damage_probability": 0.08,
        "product_cost": 180.0,
        "direct_rto_loss": 169.40,
        "cac": 300.0
    }
    res = client.put("/api/settings", json=bad_payload)
    assert res.status_code == 400

def test_evaluate_order_api(client):
    order_payload = {
        "order_id": "API_TEST_01",
        "customer_name": "Deepika Padukone",
        "address": "1204 Palm Beach Road, Bandra West",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400050",
        "order_value": 799.0,
        "customer_prior_orders": 2,
        "customer_prior_rto": 0,
        "utm_source": "direct",
        "courier": "Delhivery",
        "payment_method": "COD"
    }
    res = client.post("/api/orders/evaluate", json=order_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["order_id"] == "API_TEST_01"
    assert data["action"] in ["SHIP_AS_IS", "SHIP_AFTER_CONFIRMATION", "NUDGE_TO_PREPAID", "HOLD_OR_CANCEL"]
    assert "expected_financial_impact" in data

def test_whatsapp_confirmation_workflow(client):
    # Create fresh order for test
    fresh_id = f"TEST_ORD_{uuid.uuid4().hex[:8]}"
    client.post("/api/orders", json={
        "order_id": fresh_id,
        "customer_name": "Test Customer",
        "phone": "9876543210",
        "address": "Flat 101, Test Street",
        "city": "Pune",
        "state": "Maharashtra",
        "pincode": "411001",
        "order_value": 649.0
    })

    # 1. Start confirmation flow
    start_res = client.post("/api/whatsapp/start", json={"order_id": fresh_id, "workflow_type": "CONFIRMATION"})
    assert start_res.status_code == 200
    conv_data = start_res.json()
    conv_id = conv_data["conversation_id"]
    assert conv_data["current_state"] == "PENDING_REPLY"
    assert len(conv_data["messages"]) >= 1

    # 2. Customer replies YES
    reply_res = client.post(f"/api/whatsapp/{conv_id}/reply", json={"text": "YES, please dispatch"})
    assert reply_res.status_code == 200
    reply_data = reply_res.json()
    assert reply_data["current_state"] == "CONFIRMED"

def test_whatsapp_prepaid_workflow_and_timeout(client):
    fresh_id = f"TEST_ORD_{uuid.uuid4().hex[:8]}"
    client.post("/api/orders", json={
        "order_id": fresh_id,
        "customer_name": "Prepaid Customer",
        "phone": "9876543211",
        "address": "House 50, Sector 2",
        "city": "Noida",
        "state": "Uttar Pradesh",
        "pincode": "201301",
        "order_value": 1299.0
    })

    # 1. Start prepaid nudge flow
    start_res = client.post("/api/whatsapp/start", json={"order_id": fresh_id, "workflow_type": "PREPAID_NUDGE", "discount_pct": 10.0})
    assert start_res.status_code == 200
    conv_id = start_res.json()["conversation_id"]

    # 2. Advance time past 24 hours to trigger TIMEOUT
    advance_res = client.post(f"/api/whatsapp/{conv_id}/advance-time", json={"hours": 26})
    assert advance_res.status_code == 200
    assert advance_res.json()["current_state"] == "TIMEOUT"

