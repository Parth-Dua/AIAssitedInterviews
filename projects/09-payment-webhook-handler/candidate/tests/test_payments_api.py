from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_webhook_payment_succeeded_returns_received():
    response = client.post(
        "/webhooks/payment",
        json={
            "event_id": "evt-api-basic",
            "order_id": 101,
            "amount_cents": 1500,
            "status": "succeeded",
        },
    )
    assert response.status_code == 200
    assert response.json() == {"received": True}


def test_webhook_unknown_order_returns_404():
    response = client.post(
        "/webhooks/payment",
        json={
            "event_id": "evt-api-unknown",
            "order_id": 9999,
            "amount_cents": 1000,
            "status": "succeeded",
        },
    )
    assert response.status_code == 404


def test_webhook_rejects_invalid_status():
    response = client.post(
        "/webhooks/payment",
        json={
            "event_id": "evt-api-bad-status",
            "order_id": 102,
            "amount_cents": 1000,
            "status": "pending",
        },
    )
    assert response.status_code == 422
