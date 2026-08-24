"""Reference solution — TieredRateLimiter.

The whole point of this class: it must depend only on the `RateLimiter`
interface, never on any concrete implementation. It should work correctly
with a `default`/`overrides` limiter of any type at all, including types
that don't exist yet at the time this class is written.
"""

from typing import Dict, Optional

from .base import RateLimiter


class TieredRateLimiter(RateLimiter):
    def __init__(self, default: RateLimiter, overrides: Optional[Dict[str, RateLimiter]] = None):
        self._default = default
        self._overrides: Dict[str, RateLimiter] = dict(overrides) if overrides else {}

    def allow_request(self, key: str) -> bool:
        limiter = self._overrides.get(key, self._default)
        return limiter.allow_request(key)
