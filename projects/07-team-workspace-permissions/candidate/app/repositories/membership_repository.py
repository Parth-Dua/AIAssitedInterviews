from app.models.schemas import WorkspaceMembership


class MembershipRepository:
    """In-memory store of workspace memberships.

    Each record ties one user to one workspace with a role. A user can hold
    different roles in different workspaces — there's no single "the role"
    for a user, only "their role in workspace X".
    """

    def __init__(self):
        self._memberships: list[WorkspaceMembership] = [
            WorkspaceMembership(workspace_id="marketing", user_id=1, role="owner"),
            WorkspaceMembership(workspace_id="marketing", user_id=2, role="editor"),
            WorkspaceMembership(workspace_id="marketing", user_id=3, role="editor"),
            WorkspaceMembership(workspace_id="engineering", user_id=2, role="owner"),
            WorkspaceMembership(workspace_id="engineering", user_id=1, role="editor"),
            WorkspaceMembership(workspace_id="engineering", user_id=3, role="editor"),
        ]

    def get_membership(
        self, user_id: int, workspace_id: str
    ) -> WorkspaceMembership | None:
        """A user's role within one specific workspace, or None if they
        aren't a member of it.
        """
        for membership in self._memberships:
            if membership.user_id == user_id and membership.workspace_id == workspace_id:
                return membership
        return None

    def get_memberships_for_user(self, user_id: int) -> list[WorkspaceMembership]:
        """Every workspace a user belongs to, across the whole system."""
        return [m for m in self._memberships if m.user_id == user_id]

    def get_memberships_for_workspace(
        self, workspace_id: str
    ) -> list[WorkspaceMembership]:
        return [m for m in self._memberships if m.workspace_id == workspace_id]

    def add_membership(
        self, workspace_id: str, user_id: int, role: str
    ) -> WorkspaceMembership:
        existing = self.get_membership(user_id, workspace_id)
        if existing is not None:
            self._memberships.remove(existing)
        membership = WorkspaceMembership(
            workspace_id=workspace_id, user_id=user_id, role=role
        )
        self._memberships.append(membership)
        return membership
