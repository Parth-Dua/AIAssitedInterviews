# Expected Design Reasoning — Project 11

*(Repurposed for an LLD project: this describes what a good class design
looks like and why, rather than a root-cause reasoning path through an
injected bug.)*

## What each class should own

- **`TokenBucketRateLimiter`** owns, per key: a token count (float, to allow
  fractional accumulation) and a "last touched" timestamp. It should not
  need to know anything about `FixedWindowRateLimiter` or
  `TieredRateLimiter`, and vice versa. A clean implementation stores this as
  a small private mapping from key to a tiny state object (a dataclass or
  even a 2-tuple), keeps that mapping as a private attribute, and never
  exposes it directly.

- **`FixedWindowRateLimiter`** owns, per key: a window index and a count
  within that window. The window index is derived purely from the current
  time and `window_seconds` (`int(now // window_seconds)`) — it does not
  need to store window *start times*, just the index, which makes rollover
  detection a single equality check.

- **`TieredRateLimiter`** owns no rate-limiting state of its own at all — it
  owns exactly one thing: a `default: RateLimiter` and a `dict[str,
  RateLimiter]` of overrides, and its only job is picking which one to
  delegate to for a given key. This is the crux of the exercise: if
  `TieredRateLimiter` needs to know anything about *how* a `RateLimiter`
  decides to allow or deny a request, the design has leaked a
  responsibility that belongs entirely inside each strategy.

## Why the clock should be injectable

Any time-based rate limiter is fundamentally difficult to test without
either (a) real sleeping, which makes tests slow and flaky, or (b) an
injectable clock, which makes tests instant and deterministic. A candidate
who reaches for `now_fn` (or equivalent) without being told exactly how to
wire it — the skeleton gives the parameter, but not the internal plumbing —
is demonstrating the same testability instinct interviewers look for when
they ask "how would you test this?" in a live LLD interview. The strongest
signal here is not just that `now_fn` exists as a parameter (it's given),
but that the candidate's every internal time read goes through it — no
stray `time.monotonic()` call anywhere in the method bodies.

## Why `TieredRateLimiter` should only depend on the abstract interface

The Part 2 requirement is explicit: "without any calling code needing to
know which strategy is in use for a given key." This is a direct,
practical restatement of depending on an abstraction rather than a
concretion. A candidate does not need to know the name of any formal
design pattern to arrive at the right shape here — they only need to take
the requirement at face value: `TieredRateLimiter` receives objects that
are typed as `RateLimiter` and should therefore only ever call
`RateLimiter`'s one method on them. The moment a candidate writes
`isinstance(limiter, TokenBucketRateLimiter)` inside `TieredRateLimiter`,
they've silently added a hidden coupling: `TieredRateLimiter` can now only
be used with a fixed, closed set of strategy classes it knows about by
name, which is precisely the situation the requirement was written to rule
out (a gateway team that wants to add a third strategy later without
touching existing code).

## Expected implementation path

1. Read `base.py` — a one-method ABC, `allow_request(key) -> bool`.
2. Implement `TokenBucketRateLimiter`: per-key lazy-initialized state
   (bucket starts full on first sight of a key), refill-then-consume order
   inside `allow_request`, refill capped at `capacity`.
3. Run `pytest -q tests/test_token_bucket.py`, get it green, including the
   fractional-refill and multi-key independence tests.
4. Read the Part 2 section. Implement `FixedWindowRateLimiter` similarly
   (per-key lazy state, window index derived from `now // window_seconds`).
5. Implement `TieredRateLimiter` as a pure dispatcher: look up
   `overrides.get(key, default)`, call `.allow_request(key)` on whatever
   comes back, return the result. No type inspection of the collaborator.
6. Run `pytest -q tests/test_fixed_window_and_tiered.py`, get it green.
7. Reflect (unprompted, or when asked in the debrief): Part 1's
   `TokenBucketRateLimiter` required zero changes to support Part 2,
   because `TieredRateLimiter` only ever calls the interface it was
   written against — the two strategies are fully decoupled from the
   dispatcher and from each other.

A strong candidate reaches a fully passing, polymorphic implementation of
all three classes within 45-60 minutes, with 15-30 minutes left to add
tests and articulate the design reasoning above.
