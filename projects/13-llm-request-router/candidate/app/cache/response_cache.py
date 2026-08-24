"""A small in-memory cache for completed model responses, standing in for a
Redis-like cache layer that would sit in front of a real (paid, networked)
model provider in production. Pure Python, dict-backed — no external cache
server involved.

This module only stores and retrieves values by key. It has no opinion
about *what* should be cached or *when* a cache entry is allowed to be
written — that policy decision belongs to whatever calls `set()`, not to
the cache itself.
"""

from typing import Optional


class ResponseCache:
    def __init__(self):
        self._store: dict[str, object] = {}

    def get(self, key: str) -> Optional[object]:
        return self._store.get(key)

    def set(self, key: str, value: object) -> None:
        self._store[key] = value

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()
