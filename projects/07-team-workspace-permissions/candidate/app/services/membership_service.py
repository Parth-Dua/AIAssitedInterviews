from app.models.schemas import MembershipCreateRequest, WorkspaceMembership
from app.repositories.membership_repository import MembershipRepository


class MembershipService:
    def __init__(self, membership_repository: MembershipRepository):
        self._membership_repository = membership_repository

    def add_member(
        self, workspace_id: str, request: MembershipCreateRequest
    ) -> WorkspaceMembership:
        return self._membership_repository.add_membership(
            workspace_id=workspace_id, user_id=request.user_id, role=request.role
        )
