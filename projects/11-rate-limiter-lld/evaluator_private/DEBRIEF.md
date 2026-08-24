# Interview Follow-Up Questions (private)

1. **Why did (or didn't) your Part 1 design need to change when you read
   the Part 2 requirements?**
   Strong answer: it didn't need to change, because `TokenBucketRateLimiter`
   only ever needed to correctly implement `RateLimiter.allow_request` —
   nothing about adding `FixedWindowRateLimiter` or `TieredRateLimiter`
   required it to expose anything new or behave differently. If the
   candidate *did* have to go back and change Part 1, ask specifically what
   had to change and why — a common honest answer is "I hadn't made the
   clock injection consistent" or "I exposed internal state that
   `TieredRateLimiter` ended up needing," which is itself useful signal
   about what to probe further.

2. **What would you need to add to make this safe under real concurrent
   access from multiple threads or multiple processes?** (Discussion only —
   not implemented in this exercise.)
   Strong answer: for multi-threaded single-process use, the read-refill-
   consume sequence in `TokenBucketRateLimiter.allow_request` needs to be
   atomic per key (e.g. a lock per key, or one lock guarding the whole
   bucket dict, being mindful of contention if the lock is coarse-grained).
   For multi-process/distributed use (the realistic gateway scenario), an
   in-memory dict per instance isn't sufficient at all — you'd need shared
   state in something like Redis, and the refill-then-consume logic would
   typically move into a Lua script or similar atomic server-side operation
   to avoid race conditions between concurrent gateway instances checking
   and decrementing the same key's budget.

3. **How would you extend this to support per-tier configuration loaded
   from a config file instead of constructed in code?**
   Strong answer: `TieredRateLimiter` already takes plain `RateLimiter`
   objects for `default` and each override, so a config loader's job is
   just to parse structured config (e.g. `{"strategy": "token_bucket",
   "capacity": 10, "refill_rate_per_second": 1.0}` per tier) into the
   appropriate constructed instances, then build the `overrides` dict from
   that. Bonus/strong signal: recognizing this could be a small factory
   function keyed on a `"strategy"` string field, kept entirely separate
   from `TieredRateLimiter` itself, which shouldn't need to know configs
   exist at all.

4. **Walk me through what happens, step by step, for a single call to
   `allow_request` on `TieredRateLimiter` when the key has no override
   configured.**
   Strong answer: look up the key in `overrides`; not found, so fall back
   to `default`; call `default.allow_request(key)` and return whatever it
   returns — `TieredRateLimiter` does not itself decide allow/deny, it only
   routes.

5. **Suppose `refill_rate_per_second` is 0 (a client tier explicitly
   configured with no refill). What should happen, and does your
   implementation handle it correctly?**
   Strong answer: the bucket never refills after its initial full capacity
   is exhausted — every subsequent request for that key should be denied
   forever (until the process restarts). Candidates should recognize this
   as a valid, if extreme, configuration rather than something to guard
   against or treat as an error, unless they've deliberately chosen to
   validate `refill_rate_per_second > 0` in their constructor — either
   choice is defensible as long as they can explain it.

6. **If you'd been told from the very start that a second strategy and
   runtime dispatch were coming, would you have designed Part 1 any
   differently?**
   Strong answer (self-critical, design-forward): probably not much
   differently for `TokenBucketRateLimiter` itself, since it was always
   going to be one implementation of the given interface — but it might
   have changed how much they front-loaded generality that turned out
   unnecessary (YAGNI point), or made them more deliberate about keeping
   the clock-injection pattern identical across strategies from the start
   so `TieredRateLimiter` didn't need any special-casing per strategy's
   constructor signature. A good answer resists over-engineering Part 1 in
   anticipation of a requirement that hadn't been stated yet.
