import time
from typing import Callable, Optional


class Cache:
    """A small in-memory cache, standing in for a Redis-like cache layer
    that would sit in front of a real database in production. Pure
    Python, dict-backed — no external cache server required.

    Entries may carry an optional TTL (time-to-live), in seconds. `get()`
    treats an expired entry as a miss and evicts it at that point. The
    boundary is inclusive: an entry is considered expired once
    `now() >= expires_at` (i.e. exactly `ttl_seconds` after it was set, not
    a moment later) — this matches the usual "entry is stale starting at
    its expiry instant" convention and keeps the boundary deterministic
    for tests.

    The clock is injectable via `now_fn` (defaults to `time.monotonic`) so
    callers/tests can control time deterministically instead of relying on
    real wall-clock sleeps.
    """

    def __init__(self, now_fn: Callable[[], float] = time.monotonic):
        self._now = now_fn
        self._store: dict[str, object] = {}
        self._expires_at: dict[str, float] = {}

    def get(self, key: str) -> Optional[object]:
        if key not in self._store:
            return None

        expires_at = self._expires_at.get(key)
        if expires_at is not None and self._now() >= expires_at:
            self._evict(key)
            return None

        return self._store[key]

    def set(
        self, key: str, value: object, ttl_seconds: Optional[float] = None
    ) -> None:
        self._store[key] = value
        if ttl_seconds is None:
            self._expires_at.pop(key, None)
        else:
            self._expires_at[key] = self._now() + ttl_seconds

    def delete(self, key: str) -> None:
        self._evict(key)

    def _evict(self, key: str) -> None:
        self._store.pop(key, None)
        self._expires_at.pop(key, None)
