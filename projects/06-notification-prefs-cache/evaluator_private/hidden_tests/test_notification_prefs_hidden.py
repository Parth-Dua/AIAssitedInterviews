"""Hidden tests. Copy this file into candidate/tests/ (it is not present in
the candidate repo) and run `pytest` from candidate/ after applying a
candidate's fix, or after applying reference_solution/ to validate the
answer key.
"""

from app.cache.cache import Cache
from app.models.schemas import NotificationPreferencesUpdate
from app.repositories.notification_prefs_repository import (
    NotificationPreferencesRepository,
)
from app.services.notification_prefs_service import NotificationPreferencesService


def make_service(repository=None, cache=None) -> NotificationPreferencesService:
    return NotificationPreferencesService(
        repository or NotificationPreferencesRepository(), cache or Cache()
    )


class CountingRepository(NotificationPreferencesRepository):
    def __init__(self):
        super().__init__()
        self.get_call_count = 0

    def get(self, user_id: int):
        self.get_call_count += 1
        return super().get(user_id)


# --- Cache TTL boundary convention -----------------------------------------


def test_cache_ttl_boundary_exactly_at_ttl_is_expired():
    """Documents/pins the boundary convention: an entry is expired once
    `now() >= expires_at`, i.e. exactly at the `ttl_seconds` mark, not only
    strictly after it.
    """
    fake_now = [0.0]
    cache = Cache(now_fn=lambda: fake_now[0])
    cache.set("key", "value", ttl_seconds=10)

    fake_now[0] = 10.0  # exactly at the boundary
    assert cache.get("key") is None


def test_cache_ttl_boundary_just_before_ttl_is_still_present():
    fake_now = [0.0]
    cache = Cache(now_fn=lambda: fake_now[0])
    cache.set("key", "value", ttl_seconds=10)

    fake_now[0] = 9.999999
    assert cache.get("key") == "value"


# --- Write path: repeated PUTs always keep GET fresh ------------------------


def test_multiple_sequential_puts_each_invalidate_cache():
    """Several writes in a row, each followed by a read, must each reflect
    the latest write — not just the first invalidation.
    """
    service = make_service()

    for sms in (True, False, True, False):
        update = NotificationPreferencesUpdate(
            email_enabled=True, sms_enabled=sms, push_enabled=True
        )
        service.update_preferences(2, update)
        current = service.get_preferences(2)
        assert current.sms_enabled == sms, (
            f"expected sms_enabled={sms} after this PUT, got "
            f"{current.sms_enabled} — a stale cache entry from an earlier "
            "write is leaking through"
        )


# --- The "cache the request body instead of the persisted value" trap ------


def test_put_disable_all_channels_get_returns_persisted_not_request_body():
    """PUTs a request trying to disable all three channels. The server
    normalizes this by forcing email back on before persisting. A GET
    immediately after must reflect what was actually persisted (email
    True), not the raw pre-normalization request body (email False).

    This is the test that catches the tempting-but-incomplete fix: adding
    cache invalidation on write by *overwriting* the cache with the
    request body (or otherwise deriving the cached value from the request
    before normalization) instead of invalidating and letting the next
    read repopulate from — or otherwise caching exactly — what was
    persisted.
    """
    service = make_service()

    update = NotificationPreferencesUpdate(
        email_enabled=False, sms_enabled=False, push_enabled=False
    )
    put_result = service.update_preferences(1, update)
    assert put_result.email_enabled is True  # sanity: normalization ran

    get_result = service.get_preferences(1)
    assert get_result is not None
    assert get_result.email_enabled is True, (
        "GET after the PUT returned email_enabled=False, matching the raw "
        "request body instead of the normalized value that was actually "
        "persisted — the cache is diverging from the repository"
    )
    assert get_result.sms_enabled is False
    assert get_result.push_enabled is False
    assert get_result == put_result


# --- Natural expiry falls through and repopulates ---------------------------


def test_cache_naturally_expires_then_repopulates_with_fresh_ttl():
    """If a cache entry is allowed to expire (clock advanced past its TTL)
    without any write happening, the next GET must fall through to the
    repository, return the correct (repository) value, and repopulate the
    cache with a fresh TTL — a following GET should then be served from
    cache again without hitting the repository.
    """
    fake_now = [0.0]
    cache = Cache(now_fn=lambda: fake_now[0])
    repository = CountingRepository()
    service = make_service(repository=repository, cache=cache)

    first = service.get_preferences(3)
    assert repository.get_call_count == 1

    # Still within the TTL window: should be served from cache.
    second = service.get_preferences(3)
    assert repository.get_call_count == 1
    assert second == first

    # Advance well past any reasonable default TTL.
    fake_now[0] += 3600.0

    third = service.get_preferences(3)
    assert third == first
    assert repository.get_call_count == 2, (
        "expected the expired entry to fall through to the repository "
        "exactly once more"
    )

    # The cache should have been repopulated with a fresh TTL — another
    # immediate GET should not hit the repository again.
    fourth = service.get_preferences(3)
    assert fourth == first
    assert repository.get_call_count == 2
