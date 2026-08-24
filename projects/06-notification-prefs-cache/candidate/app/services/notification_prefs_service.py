from typing import Optional

from app.cache.cache import Cache
from app.models.schemas import NotificationPreferences, NotificationPreferencesUpdate
from app.repositories.notification_prefs_repository import (
    NotificationPreferencesRepository,
)

_CACHE_KEY_PREFIX = "prefs:"


def _cache_key(user_id: int) -> str:
    return f"{_CACHE_KEY_PREFIX}{user_id}"


class NotificationPreferencesService:
    """Read-through cache in front of NotificationPreferencesRepository.

    Read path: check the cache first; on a miss, read the repository and
    populate the cache so the next read is cheap.

    Write path: a full replace of a user's preferences. Also applies one
    small server-side normalization rule (see `update_preferences`).
    """

    def __init__(
        self, repository: NotificationPreferencesRepository, cache: Cache
    ):
        self._repository = repository
        self._cache = cache

    def get_preferences(self, user_id: int) -> Optional[NotificationPreferences]:
        key = _cache_key(user_id)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        preferences = self._repository.get(user_id)
        if preferences is None:
            return None

        self._cache.set(key, preferences)
        return preferences

    def update_preferences(
        self, user_id: int, update: NotificationPreferencesUpdate
    ) -> NotificationPreferences:
        email_enabled = update.email_enabled
        sms_enabled = update.sms_enabled
        push_enabled = update.push_enabled

        # Product rule: a user must always keep at least one notification
        # channel enabled. If a request would disable all three at once,
        # email is force-enabled server-side rather than rejecting the
        # request.
        if not (email_enabled or sms_enabled or push_enabled):
            email_enabled = True

        preferences = NotificationPreferences(
            user_id=user_id,
            email_enabled=email_enabled,
            sms_enabled=sms_enabled,
            push_enabled=push_enabled,
        )
        saved = self._repository.save(preferences)

        return saved
