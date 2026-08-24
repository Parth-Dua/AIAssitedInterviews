# Scoring Rubric — Project 6 (100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the route → service → cache/repository flow; noticed `get_preferences` is a correct read-through cache and `update_preferences` never touches the cache, before editing. |
| Debugging process | 10 | Reproduced the stale-cache bug via the failing test (or equivalent manual repro: GET, PUT, GET) before making changes; didn't shotgun-edit across files. |
| Root-cause reasoning | 15 | Correctly identifies that the write path never invalidates or updates the cache entry, and can articulate the general invariant violated ("the cache must never diverge from the repository after a write"). |
| Bug-fix correctness | 15 | Public stale-read test passes; the write path either deletes the cache entry or repopulates it with the *persisted* value (not the raw request); sequential-PUTs hidden test passes (invalidation isn't a one-shot fix scoped to a single call site). |
| Feature/TTL implementation quality | 20 | `Cache.set` accepts `ttl_seconds`; `Cache.get` treats an expired entry as a miss and evicts it; uses the injectable `now_fn` clock (no real sleeps anywhere, including in the candidate's own tests); read-through path populates the cache with a sensible default TTL; boundary convention is consistent and the candidate can state which one they chose. |
| Tests added | 10 | Added at least one regression test beyond the given failing ones — ideally one exercising the write-then-read cycle with the normalization rule active (all channels disabled), since that's the only kind of test that would have caught the "cache the request body" mistake, plus a TTL-expiry test using a fake/controllable clock. |
| Scope discipline | 5 | Did not modify the response schema, repository normalization rule, unrelated endpoints, or add a real Redis/database dependency; changes stayed within `cache.py` and the service (plus the route only if a default-TTL constant or similar was added there instead). |
| Communication | 15 | Can clearly state: the stale-cache bug's root cause and why the fix is correct; why caching the request body instead of the persisted value is risky in general, not just for this normalization rule; why the clock needed to be injectable rather than using real sleeps; what they checked to confirm both the fix and the feature work together. |

**Passing bar (strong intern/new-grad signal):** ≥75, all hidden tests
pass, and the candidate can explain both the cache-invalidation root
cause and the request-vs-persisted-value distinction without prompting.

**Red flags:**
- Fix passes the public `test_put_then_immediate_get_returns_new_values`
  test but fails
  `test_put_disable_all_channels_get_returns_persisted_not_request_body`
  (the "cache the request body instead of what was persisted" incomplete
  fix — see `bug_design.md`).
- Candidate fixes the stale-cache bug but never implements TTL, or vice
  versa — this exercise has two deliverables and both are graded.
- Candidate's TTL tests use real `time.sleep()` calls (even short ones)
  instead of a fake/injectable clock — a correctness smell (flaky,
  slow) and a sign they didn't notice or use the `now_fn` parameter
  already present on `Cache.__init__`.
- Candidate "fixes" the bug by disabling caching for `PUT` responses only
  (e.g. never caching after a write) while leaving `GET`'s read-through
  cache untouched — this happens to pass the given test but doesn't
  address that a *previously cached* entry from before the write is still
  stale; verify with the sequential-PUTs hidden test.
- Candidate adds a hardcoded per-user or global cache-clear/"flush
  everything" call on every write instead of invalidating the specific
  key — works but doesn't scale and suggests they didn't reason about why
  the read path uses a per-user key in the first place.
- Candidate cannot explain *why* either the fix or the TTL design is
  correct, only that changing X made a test pass.
