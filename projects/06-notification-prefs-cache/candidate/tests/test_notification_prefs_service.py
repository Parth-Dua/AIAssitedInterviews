from app.cache.cache import Cache
from app.models.schemas import NotificationPreferencesUpdate
from app.repositories.notification_prefs_repository import (
    NotificationPreferencesRepository,
)
from app.services.notification_prefs_service import NotificationPreferencesService


class CountingRepository(NotificationPreferencesRepository):
    """Spy repository that counts calls to `get()`, so tests can assert
    the cache is actually being used (i.e. the "expensive" repository read
    only happens on a cache miss).
    """

    def __init__(self):
        super().__init__()
        self.get_call_count = 0

    def get(self, user_id: int):
        self.get_call_count += 1
        return super().get(user_id)


def make_service(repository=None, cache=None) -> NotificationPreferencesService:
    return NotificationPreferencesService(
        repository or NotificationPreferencesRepository(), cache or Cache()
    )


def test_get_returns_seeded_preferences():
    service = make_service()
    preferences = service.get_preferences(1)
    assert preferences is not None
    assert preferences.user_id == 1
    assert preferences.email_enabled is True
    assert preferences.sms_enabled is True
    assert preferences.push_enabled is False


def test_get_unknown_user_returns_none():
    service = make_service()
    assert service.get_preferences(999) is None


def test_repeated_get_uses_cache_and_reads_repository_only_once():
    """Two GETs in a row without any write in between should return the
    same (cached) values, and the repository — the "expensive" read —
    should only actually be hit once.
    """
    repository = CountingRepository()
    service = make_service(repository=repository)

    first = service.get_preferences(2)
    second = service.get_preferences(2)

    assert first == second
    assert repository.get_call_count == 1, (
        "expected the second GET to be served from the cache without "
        f"reading the repository again, but the repository was read "
        f"{repository.get_call_count} times"
    )


def test_put_then_immediate_get_returns_new_values():
    """Bug report: a user turned SMS off, got a confirmation the change
    saved, but the settings page still showed the old value right after
    saving. A GET immediately following a successful PUT must reflect the
    values that were just written, not a stale cached copy.
    """
    service = make_service()

    # Warm the cache with the original (seeded) preferences.
    original = service.get_preferences(2)
    assert original.sms_enabled is False

    update = NotificationPreferencesUpdate(
        email_enabled=True, sms_enabled=True, push_enabled=True
    )
    service.update_preferences(2, update)

    refreshed = service.get_preferences(2)
    assert refreshed.sms_enabled is True, (
        "GET returned a stale cached value after the PUT — the cache was "
        "not updated/invalidated on write"
    )
    assert refreshed.email_enabled is True
    assert refreshed.push_enabled is True


def test_disabling_all_channels_forces_email_back_on():
    """Product rule: a user must keep at least one channel enabled. This
    rule already works correctly — it's context for the exercise, not the
    bug. Checked against what update_preferences() reports as persisted,
    independent of the cache/read path.
    """
    service = make_service()
    update = NotificationPreferencesUpdate(
        email_enabled=False, sms_enabled=False, push_enabled=False
    )
    saved = service.update_preferences(1, update)

    assert saved.email_enabled is True, "email should be forced back on"
    assert saved.sms_enabled is False
    assert saved.push_enabled is False
