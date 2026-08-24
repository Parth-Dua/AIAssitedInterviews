# Bug + Feature Design (private — do not expose to candidate)

This project bundles a debugging task and a feature-implementation task
that share the same code path, so they're documented together.

## Part A — The stale cache bug

### Expected behavior
The cache must never diverge from the underlying repository after a write
completes. Concretely: `PUT /users/{user_id}/notification-preferences`
persists the new preferences to the repository *and* ensures the cache no
longer serves the pre-update value — a subsequent `GET` must reflect the
values that were just written.

### Actual (buggy) behavior
`app/services/notification_prefs_service.py::NotificationPreferencesService.update_preferences`
writes the new preferences to the repository (correct) but never touches
the cache — no `cache.delete(...)`, no `cache.set(...)` with the new
value. Because the starting `Cache` class has no TTL yet, a stale entry
that was already cached before the write lives in the cache forever (or
until some other event evicts it), so `GET` keeps returning the old value
indefinitely after a successful `PUT`.

### Root cause
Classic cache-invalidation-on-write bug: the read path
(`get_preferences`) is a correct read-through cache (check cache → on
miss, read repository → populate cache), but the write path was written
without symmetry — it updates the source of truth and stops, forgetting
the cache exists.

### Violated invariant
"The cache must never diverge from the underlying repository after a
write completes." Implied by the bug report (settings page shows the old
value right after saving) and by the basic contract of any cache sitting
in front of a source of truth.

### Relevant execution path
`GET`/`PUT /users/{user_id}/notification-preferences`
(`app/api/routes/notification_prefs.py`, thin pass-through for both
verbs) → `NotificationPreferencesService` (both `get_preferences` and
`update_preferences` live in the same class,
`app/services/notification_prefs_service.py`) → `Cache`
(`app/cache/cache.py`) and `NotificationPreferencesRepository`
(`app/repositories/notification_prefs_repository.py`). The candidate must
read both handlers in the service to notice the asymmetry: `get_preferences`
touches the cache on every path; `update_preferences` never does.

### Evidence available to the candidate
- The public test `test_put_then_immediate_get_returns_new_values`
  reproduces the exact reported scenario deterministically (no timing
  flakiness needed, since without a TTL a stale entry never expires on its
  own).
- Reading `get_preferences` shows the cache is populated on every miss.
- Reading `update_preferences` immediately below it shows it calls
  `self._repository.save(...)` and returns — no reference to `self._cache`
  anywhere in the method.

### Reasonable hypotheses
1. (Correct) `update_preferences` never invalidates or updates the cache
   entry for the user it just wrote.
2. (Plausible, wrong) Maybe the repository write itself is failing
   silently (e.g. writing to the wrong key, or a copy instead of the
   stored object). Ruled out by inspecting `update_preferences` return
   value directly (bypassing the cache) or by reading
   `NotificationPreferencesRepository.save`, which is a one-line dict
   assignment — the repository is unconditionally and correctly updated;
   only the *cache* is stale, not the underlying data.
3. (Plausible, wrong) Maybe Pydantic model equality/identity is confusing
   the cache (e.g. the cache is comparing objects and somehow returning a
   copy). Ruled out because the cache is a plain `dict.get`/`dict[key] =
   value` — there's no comparison logic in `Cache` at all in the starting
   code; the cache simply is never asked to update or forget this key.

### Intended regression test
`test_put_then_immediate_get_returns_new_values` (already present as a
public test) plus the hidden `test_multiple_sequential_puts_each_invalidate_cache`
(catches a fix that only invalidates once, e.g. hardcoded to a specific
call site or accidentally scoped to first-write-only).

### Acceptable fixes
- `cache.delete(key)` at the end of `update_preferences` (or before
  returning), so the next `get_preferences` call repopulates from the
  repository.
- Equivalent: `cache.set(key, saved, ttl_seconds=...)` — i.e. actively
  write the *actually persisted* value (`saved`, the repository's return
  value) into the cache with a fresh TTL, instead of deleting. This is
  fine as long as the value written is what was persisted, not the raw
  request body (see the trap below).
- Either fix must use the same cache key format (`f"prefs:{user_id}"`) the
  read path uses — a fix that invalidates a differently-formatted key is a
  no-op bug in disguise and should be caught by
  `test_put_then_immediate_get_returns_new_values` regardless.

### Tempting but incomplete/wrong fix
Adding cache invalidation on write, but doing it via `cache.set(key,
new_value)` where `new_value` is built directly from the *request body*
(pre-normalization) rather than from `saved` (the repository's return
value, post-normalization). This looks like a complete, even slightly
more efficient fix (it avoids the extra repository round-trip on the next
`GET`) and passes every public test, including the basic PUT-then-GET
test, because for most inputs the request body and the persisted value
are identical.

It diverges from the actually-persisted value only when the server-side
normalization rule fires: the product rule "a user must keep at least one
channel enabled" forces `email_enabled` back to `True` when a request
tries to disable all three channels. A candidate who caches the raw
request body caches `email_enabled=False` while the repository holds
`email_enabled=True` — so a `GET` right after this "fixed" `PUT` returns a
value that doesn't match what's actually in the repository, silently
reintroducing a cache/repository divergence bug of a different shape than
the one that was reported.

**Caught by:**
`hidden_tests/test_notification_prefs_hidden.py::test_put_disable_all_channels_get_returns_persisted_not_request_body`
— PUTs a request disabling all three channels, then immediately GETs, and
asserts the returned preferences match what was actually persisted (email
forced back on). Validated in a temporary copy of the candidate repo: 18
passed, 1 failed — the failure is exactly this test; every public test
(including the normalization-only
`test_disabling_all_channels_forces_email_back_on`, which checks the PUT
response only, not a subsequent GET) and every other hidden test passed.

