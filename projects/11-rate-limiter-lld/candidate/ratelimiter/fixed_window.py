"""Part 2 — implement FixedWindowRateLimiter.

See the "Part 2 — Follow-Up" section of the README for the full
requirements. This file only gives you the shape of the class; the body is
up to you.

Do not start this file until Part 1 (token_bucket.py) is done and tested —
the README explains why.
"""

import time
from typing import Callable

from .base import RateLimiter


class FixedWindowRateLimiter(RateLimiter):
    def __init__(
        self,
        max_requests: int,
        window_seconds: float,
        now_fn: Callable[[], float] = time.monotonic,
    ):
        raise NotImplementedError

    def allow_request(self, key: str) -> bool:
        raise NotImplementedError
