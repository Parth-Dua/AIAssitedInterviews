from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_add_editor_member_succeeds():
    response = client.post(
        "/workspaces/marketing/members", json={"user_id": 99, "role": "editor"}
    )
    assert response.status_code == 201
    assert response.json() == {"workspace_id": "marketing", "user_id": 99, "role": "editor"}


def test_add_viewer_member():
    """Feature request: workspaces should support a read-only viewer role
    for members who should be able to see documents but never change them.
    """
    response = client.post(
        "/workspaces/marketing/members", json={"user_id": 98, "role": "viewer"}
    )
    assert response.status_code == 201


def test_add_member_with_invalid_role_is_rejected():
    response = client.post(
        "/workspaces/marketing/members", json={"user_id": 97, "role": "superadmin"}
    )
    assert response.status_code == 422
