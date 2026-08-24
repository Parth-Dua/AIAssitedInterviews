# Rate Limiter Library (Interview Exercise)

**Format:** Low-Level Design + Implementation
**Timebox:** 60–90 minutes
**Level:** Backend / SWE — Difficulty 7/10

## Scenario

You're building a rate-limiting library for an internal API gateway.
Different client tiers need different limiting behavior, and the gateway
team wants a clean library they can extend later without rewriting existing
code.

The public interface you're building against is already given to you, fully
implemented, in `ratelimiter/base.py`:

```python
class RateLimiter(ABC):
    @abstractmethod
    def allow_request(self, key: str) -> bool:
        """Return True if a request identified by `key` should be allowed
        right now (and record/consume whatever capacity that implies),
        False if it should be rejected. Calls for different keys must be
        tracked independently."""
```

Everything you write should work in terms of this interface.

## Part 1 — Token Bucket

Implement `TokenBucketRateLimiter` in `ratelimiter/token_bucket.py`. The
class shape is already stubbed out:

```python
class TokenBucketRateLimiter(RateLimiter):
    def __init__(self, capacity: int, refill_rate_per_second: float,
                 now_fn: Callable[[], float] = time.monotonic):
        ...

    def allow_request(self, key: str) -> bool:
        ...
```

Requirements:

- Each distinct `key` gets its own **independent** bucket. A bucket you've
  never seen before starts **full**, i.e. at `capacity` tokens.
- Each call to `allow_request(key)` should, in order:
  1. Refill that key's bucket based on how much time has elapsed since it
     was last touched, at `refill_rate_per_second` tokens per second, capped
     so the bucket never holds more than `capacity` tokens. Fractional
     tokens are fine to track internally (don't round early).
  2. If at least one token is available, consume exactly one token and
     return `True`.
  3. Otherwise, consume nothing and return `False`.
- The clock must be **injectable** via `now_fn`. Your implementation should
  call `now_fn()` to get the current time rather than calling
  `time.monotonic()` directly — this is what lets tests control time
  deterministically. Don't use real `time.sleep()` anywhere, including in
  any tests you add.

Run `pytest -q tests/test_token_bucket.py` until it's green before moving
on to Part 2.

## Part 2 — Follow-Up

**Read this section only after Part 1 is implemented and its tests pass.**
In a real interview, requirements often get extended after your initial
design is in place — this section is exactly that.

> The gateway also needs to support a second, simpler strategy — a
> fixed-window counter — for a lower-tier customer plan, and needs to apply
> different strategies to different API keys at runtime, without any
> calling code needing to know which strategy is in use for a given key.

Implement two more classes, both already stubbed out for you:

### `FixedWindowRateLimiter` (`ratelimiter/fixed_window.py`)

```python
class FixedWindowRateLimiter(RateLimiter):
    def __init__(self, max_requests: int, window_seconds: float,
                 now_fn: Callable[[], float] = time.monotonic):
        ...

    def allow_request(self, key: str) -> bool:
        ...
```

Allows up to `max_requests` for a given key within a window of
`window_seconds`. Use a **fixed** window, not a sliding one: the counter for
a key resets whenever a new window starts (e.g. bucket time into windows of
index `int(now // window_seconds)`; a new index means a fresh count of 0 for
that key). The clock is injectable the same way as Part 1.

### `TieredRateLimiter` (`ratelimiter/tiered.py`)

```python
class TieredRateLimiter(RateLimiter):
    def __init__(self, default: RateLimiter, overrides: dict[str, RateLimiter] | None = None):
        ...

    def allow_request(self, key: str) -> bool:
        ...
```

Dispatches each `key` to `overrides[key]` if one is configured for that key,
otherwise to `default`. It must work with **any** `RateLimiter`
implementation passed in for `default` or in `overrides` — including ones
that don't exist yet. Don't write `TieredRateLimiter` in a way that assumes
its collaborators are specifically `TokenBucketRateLimiter` or
`FixedWindowRateLimiter`; it should only ever call the `RateLimiter`
interface it's given.

Run `pytest -q tests/test_fixed_window_and_tiered.py` until it's green.

When you're done, think about whether finishing Part 2 required you to go
back and change anything in `token_bucket.py`. You should be able to explain
why it did or didn't.

## Repository layout

```
ratelimiter/
  base.py            RateLimiter interface (given, do not modify)
  token_bucket.py     TokenBucketRateLimiter — Part 1, implement this
  fixed_window.py      FixedWindowRateLimiter — Part 2, implement this
  tiered.py             TieredRateLimiter — Part 2, implement this
api/
  main.py            Optional thin FastAPI wrapper — not required reading,
                      contains no graded logic
tests/
  test_token_bucket.py                Part 1 public tests
  test_fixed_window_and_tiered.py     Part 2 public tests
```

## Setup

```bash
pip install -e ".[dev]"
```

The `ratelimiter` package itself has **zero dependencies** — everything you
need to implement is plain Python. (The optional `api` extra pulls in
FastAPI/Pydantic only if you want to poke at the demo wrapper in `api/`; it
is not required for this exercise.)

## Running tests

```bash
pytest -q
```

All tests currently fail with `NotImplementedError` — that's expected,
nothing is implemented yet. Part 1 and Part 2 tests are in separate files so
you can run just the section you're working on, e.g.:

```bash
pytest -q tests/test_token_bucket.py
```

## Constraints

- Implement against the given `RateLimiter` interface in `base.py` — don't
  change it.
- Keep the clock injectable (`now_fn`) in both `TokenBucketRateLimiter` and
  `FixedWindowRateLimiter`. Don't call `time.monotonic()`/`time.time()`
  directly inside your logic — call `self._now_fn()` (or however you store
  it).
- No real sleeping (`time.sleep`) anywhere, including in any tests you add —
  use a fake/controllable clock instead, the same way the given tests do.
- Beyond the given class shapes and the `RateLimiter` interface, the
  internal design is yours: you may add private helper methods, private
  state, or small internal data structures freely.

## AI tool policy

You may use an AI coding assistant. If you'd like it to behave the way a
real interview/OA proctor would configure it, load
`.ai/assessment-skill/SKILL.md` into your assistant as a system/project
instruction. It's written to work with any capable coding assistant, not
a specific product.

Using an assistant well is part of what's being evaluated — treat it like
a knowledgeable but junior pair programmer, not an oracle. It can help you
reason through your class design and talk through tradeoffs, but the actual
implementation and the design decisions behind it need to be yours.

## Deliverables

- Your implementation of all three classes.
- Any tests you added.
- Be ready to explain: your class design, what invariants each class
  maintains, and why Part 2 did or didn't require changing your Part 1 code.
