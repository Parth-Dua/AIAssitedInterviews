"""Part 2 — implement TieredRateLimiter.

See the "Part 2 — Follow-Up" section of the README for the full
requirements. This file only gives you the shape of the class; the body is
up to you.

Do not start this file until Part 1 (token_bucket.py) is done and tested —
the README explains why.
"""

from typing import Optional

from .base import RateLimiter


class TieredRateLimiter(RateLimiter):
    def __init__(self, default: RateLimiter, overrides: Optional[dict] = None):
        raise NotImplementedError

    def allow_request(self, key: str) -> bool:
        raise NotImplementedError
