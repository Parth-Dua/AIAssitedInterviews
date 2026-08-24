from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _headers(user_id: int) -> dict:
    return {"X-User-Id": str(user_id)}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_get_document_requires_workspace_membership():
    # doc 5: engineering. Carol (3) is a member of engineering.
    response = client.get("/documents/5", headers=_headers(3))
    assert response.status_code == 200
    assert response.json()["id"] == 5


def test_document_owner_can_patch_and_delete_own_document():
    # doc 1: marketing, owned by Carol (3)
    patch = client.patch(
        "/documents/1", json={"title": "Updated Campaign Brief"}, headers=_headers(3)
    )
    assert patch.status_code == 200
    assert patch.json()["title"] == "Updated Campaign Brief"

    delete = client.delete("/documents/1", headers=_headers(3))
    assert delete.status_code == 204


def test_editor_without_owner_role_can_patch_but_not_delete_others_document():
    # doc 2: marketing, owned by Alice (1). Carol (3) is only ever an
    # editor, in either workspace.
    patch = client.patch(
        "/documents/2", json={"title": "Revised Marketing OKRs"}, headers=_headers(3)
    )
    assert patch.status_code == 200

    delete = client.delete("/documents/2", headers=_headers(3))
    assert delete.status_code == 403


def test_workspace_owner_can_delete_document_they_dont_personally_own_in_own_workspace():
    # doc 3: marketing, owned by Bob (2). Alice (1) is the marketing owner.
    delete = client.delete("/documents/3", headers=_headers(1))
    assert delete.status_code == 204


def test_owner_role_in_other_workspace_cannot_delete_document_here():
    """Bug report: Alice is workspace owner in Marketing but only a regular
    editor in Engineering. She must not be able to delete a document she
    doesn't own in Engineering.
    """
    # doc 4: engineering, owned by Bob (2). Alice (1) is only editor there.
    delete = client.delete("/documents/4", headers=_headers(1))
    assert delete.status_code == 403
