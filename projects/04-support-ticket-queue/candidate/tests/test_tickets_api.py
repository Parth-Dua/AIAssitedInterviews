from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_create_ticket_endpoint_basic():
    response = client.post(
        "/tickets",
        json={"subject": "Laptop won't boot", "watchers": ["grace@company.example"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["subject"] == "Laptop won't boot"
    assert body["status"] == "open"
    assert "grace@company.example" in body["watchers"]


def test_get_ticket_not_found():
    response = client.get("/tickets/999999")
    assert response.status_code == 404


def test_create_ticket_rejects_missing_subject():
    response = client.post("/tickets", json={"watchers": ["grace@company.example"]})
    assert response.status_code == 422