### Acceptable variants for the fixed write path
- Delete-then-let-next-read-repopulate (simplest, recommended).
- Set the cache directly with `saved` (the repository's return value),
  never with the raw request/update object.
- Not acceptable: caching anything derived from `update` (the incoming
  `NotificationPreferencesUpdate`) instead of from `saved` or the
  repository.

---

## Part B — The TTL feature

### Requested behavior
Cache entries support an optional TTL (time-to-live), in seconds.
`Cache.set(key, value, ttl_seconds=...)` records an expiry; `Cache.get(key)`
must treat an entry whose TTL has elapsed as a miss and evict it at that
point, rather than ever returning stale data past its TTL. The read-through
path (`get_preferences`) should populate the cache with a sensible default
TTL (e.g. 60 seconds) so that even if some future write path forgets to
invalidate the cache (defense in depth against a regression of Part A),
staleness is bounded.

### Starting (incomplete) state
`Cache.__init__` already accepts an injectable `now_fn` clock (defaulting
to `time.monotonic`), so the clock-injection design decision is already
made for the candidate — they don't need to redesign that part, just use
it. `Cache.set` and `Cache.get` have no TTL logic at all yet: `set` takes
only `(key, value)`, and `get` is a plain `dict.get`. A `# TODO` comment
in the class docstring names the missing feature but not its
implementation. This mirrors a realistic "clock injection was set up for
this, then the person got pulled onto something else" partially-built
state.

### Correct design
- `set(key, value, ttl_seconds=None)`: when `ttl_seconds` is given, record
  `expires_at = now() + ttl_seconds` for that key; when omitted (or
  `None`), the entry has no expiry (matches existing no-TTL callers, if
  any remain).
- `get(key)`: if the key has an `expires_at` and `now() >= expires_at`,
  treat it as a miss — evict the key from both the value store and the
  expiry map, then return `None` — rather than returning the stale value.
- Boundary convention (documented, tested, either convention is
  acceptable as long as the candidate is consistent and states it): this
  reference solution treats the entry as expired at `now() >=
  expires_at`, i.e. exactly at the `ttl_seconds` mark counts as expired,
  not one instant later. A candidate who instead uses strict `>` (expires
  one instant *after* the TTL mark) is also acceptable — grade the
  candidate's own stated convention for consistency, not against this
  exact boundary, but do check `hidden_tests/test_notification_prefs_hidden.py::test_cache_ttl_boundary_exactly_at_ttl_is_expired`
  and adjust your read if they chose the other convention deliberately
  and documented it.
- The read-through path (`get_preferences`) should call
  `self._cache.set(key, preferences, ttl_seconds=<some default>)`
  instead of the current bare `self._cache.set(key, preferences)`.

### Tempting but incomplete/wrong implementation
Implementing TTL expiry checking *only* inside `get()`, using data
recorded correctly by `set()` — this part is usually done fine by
candidates. The place candidates more often go wrong is the *boundary
math* itself: computing `expires_at = now() - ttl_seconds` (sign flip) or
comparing `now() > expires_at + ttl_seconds` (double-counting the TTL) —
either mistake makes entries expire immediately or never expire at all,
which is caught immediately by the public
`test_cache_entries_expire_after_ttl` test once the `TypeError` from the
missing parameter is fixed, so it's unlikely to reach hidden-test review
undetected. The more interesting/valid case worth probing in the
interview is the boundary convention itself (`>` vs `>=`) — see the two
hidden boundary tests, which pin down `>=` (inclusive) as this reference
solution's choice; ask the candidate to state and justify theirs.

### Acceptable implementations
- The reference `Cache` above (dict of values + parallel dict of expiry
  timestamps).
- Equivalent: store `(value, expires_at)` tuples in a single dict instead
  of two parallel dicts — same behavior, different data layout.
- Not acceptable: a fix that requires real `time.sleep()` in tests to
  verify, or that hardcodes `time.monotonic` directly inside `Cache`
  without going through the injectable `now_fn` (breaks deterministic
  testing, which the starting code and README both call out as a
  requirement).

### Validation performed
The reference `Cache` (`reference_solution/cache.py`) and reference
service (`reference_solution/notification_prefs_service.py`) were applied
to a temporary copy of the candidate repository, hidden tests were copied
into `tests/`, and `pytest -q` was run: **19 passed** (14 public + 5
hidden). Separately, the tempting-but-incomplete "cache the request body"
service variant (bug fix present, TTL correctly implemented, but the
write path caches `update` instead of `saved`) was applied the same way:
**18 passed, 1 failed** — the failure was exactly
`test_put_disable_all_channels_get_returns_persisted_not_request_body`;
all 14 public tests and all 4 other hidden tests passed. The original,
untouched candidate starting state was re-verified afterward: **12
passed, 2 failed** (`test_put_then_immediate_get_returns_new_values` and
`test_cache_entries_expire_after_ttl`), confirming the intended pass/fail
split.

## Why this is interview-appropriate
Cache-invalidation-on-write bugs ("the two hardest things in computer
science...") are one of the most common real-world backend bug shapes,
and pairing one with "now add a TTL as defense in depth" is exactly the
kind of natural follow-up a real team would ask for once the root cause
is understood. No specialist caching/Redis knowledge is required — the
cache is intentionally a five-method, pure-Python, in-memory class — the
signal is about recognizing the invalidation asymmetry and reasoning
carefully about what a cache is allowed to serve after a write.
