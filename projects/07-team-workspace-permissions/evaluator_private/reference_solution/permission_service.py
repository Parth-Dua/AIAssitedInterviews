from app.models.schemas import Document
from app.repositories.membership_repository import MembershipRepository


class PermissionService:
    """Authorization checks for documents. All authority over a document
    comes from either personally owning it, or from the caller's role
    within the document's own workspace. A viewer's role is checked first
    and short-circuits everything else — a viewer can never edit or delete,
    even in the edge case where they happen to be a document's owner_id.
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
        workspace, may edit it. Viewers never can.
        """
        membership = self._membership_repository.get_membership(
            user_id, document.workspace_id
        )
        if membership is not None and membership.role == "viewer":
            return False
        if document.owner_id == user_id:
            return True
        return membership is not None and membership.role in ("owner", "editor")

    def can_manage_document(self, user_id: int, document: Document) -> bool:
        """The document's owner, or a workspace member with the "owner"
        role *in that document's own workspace*, may edit or delete it.
        Viewers never can. A role held in some other workspace confers no
        authority here.
        """
        membership = self._membership_repository.get_membership(
            user_id, document.workspace_id
        )
        if membership is not None and membership.role == "viewer":
            return False
        if document.owner_id == user_id:
            return True
        return membership is not None and membership.role == "owner"
