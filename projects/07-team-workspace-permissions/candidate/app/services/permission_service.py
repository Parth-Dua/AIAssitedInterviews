from app.models.schemas import Document
from app.repositories.membership_repository import MembershipRepository


class PermissionService:
    """Authorization checks for documents. All authority over a document
    comes from either personally owning it, or from the caller's role
    within the document's own workspace.
    """

    def __init__(self, membership_repository: MembershipRepository):
        self._membership_repository = membership_repository

    def can_read_document(self, user_id: int, document: Document) -> bool:
        """Any member of the document's workspace can read it."""
        membership = self._membership_repository.get_membership(
            user_id, document.workspace_id
        )
        return membership is not None

    def can_edit_document(self, user_id: int, document: Document) -> bool:
        """The document's owner, or any owner/editor member of its
        workspace, may edit it.
        """
        if document.owner_id == user_id:
            return True
        membership = self._membership_repository.get_membership(
            user_id, document.workspace_id
        )
        return membership is not None and membership.role in ("owner", "editor")

    def can_manage_document(self, user_id: int, document: Document) -> bool:
        """The document's owner, or a workspace member with the "owner"
        role, may edit or delete it.
        """
        if document.owner_id == user_id:
            return True
        memberships = self._membership_repository.get_memberships_for_user(user_id)
        return any(m.role == "owner" for m in memberships)
