from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_get_user_endpoint_returns_seeded_profile():
    response = client.get("/users/2")
    assert response.status_code == 200
    body = response.json()
    assert body["display_name"] == "Bob Martinez"
    assert body["bio"] == "Full-stack engineer, coffee enthusiast"
    assert body["timezone"] == "Europe/London"
    assert body["email_notifications"] is False


def test_get_nonexistent_user_returns_404():
    response = client.get("/users/999")
    assert response.status_code == 404


def test_patch_nonexistent_user_returns_404():
    response = client.patch("/users/999", json={"timezone": "UTC"})
    assert response.status_code == 404


def test_patch_empty_display_name_returns_422():
    response = client.patch("/users/1", json={"display_name": ""})
    assert response.status_code == 422
