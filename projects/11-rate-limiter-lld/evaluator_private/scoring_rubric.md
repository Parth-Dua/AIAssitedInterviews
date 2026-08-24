# Scoring Rubric — Project 11: Rate Limiter LLD (100 points)

| Category | Points | Notes |
|---|---|---|
| Public API / interface design | 15 | Implementations depend only on `RateLimiter.allow_request`; constructors match the given signatures; clock is genuinely injectable (`now_fn` is called, not `time.monotonic()` hardcoded internally); per-key state is encapsulated, not leaked as a public attribute. |
| Part 1 correctness (`TokenBucketRateLimiter`) | 20 | Bucket starts full per key; refill is proportional to elapsed time and capped at capacity; fractional tokens accumulate correctly across multiple calls; independent keys don't interfere; boundary/fractional-refill hidden tests pass. |
| Part 2 correctness (`FixedWindowRateLimiter` + `TieredRateLimiter`) | 15 | Fixed-window semantics correctly reset on window rollover (not sliding); `TieredRateLimiter` correctly dispatches override vs. default per key; independent keys under different strategies behave correctly; boundary hidden tests pass. |
| Extensibility — did Part 2 require rewriting Part 1? | 15 | The core question: does `TieredRateLimiter.allow_request` call `limiter.allow_request(key)` polymorphically, or does it branch on `isinstance(limiter, TokenBucketRateLimiter)` / `FixedWindowRateLimiter`? The isinstance-branching hidden tests (see `bug_design.md`) are the objective check; also check whether the candidate had to go back and change `token_bucket.py` for Part 2 to work (they shouldn't have needed to) — ask directly in the debrief if not obvious from the diff/timeline. |
| Code quality / responsibility assignment | 10 | Each class owns only its own state; no shared mutable state leaked between classes; reasonable private helper structure; see `bug_design.md` pitfall #2 for the token-bucket internal-state quality signal. |
| Tests added | 10 | Candidate added at least one test beyond the given public ones — a boundary case, an additional custom `RateLimiter` implementation, a multi-key scenario, etc. |
| Communication / design explanation | 15 | Can clearly state: what state each class owns, why the clock is injectable, why `TieredRateLimiter` only depends on the abstract interface (or, if it doesn't, why they made that tradeoff), and whether/why Part 2 required touching Part 1 code. |

**Passing bar (strong backend signal):** ≥75, all public tests pass, and the
isinstance-branching hidden tests specifically pass (i.e. `TieredRateLimiter`
is genuinely polymorphic) — a candidate who ships a correct Part 1 and Part 2
but built `TieredRateLimiter` via isinstance-branching should not clear the
Extensibility category and should be capped well below the passing bar
regardless of how clean the rest of the code is, since the whole point of
Part 2 is testing exactly this.

**Red flags:**
- `TieredRateLimiter` uses `isinstance()` against
  `TokenBucketRateLimiter`/`FixedWindowRateLimiter` (or a `type()` check, or
  a string tag like `strategy_name`) instead of calling the interface
  polymorphically — fails the design-pitfall hidden tests even if every
  public test passes.
- Candidate mutates `capacity`/`refill_rate_per_second` on an existing
  `TokenBucketRateLimiter` instance to "reuse" it for a different tier
  instead of composing via `TieredRateLimiter`.
- No real fake-clock discipline — candidate's own added tests use
  `time.sleep()`, defeating the point of the injectable clock.
- Candidate cannot explain why the clock needed to be injectable, or treats
  it as an incidental implementation detail rather than a deliberate
  testability decision.
- Part 1 passes but required a rewrite once Part 2 requirements were read
  (e.g. had to change `TokenBucketRateLimiter`'s constructor or internal
  data shape to make `TieredRateLimiter` work) — acceptable to note but
  should cost points in Extensibility, and is worth discussing in the
  debrief regardless of the final diff.
