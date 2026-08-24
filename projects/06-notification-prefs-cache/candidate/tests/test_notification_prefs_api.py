from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_get_notification_preferences_endpoint_basic():
    response = client.get("/users/3/notification-preferences")
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == 3
    assert body["email_enabled"] is False
    assert body["sms_enabled"] is True
    assert body["push_enabled"] is True


def test_get_notification_preferences_unknown_user_returns_404():
    response = client.get("/users/999/notification-preferences")
    assert response.status_code == 404


def test_put_notification_preferences_endpoint_returns_updated_shape():
    response = client.put(
        "/users/4/notification-preferences",
        json={"email_enabled": False, "sms_enabled": True, "push_enabled": False},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == 4
    assert body["email_enabled"] is False
    assert body["sms_enabled"] is True
    assert body["push_enabled"] is False


def test_put_notification_preferences_rejects_missing_field():
    response = client.put(
        "/users/4/notification-preferences",
        json={"email_enabled": False, "sms_enabled": True},
    )
    assert response.status_code == 422
