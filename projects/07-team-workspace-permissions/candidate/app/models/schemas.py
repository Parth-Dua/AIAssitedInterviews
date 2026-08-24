from typing import Literal, Optional

from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str


class WorkspaceMembership(BaseModel):
    """A user's role within a single workspace. Authority over anything in
    that workspace is derived entirely from this record — users don't carry
    a global role anywhere else.
    """

    workspace_id: str
    user_id: int
    role: str


class Document(BaseModel):
    id: int
    workspace_id: str
    owner_id: int
    title: str
    content: str


class DocumentPatchRequest(BaseModel):
    """Partial update. Any field left unset keeps its current value."""

    title: Optional[str] = None
    content: Optional[str] = None


class MembershipCreateRequest(BaseModel):
    """Request body for adding a member to a workspace."""

    user_id: int
    role: Literal["owner", "editor"]


class MembershipOut(BaseModel):
    workspace_id: str
    user_id: int
    role: str
