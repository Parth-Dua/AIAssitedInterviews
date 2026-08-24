"""Part 2 public tests for FixedWindowRateLimiter and TieredRateLimiter.

Only start on these once Part 1 (test_token_bucket.py) is fully passing —
see the README.
"""

from ratelimiter import FixedWindowRateLimiter, TieredRateLimiter, TokenBucketRateLimiter


class FakeClock:
    """A controllable stand-in for time.monotonic()."""

    def __init__(self, start: float = 0.0):
        self._now = start

    def __call__(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds


# ---------------------------------------------------------------------------
# FixedWindowRateLimiter
# ---------------------------------------------------------------------------


def test_fixed_window_allows_up_to_max_requests_within_window():
    clock = FakeClock()
    limiter = FixedWindowRateLimiter(max_requests=3, window_seconds=10.0, now_fn=clock)

    assert limiter.allow_request("user-a") is True
    assert limiter.allow_request("user-a") is True
    assert limiter.allow_request("user-a") is True
    assert limiter.allow_request("user-a") is False


def test_fixed_window_resets_on_window_rollover():
    clock = FakeClock()
    limiter = FixedWindowRateLimiter(max_requests=2, window_seconds=10.0, now_fn=clock)

    assert limiter.allow_request("user-a") is True
    assert limiter.allow_request("user-a") is True
    assert limiter.allow_request("user-a") is False

    # Move into the next window entirely.
    clock.advance(10.0)

    assert limiter.allow_request("user-a") is True
    assert limiter.allow_request("user-a") is True
    assert limiter.allow_request("user-a") is False


def test_fixed_window_tracks_keys_independently():
    clock = FakeClock()
    limiter = FixedWindowRateLimiter(max_requests=1, window_seconds=5.0, now_fn=clock)

    assert limiter.allow_request("user-a") is True
    assert limiter.allow_request("user-a") is False

    assert limiter.allow_request("user-b") is True
    assert limiter.allow_request("user-b") is False


# ---------------------------------------------------------------------------
# TieredRateLimiter
# ---------------------------------------------------------------------------


def test_tiered_uses_override_for_specific_key_and_default_otherwise():
    clock = FakeClock()
    default = TokenBucketRateLimiter(capacity=1, refill_rate_per_second=1.0, now_fn=clock)
    vip = TokenBucketRateLimiter(capacity=5, refill_rate_per_second=1.0, now_fn=clock)

    tiered = TieredRateLimiter(default=default, overrides={"vip-user": vip})

    # Non-override key follows the default (capacity 1).
    assert tiered.allow_request("regular-user") is True
    assert tiered.allow_request("regular-user") is False

    # Override key follows its own strategy (capacity 5), unaffected by the
    # default limiter's state.
    for _ in range(5):
        assert tiered.allow_request("vip-user") is True
    assert tiered.allow_request("vip-user") is False


def test_tiered_keys_under_different_strategies_are_independent():
    clock = FakeClock()
    default = FixedWindowRateLimiter(max_requests=2, window_seconds=10.0, now_fn=clock)
    override = TokenBucketRateLimiter(capacity=1, refill_rate_per_second=0.1, now_fn=clock)

    tiered = TieredRateLimiter(default=default, overrides={"limited-user": override})

    # "limited-user" follows the token-bucket override.
    assert tiered.allow_request("limited-user") is True
    assert tiered.allow_request("limited-user") is False

    # A different key still gets the fixed-window default, with its own
    # independent budget.
    assert tiered.allow_request("other-user") is True
    assert tiered.allow_request("other-user") is True
    assert tiered.allow_request("other-user") is False
