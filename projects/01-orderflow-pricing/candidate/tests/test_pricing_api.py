from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_price_order_endpoint_basic():
    response = client.post(
        "/orders/price",
        json={"items": [{"sku": "A", "unit_price_cents": 1000, "quantity": 2}]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["subtotal_cents"] == 2000


def test_price_order_rejects_zero_quantity():
    response = client.post(
        "/orders/price",
        json={"items": [{"sku": "A", "unit_price_cents": 1000, "quantity": 0}]},
    )
    assert response.status_code == 422
