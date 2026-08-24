from pydantic import BaseModel


class NotificationPreferences(BaseModel):
    """A user's notification channel preferences."""

    user_id: int
    email_enabled: bool
    sms_enabled: bool
    push_enabled: bool


class NotificationPreferencesUpdate(BaseModel):
    """Request body for a full replace of a user's notification
    preferences. All three channels must be specified.
    """

    email_enabled: bool
    sms_enabled: bool
    push_enabled: bool
