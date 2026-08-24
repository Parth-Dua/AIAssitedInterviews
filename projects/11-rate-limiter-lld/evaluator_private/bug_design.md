# Design Brief (private — do not expose to candidate)

*(Filename kept as `bug_design.md` for structural consistency with the rest
of the curriculum's evaluator_private layout. This project has no injected
bug — its content is the private design brief for an LLD/implement-from-
requirements exercise.)*

## Full requirements (candidate-facing, restated here for evaluator reference)

**Given, fully implemented:** `RateLimiter` ABC with a single method,
`allow_request(key: str) -> bool`, which must track state per key
independently.

**Part 1 — `TokenBucketRateLimiter`:** each key gets an independent bucket
starting full at `capacity`. Each `allow_request` call refills based on
elapsed time (`refill_rate_per_second`, capped at `capacity`, fractional
tokens tracked internally), then consumes one token if available. Clock is
injectable via `now_fn`.

**Part 2 — `FixedWindowRateLimiter`:** allows up to `max_requests` per key
within a `window_seconds` window. We deliberately specify **fixed-window**
semantics (window index `int(now // window_seconds)`; count resets to 0
whenever the index changes), not sliding-window, and say so explicitly in
the candidate README — this removes the sliding-vs-fixed ambiguity as a
source of ungraded confusion and lets hidden tests assert exact counts at
exact boundaries. Clock injectable the same way.

**Part 2 — `TieredRateLimiter`:** takes a `default: RateLimiter` and
`overrides: dict[str, RateLimiter]`. Dispatches each key to its override if
present, else default. Must depend only on the `RateLimiter` interface.

## Why this is interview-appropriate

Rate limiters are one of the most common LLD interview questions at
mid-to-large tech companies (frequently asked as a 45-90 minute
system/object design exercise, sometimes as a pure coding exercise like
this one). The two-part structure — implement a first strategy, then reveal
a second requirement that tests whether the first design anticipated
change — mirrors how these interviews are actually run in practice
(interviewers commonly add "now support a second algorithm" or "now make it
configurable per client" as a follow-up once the first pass works). No
named design pattern (e.g. "Strategy") was suggested to the candidate
anywhere in the README, the SKILL.md, or any candidate-facing file — the
interface (`RateLimiter` with one abstract method) makes the appropriate
shape discoverable through the requirements themselves, without pre-labeling
it. A candidate who has independently learned this pattern will recognize
it; a candidate who hasn't can still arrive at a correct design by directly
satisfying the stated requirements ("`TieredRateLimiter` must work with any
`RateLimiter` implementation, without calling code needing to know which
strategy is in use").

## Design pitfall #1 (hidden-test-enforced): isinstance-branching in
`TieredRateLimiter`

**The temptation:** a candidate implements `TieredRateLimiter.allow_request`
as something like:

```python
def allow_request(self, key):
    limiter = self._overrides.get(key, self._default)
    if isinstance(limiter, TokenBucketRateLimiter):
        return limiter.allow_request(key)
    elif isinstance(limiter, FixedWindowRateLimiter):
        return limiter.allow_request(key)
    else:
        raise TypeError(...)  # or silently falls through to default
```

This *works* for every public test and passes most hidden tests, because
the exercise only ever hands `TieredRateLimiter` the two concrete strategies
it was written against. It violates the entire point of depending on the
`RateLimiter` interface: adding a third strategy later would require going
back and modifying `TieredRateLimiter` again, which is exactly the coupling
the Part 2 requirement ("without any calling code needing to know which
strategy is in use for a given key") was written to rule out.

**Exactly which hidden tests catch it:** `hidden_tests/test_rate_limiter_hidden.py`
defines three tiny custom `RateLimiter` subclasses inline
(`AlwaysAllowLimiter`, `AlwaysDenyLimiter`, `CountingLimiter`) — each just a
few lines implementing `allow_request` directly, with zero knowledge of
`TokenBucketRateLimiter`/`FixedWindowRateLimiter` and vice versa — and uses
them as `TieredRateLimiter` overrides/defaults in:

- `test_tiered_works_with_a_custom_third_party_limiter_as_override`
- `test_tiered_works_with_a_custom_third_party_limiter_as_default`
- `test_tiered_custom_limiter_state_is_genuinely_delegated_not_reimplemented`

A correct, purely-polymorphic `TieredRateLimiter` (i.e. `limiter =
self._overrides.get(key, self._default); return limiter.allow_request(key)`)
passes all three trivially. An isinstance-branching implementation fails all
three — verified directly (see Validation section of the build brief / the
final report): it raises `TypeError` on the unrecognized custom type in each
case, while every public test and every other hidden test still passes. This
is the intended, precise signal: the isinstance version is "correct" by
every test that only exercises the two known strategies, and wrong only by
the test built to catch exactly this shortcut.

## Design pitfall #2 (rubric/DEBRIEF signal only, not hidden-test-enforced)

A candidate's `TokenBucketRateLimiter` internal per-key state design can be
low quality in ways the given tests don't directly penalize, e.g.:

- Storing per-key state as a raw `dict[str, tuple[float, float]]` (tokens,
  timestamp) and mutating tuples via reassignment scattered across the
  method, instead of a small internal state object/dataclass — works, but
  is harder to extend (e.g. if a future requirement needed to also track
  "last denied at" per key).
- Leaking the internal bucket dict itself (e.g. exposing `self.buckets` as
  a public attribute, or a method that returns the raw internal mapping)
  rather than keeping it a private implementation detail behind
  `allow_request`.
- Recomputing "now" multiple times per call via separate `now_fn()` calls
  in ways that could observe different values within a single logical
  operation (minor correctness smell, worth a quick question in DEBRIEF
  even though the fake clock in tests won't necessarily catch it since it's
  synchronous and single-threaded).

This is intentionally *not* hidden-test-enforced — it's a code-quality
signal, not a correctness one — but reviewers should look for it and it's
called out explicitly in `scoring_rubric.md` (code quality / responsibility
assignment) and as a `DEBRIEF.md` discussion point.

## Relevant files
- `candidate/ratelimiter/base.py` — given, correct, not graded directly.
- `candidate/ratelimiter/token_bucket.py`, `fixed_window.py`, `tiered.py` —
  the three graded classes.
- `evaluator_private/reference_solution/ratelimiter/` — full working
  reference implementation of all three classes.
- `evaluator_private/hidden_tests/test_rate_limiter_hidden.py` — hidden
  tests described above.
