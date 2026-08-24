"""Hidden tests. Copy this file into candidate/tests/ (it is not present in
the candidate repo) and run `pytest` from candidate/ after applying a
candidate's fix, or after applying reference_solution/*.py to validate the
answer key.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import Document
from app.repositories.document_repository import DocumentRepository
from app.repositories.membership_repository import MembershipRepository
from app.services.permission_service import PermissionService

client = TestClient(app)


def _headers(user_id: int) -> dict:
    return {"X-User-Id": str(user_id)}


def make_permission_service() -> PermissionService:
    return PermissionService(MembershipRepository())


def make_documents() -> DocumentRepository:
    return DocumentRepository()


def test_workspace_owner_can_delete_others_document_second_instance():
    """A second same-workspace-owner-manages-a-non-owned-document case, in
    the other workspace than the public test uses. Catches an
    over-correction that removes the workspace-owner escape hatch entirely
    (e.g. reducing can_manage_document to `document.owner_id == user_id`),
    which stops the reported cross-workspace leak but also incorrectly
    breaks this legitimate, intended admin capability.
    """
    permissions = make_permission_service()
    documents = make_documents()
    doc = documents.get_document(5)  # engineering, owned by Carol (3)

    # Bob (2) is the engineering workspace owner but does not personally
    # own this document.
    assert permissions.can_manage_document(2, doc) is True


def test_owner_role_does_not_leak_into_other_workspace_reverse_direction():
    """Same class of bug as the reported one, exercised in the other
    direction: Bob is workspace owner in Engineering but only an editor
    (non-owner) in Marketing.
    """
    permissions = make_permission_service()
    documents = make_documents()
    doc = documents.get_document(2)  # marketing, owned by Alice (1)

    assert permissions.can_manage_document(2, doc) is False


def test_viewer_can_read_but_not_write_document():
    add = client.post(
        "/workspaces/engineering/members", json={"user_id": 401, "role": "viewer"}
    )
    assert add.status_code == 201

    read = client.get("/documents/4", headers=_headers(401))
    assert read.status_code == 200

    patch = client.patch(
        "/documents/4", json={"title": "Should not be allowed"}, headers=_headers(401)
    )
    assert patch.status_code == 403

    delete = client.delete("/documents/4", headers=_headers(401))
    assert delete.status_code == 403


def test_viewer_denied_even_if_they_are_the_documents_personal_owner():
    """A viewer should never legitimately be a document's owner_id in valid
    data, but the authorization code must not silently assume that — it
    must check the viewer role explicitly rather than relying on that
    invariant always holding.
    """
    membership_repository = MembershipRepository()
    membership_repository.add_membership(
        workspace_id="engineering", user_id=402, role="viewer"
    )
    permissions = PermissionService(membership_repository)
    doc = Document(
        id=999, workspace_id="engineering", owner_id=402, title="x", content="y"
    )

    assert permissions.can_edit_document(402, doc) is False
    assert permissions.can_manage_document(402, doc) is False


def test_add_member_invalid_role_rejected_with_informative_error():
    response = client.post(
        "/workspaces/marketing/members", json={"user_id": 500, "role": "superadmin"}
    )
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    detail_text = str(body["detail"]).lower()
    assert "owner" in detail_text and "editor" in detail_text
