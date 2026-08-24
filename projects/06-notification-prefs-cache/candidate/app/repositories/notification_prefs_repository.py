from typing import Optional

from app.models.schemas import NotificationPreferences


def _seed_preferences() -> dict[int, NotificationPreferences]:
    """Sample seeded users. In production this would be backed by a real
    database table; here it's a static in-memory dict seeded once at
    process start, standing in for a "real DB" read.
    """
    raw = [
        # (user_id, email_enabled, sms_enabled, push_enabled)
        (1, True, True, False),
        (2, True, False, False),
        (3, False, True, True),
        (4, True, True, True),
    ]
    return {
        user_id: NotificationPreferences(
            user_id=user_id,
            email_enabled=email_enabled,
            sms_enabled=sms_enabled,
            push_enabled=push_enabled,
        )
        for user_id, email_enabled, sms_enabled, push_enabled in raw
    }


class NotificationPreferencesRepository:
    """In-memory store of per-user notification preferences.

    Stands in for a real database table. A cache layer sits in front of
    this repository (see `app.cache.cache.Cache`) so that repeated reads
    for the same user don't have to come back here every time.
    """

    def __init__(self):
        self._preferences: dict[int, NotificationPreferences] = _seed_preferences()

    def get(self, user_id: int) -> Optional[NotificationPreferences]:
        return self._preferences.get(user_id)

    def save(self, preferences: NotificationPreferences) -> NotificationPreferences:
        self._preferences[preferences.user_id] = preferences
        return preferences
