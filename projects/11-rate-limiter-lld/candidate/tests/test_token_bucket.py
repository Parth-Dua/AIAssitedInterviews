"""Part 1 public tests for TokenBucketRateLimiter.

These use a fake, fully-controllable clock (`FakeClock`) so no test ever
sleeps in real time. Advance the clock explicitly to simulate elapsed time.
"""

from ratelimiter import TokenBucketRateLimiter


class FakeClock:
    """A controllable stand-in for time.monotonic()."""

    def __init__(self, start: float = 0.0):
        self._now = start

    def __call__(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds


def test_bucket_starts_full_and_allows_up_to_capacity():
    clock = FakeClock()
    limiter = TokenBucketRateLimiter(capacity=3, refill_rate_per_second=1.0, now_fn=clock)

    assert limiter.allow_request("user-a") is True
    assert limiter.allow_request("user-a") is True
    assert limiter.allow_request("user-a") is True
    # Bucket is now empty (started full at 3, consumed 3, no time elapsed).
    assert limiter.allow_request("user-a") is False


def test_bucket_refills_over_time():
    clock = FakeClock()
    limiter = TokenBucketRateLimiter(capacity=2, refill_rate_per_second=1.0, now_fn=clock)

    assert limiter.allow_request("user-a") is True
    assert limiter.allow_request("user-a") is True
    assert limiter.allow_request("user-a") is False

    # Advance the clock enough to refill at least one token.
    clock.advance(1.0)
    assert limiter.allow_request("user-a") is True

    # Only one token was refilled (1 second * 1/sec), so the next call
    # should be rejected again immediately.
    assert limiter.allow_request("user-a") is False


def test_bucket_refill_is_capped_at_capacity():
    clock = FakeClock()
    limiter = TokenBucketRateLimiter(capacity=2, refill_rate_per_second=10.0, now_fn=clock)

    # Let a huge amount of time pass with no requests at all.
    clock.advance(1000.0)

    # Even though refill_rate * elapsed is huge, the bucket should never
    # hold more than `capacity` tokens.
    assert limiter.allow_request("user-a") is True
    assert limiter.allow_request("user-a") is True
    assert limiter.allow_request("user-a") is False


def test_different_keys_have_independent_buckets():
    clock = FakeClock()
    limiter = TokenBucketRateLimiter(capacity=1, refill_rate_per_second=1.0, now_fn=clock)

    assert limiter.allow_request("user-a") is True
    # user-a's single token is now exhausted.
    assert limiter.allow_request("user-a") is False

    # user-b has never been seen before and must start with a full bucket,
    # independent of user-a's state.
    assert limiter.allow_request("user-b") is True
    assert limiter.allow_request("user-b") is False


def test_fresh_key_starts_full_even_after_other_keys_are_exhausted():
    clock = FakeClock()
    limiter = TokenBucketRateLimiter(capacity=2, refill_rate_per_second=0.5, now_fn=clock)

    limiter.allow_request("user-a")
    limiter.allow_request("user-a")
    assert limiter.allow_request("user-a") is False

    clock.advance(100.0)

    # A brand-new key showing up later must still start at full capacity,
    # not be affected by any other key's history.
    assert limiter.allow_request("user-c") is True
    assert limiter.allow_request("user-c") is True
