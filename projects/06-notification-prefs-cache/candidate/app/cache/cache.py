import time
from typing import Callable, Optional


class Cache:
    """A small in-memory cache, standing in for a Redis-like cache layer
    that would sit in front of a real database in production. Pure
    Python, dict-backed — no external cache server required.

    The clock used for any future time-based behavior is injectable via
    `now_fn` (defaults to `time.monotonic`) so callers/tests can control
    time deterministically instead of relying on real wall-clock sleeps.

    # TODO: entries never expire yet. Add TTL (time-to-live) support so a
    # cached entry automatically falls out after a configurable number of
    # seconds: `set(key, value, ttl_seconds=...)`, and `get()` should treat
    # an expired entry as a miss and evict it.
    """

    def __init__(self, now_fn: Callable[[], float] = time.monotonic):
        self._now = now_fn
        self._store: dict[str, object] = {}

    def get(self, key: str) -> Optional[object]:
        return self._store.get(key)

    def set(self, key: str, value: object) -> None:
        self._store[key] = value

    def delete(self, key: str) -> None:
        self._store.pop(key, None)
