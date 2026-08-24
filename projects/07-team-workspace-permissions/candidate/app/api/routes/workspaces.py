from fastapi import APIRouter

from app.api.deps import membership_service
from app.models.schemas import MembershipCreateRequest, MembershipOut

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("/{workspace_id}/members", response_model=MembershipOut, status_code=201)
def add_member(workspace_id: str, request: MembershipCreateRequest) -> MembershipOut:
    """Add (or update) a user's membership in a workspace."""
    membership = membership_service.add_member(workspace_id, request)
    return MembershipOut(
        workspace_id=membership.workspace_id,
        user_id=membership.user_id,
        role=membership.role,
    )
