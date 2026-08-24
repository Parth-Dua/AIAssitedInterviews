"""Part 1 — implement TokenBucketRateLimiter.

See the "Part 1 — Token Bucket" section of the README for the full
requirements. This file only gives you the shape of the class; the body is
up to you.
"""

import time
from typing import Callable

from .base import RateLimiter


class TokenBucketRateLimiter(RateLimiter):
    def __init__(
        self,
        capacity: int,
        refill_rate_per_second: float,
        now_fn: Callable[[], float] = time.monotonic,
    ):
        raise NotImplementedError

    def allow_request(self, key: str) -> bool:
        raise NotImplementedError
