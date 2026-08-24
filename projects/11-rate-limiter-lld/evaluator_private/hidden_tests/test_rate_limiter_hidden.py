"""Hidden tests — Project 11 (Rate Limiter LLD).

Copy this file into candidate/tests/ before running `pytest -q` from
candidate/. Covers boundary/edge cases beyond the public tests, plus the
key design-quality check: TieredRateLimiter must depend only on the
RateLimiter interface, not on the concrete TokenBucketRateLimiter /
FixedWindowRateLimiter types.
"""

from ratelimiter import (
    FixedWindowRateLimiter,
    RateLimiter,
    TieredRateLimiter,
    TokenBucketRateLimiter,
)


class FakeClock:
    def __init__(self, start: float = 0.0):
        self._now = start

    def __call__(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds


# ---------------------------------------------------------------------------
# Token bucket boundary / fractional-refill edge cases
# ---------------------------------------------------------------------------


def test_token_bucket_partial_refill_below_one_token_grants_no_extra_allowance():
    clock = FakeClock()
    # refill_rate 1/sec -> 0.5s should add only half a token, not enough
    # to allow an extra request on top of an empty bucket.
    limiter = TokenBucketRateLimiter(capacity=1, refill_rate_per_second=1.0, now_fn=clock)

    assert limiter.allow_request("k") is True
    assert limiter.allow_request("k") is False

    clock.advance(0.5)
    assert limiter.allow_request("k") is False

    # The other half-second arrives later; fractional accumulation across
    # multiple calls should still add up correctly to a full token.
    clock.advance(0.5)
    assert limiter.allow_request("k") is True


def test_token_bucket_exact_boundary_allows_when_tokens_equal_one():
    clock = FakeClock()
    limiter = TokenBucketRateLimiter(capacity=5, refill_rate_per_second=2.0, now_fn=clock)

    for _ in range(5):
        assert limiter.allow_request("k") is True
    assert limiter.allow_request("k") is False

    # Exactly 0.5s at rate 2/sec refills exactly 1.0 token.
    clock.advance(0.5)
    assert limiter.allow_request("k") is True
    assert limiter.allow_request("k") is False


def test_token_bucket_no_elapsed_time_between_calls_is_stable():
    clock = FakeClock()
    limiter = TokenBucketRateLimiter(capacity=3, refill_rate_per_second=100.0, now_fn=clock)

    # Multiple calls at the exact same timestamp must not double-refill.
    assert limiter.allow_request("k") is True
    assert limiter.allow_request("k") is True
    assert limiter.allow_request("k") is True
    assert limiter.allow_request("k") is False


# ---------------------------------------------------------------------------
# Fixed window boundary case
# ---------------------------------------------------------------------------


def test_fixed_window_boundary_right_at_window_edge():
    clock = FakeClock()
    limiter = FixedWindowRateLimiter(max_requests=1, window_seconds=10.0, now_fn=clock)

    assert limiter.allow_request("k") is True
    assert limiter.allow_request("k") is False

    # One tick before the window rolls over: still the same window.
    clock.advance(9.999)
    assert limiter.allow_request("k") is False

    # Now at exactly t=10.0 (a fresh window, since window_index = 10 // 10 = 1
    # which differs from the first window's index 0).
    clock.advance(0.001)
    assert limiter.allow_request("k") is True
    assert limiter.allow_request("k") is False


def test_fixed_window_many_windows_pass_with_no_traffic():
    clock = FakeClock()
    limiter = FixedWindowRateLimiter(max_requests=2, window_seconds=5.0, now_fn=clock)

    limiter.allow_request("k")
    limiter.allow_request("k")
    assert limiter.allow_request("k") is False

    # Skip far ahead across many windows with no calls at all in between.
    clock.advance(500.0)
    assert limiter.allow_request("k") is True
    assert limiter.allow_request("k") is True
    assert limiter.allow_request("k") is False


# ---------------------------------------------------------------------------
# TieredRateLimiter must be purely polymorphic over RateLimiter
# ---------------------------------------------------------------------------


class AlwaysAllowLimiter(RateLimiter):
    """A trivial third RateLimiter implementation, unknown to TieredRateLimiter
    at write time. If TieredRateLimiter is implemented correctly (dispatching
    purely through the RateLimiter interface), this must work as an override
    or default with zero changes to any production class."""

    def allow_request(self, key: str) -> bool:
        return True


class AlwaysDenyLimiter(RateLimiter):
    """A second trivial custom RateLimiter, used to further confirm
    TieredRateLimiter never special-cases known concrete types."""

    def allow_request(self, key: str) -> bool:
        return False


class CountingLimiter(RateLimiter):
    """A third custom RateLimiter that allows exactly the first N calls for
    ANY key combined (deliberately not per-key, to prove TieredRateLimiter
    doesn't reimplement or peek into a limiter's internal counting logic —
    it must simply delegate)."""

    def __init__(self, allowance: int):
        self._remaining = allowance

    def allow_request(self, key: str) -> bool:
        if self._remaining > 0:
            self._remaining -= 1
            return True
        return False


def test_tiered_works_with_a_custom_third_party_limiter_as_override():
    default = TokenBucketRateLimiter(capacity=1, refill_rate_per_second=0.0, now_fn=lambda: 0.0)
    custom = AlwaysAllowLimiter()

    tiered = TieredRateLimiter(default=default, overrides={"custom-key": custom})

    # A candidate who branches on isinstance(limiter, TokenBucketRateLimiter)
    # / isinstance(limiter, FixedWindowRateLimiter) internally will not
    # recognize AlwaysAllowLimiter and will fail this test (e.g. by raising,
    # by silently falling through to the default, or by returning False).
    for _ in range(10):
        assert tiered.allow_request("custom-key") is True

    # The default limiter's own single token should still be independently
    # available/exhaustible, confirming the custom override didn't leak into
    # or replace the default's own state.
    assert tiered.allow_request("regular-key") is True
    assert tiered.allow_request("regular-key") is False


def test_tiered_works_with_a_custom_third_party_limiter_as_default():
    override = AlwaysDenyLimiter()
    default = AlwaysAllowLimiter()

    tiered = TieredRateLimiter(default=default, overrides={"blocked-key": override})

    assert tiered.allow_request("blocked-key") is False
    assert tiered.allow_request("blocked-key") is False
    assert tiered.allow_request("anything-else") is True
    assert tiered.allow_request("another-key") is True


def test_tiered_custom_limiter_state_is_genuinely_delegated_not_reimplemented():
    # CountingLimiter's allowance is shared across ALL keys routed to it
    # (by design, to prove real delegation) -- an isinstance-branching
    # TieredRateLimiter that doesn't know this type can't reproduce this
    # behavior at all, since it never calls into the object.
    custom = CountingLimiter(allowance=2)
    default = AlwaysDenyLimiter()

    tiered = TieredRateLimiter(default=default, overrides={"a": custom, "b": custom})

    assert tiered.allow_request("a") is True
    assert tiered.allow_request("b") is True
    # Allowance of 2 shared between "a" and "b" is now exhausted.
    assert tiered.allow_request("a") is False
    assert tiered.allow_request("b") is False


# ---------------------------------------------------------------------------
# Many keys across a TieredRateLimiter: no cross-key interference
# ---------------------------------------------------------------------------


def test_tiered_many_keys_do_not_interfere_with_each_other():
    clock = FakeClock()
    default = TokenBucketRateLimiter(capacity=2, refill_rate_per_second=1.0, now_fn=clock)
    override_x = FixedWindowRateLimiter(max_requests=3, window_seconds=10.0, now_fn=clock)
    override_y = TokenBucketRateLimiter(capacity=1, refill_rate_per_second=1.0, now_fn=clock)

    tiered = TieredRateLimiter(
        default=default,
        overrides={"tier-x": override_x, "tier-y": override_y},
    )

    keys = [f"default-{i}" for i in range(5)] + ["tier-x", "tier-y"]

    # Exhaust every default-tier key's 2-token budget independently.
    for key in [f"default-{i}" for i in range(5)]:
        assert tiered.allow_request(key) is True
        assert tiered.allow_request(key) is True
        assert tiered.allow_request(key) is False

    # tier-x (fixed window, capacity 3) is unaffected by the default-tier
    # keys being exhausted.
    assert tiered.allow_request("tier-x") is True
    assert tiered.allow_request("tier-x") is True
    assert tiered.allow_request("tier-x") is True
    assert tiered.allow_request("tier-x") is False

    # tier-y (its own token bucket, capacity 1) is likewise independent.
    assert tiered.allow_request("tier-y") is True
    assert tiered.allow_request("tier-y") is False

    # Advancing the clock refills every independent bucket/window correctly,
    # per its own strategy.
    clock.advance(1.0)
    for key in [f"default-{i}" for i in range(5)]:
        assert tiered.allow_request(key) is True
    assert tiered.allow_request("tier-y") is True
