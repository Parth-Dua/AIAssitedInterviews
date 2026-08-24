from typing import Optional

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """A user's account settings, as stored server-side."""

    user_id: int
    display_name: str = Field(min_length=1)
    bio: Optional[str] = None
    timezone: str
    email_notifications: bool


class ProfileUpdateRequest(BaseModel):
    """Partial-update request body for ``PATCH /users/{user_id}``.

    Every field is optional. A field that is *omitted* from the request body
    must leave the corresponding stored value untouched; only fields the
    caller actually included should be applied to the stored profile.
    """

    display_name: Optional[str] = Field(default=None, min_length=1)
    bio: Optional[str] = None
    timezone: Optional[str] = None
    email_notifications: Optional[bool] = None
