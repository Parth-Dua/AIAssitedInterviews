"""Reference solution — TokenBucketRateLimiter."""

import time
from dataclasses import dataclass
from typing import Callable, Dict

from .base import RateLimiter


@dataclass
class _BucketState:
    tokens: float
    last_refill_at: float


class TokenBucketRateLimiter(RateLimiter):
    def __init__(
        self,
        capacity: int,
        refill_rate_per_second: float,
        now_fn: Callable[[], float] = time.monotonic,
    ):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_rate_per_second < 0:
            raise ValueError("refill_rate_per_second must be non-negative")

        self._capacity = capacity
        self._refill_rate = refill_rate_per_second
        self._now_fn = now_fn
        self._buckets: Dict[str, _BucketState] = {}

    def _get_or_create_bucket(self, key: str, now: float) -> _BucketState:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _BucketState(tokens=float(self._capacity), last_refill_at=now)
            self._buckets[key] = bucket
        return bucket

    def _refill(self, bucket: _BucketState, now: float) -> None:
        elapsed = now - bucket.last_refill_at
        if elapsed > 0:
            bucket.tokens = min(self._capacity, bucket.tokens + elapsed * self._refill_rate)
        bucket.last_refill_at = now

    def allow_request(self, key: str) -> bool:
        now = self._now_fn()
        bucket = self._get_or_create_bucket(key, now)
        self._refill(bucket, now)

        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False
