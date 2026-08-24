from fastapi import APIRouter, HTTPException

from app.cache.cache import Cache
from app.models.schemas import NotificationPreferences, NotificationPreferencesUpdate
from app.repositories.notification_prefs_repository import (
    NotificationPreferencesRepository,
)
from app.services.notification_prefs_service import NotificationPreferencesService

router = APIRouter(prefix="/users", tags=["notification-preferences"])

_repository = NotificationPreferencesRepository()
_cache = Cache()
_service = NotificationPreferencesService(_repository, _cache)


@router.get(
    "/{user_id}/notification-preferences", response_model=NotificationPreferences
)
def get_notification_preferences(user_id: int) -> NotificationPreferences:
    """Return a user's notification channel preferences. Backed by a
    read-through cache in front of the repository.
    """
    preferences = _service.get_preferences(user_id)
    if preferences is None:
        raise HTTPException(status_code=404, detail="user not found")
    return preferences


@router.put(
    "/{user_id}/notification-preferences", response_model=NotificationPreferences
)
def update_notification_preferences(
    user_id: int, update: NotificationPreferencesUpdate
) -> NotificationPreferences:
    """Full replace of a user's notification channel preferences."""
    return _service.update_preferences(user_id, update)
