from app.repositories.document_repository import DocumentRepository
from app.repositories.membership_repository import MembershipRepository
from app.services.permission_service import PermissionService


def make_permission_service() -> PermissionService:
    return PermissionService(MembershipRepository())


def make_documents() -> DocumentRepository:
    return DocumentRepository()


def test_document_owner_can_manage_their_own_document():
    permissions = make_permission_service()
    documents = make_documents()
    doc = documents.get_document(1)  # marketing, owned by Carol (3)

    assert permissions.can_edit_document(3, doc) is True
    assert permissions.can_manage_document(3, doc) is True


def test_editor_with_no_owner_role_anywhere_can_edit_but_not_delete_others_doc():
    """Carol is an editor in both workspaces and never an owner anywhere.
    Editors can edit any document in their workspace but can only delete
    documents they personally own.
    """
    permissions = make_permission_service()
    documents = make_documents()
    doc = documents.get_document(2)  # marketing, owned by Alice (1)

    assert permissions.can_edit_document(3, doc) is True
    assert permissions.can_manage_document(3, doc) is False


def test_workspace_owner_can_manage_document_they_dont_personally_own_in_own_workspace():
    """Alice is the marketing workspace owner but does not personally own
    this document. Workspace owners can manage any document in their own
    workspace.
    """
    permissions = make_permission_service()
    documents = make_documents()
    doc = documents.get_document(3)  # marketing, owned by Bob (2)

    assert permissions.can_manage_document(1, doc) is True


def test_owner_role_in_one_workspace_does_not_grant_manage_rights_in_another():
    """Reproduces the escalated bug report: Alice is the workspace owner in
    Marketing, but only an editor (non-owner) in Engineering. She should not
    be able to manage a document she doesn't own in Engineering.
    """
    permissions = make_permission_service()
    documents = make_documents()
    doc = documents.get_document(4)  # engineering, owned by Bob (2)

    assert permissions.can_manage_document(1, doc) is False
