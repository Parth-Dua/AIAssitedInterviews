# Expected Reasoning Path

## Part A — the stale cache bug

1. Run `pytest -q`; observe `test_put_then_immediate_get_returns_new_values`
   fails while most other tests pass (along with the separate, unrelated
   TTL failure — see Part B).
2. Read the failing test: GET warms the cache with the original value,
   PUT changes it, a following GET still returns the original value.
3. Open `app/services/notification_prefs_service.py`. Read
   `get_preferences` first: cache hit → return; cache miss → read
   repository, populate cache, return. This is a correct read-through
   cache.
4. Read `update_preferences` immediately below it: builds the new
   preferences object (with the normalization rule), calls
   `self._repository.save(preferences)`, and returns — no reference to
   `self._cache` anywhere in the method.
5. Recognize the asymmetry: the read path always keeps the cache in sync
   with itself, but nothing keeps the cache in sync with a write. Since
   the starting `Cache` has no TTL, a stale entry lives there forever once
   cached.
6. Fix: add `self._cache.delete(_cache_key(user_id))` (or
   `self._cache.set(key, saved, ...)`) at the end of `update_preferences`.
7. Re-run tests; the stale-read test passes. Manually reason through (or
   write a test for) a second PUT to confirm invalidation isn't a
   one-shot fix tied to a specific call site.
8. Explain: the cache and the repository are two copies of the same data;
   any code path that changes one must also account for the other, and
   the general principle at work is "the cache must never diverge from
   the source of truth after a write completes."

## Part B — the TTL feature

1. Run `pytest -q`; observe `test_cache_entries_expire_after_ttl` fails
   with a `TypeError` — `Cache.set()` doesn't accept `ttl_seconds` yet.
2. Open `app/cache/cache.py`; notice `Cache.__init__` already accepts an
   injectable `now_fn` clock (a partially-built hook for exactly this
   feature) but `set`/`get` have no TTL logic. A `# TODO` comment names
   the gap.
3. Design: `set(key, value, ttl_seconds=None)` records an expiry
   (`self._now() + ttl_seconds`) when given; `get(key)` checks whether
   the current time (via `self._now()`) has passed that expiry, and if so
   treats the entry as a miss and evicts it.
4. Pick and apply a boundary convention consistently (this reference
   solution uses `now() >= expires_at` — inclusive at the exact TTL
   mark) and be able to state it.
5. Update `get_preferences` in the service to pass a default TTL (e.g. 60
   seconds) when populating the cache on a miss.
6. Write/extend tests using a fake clock (`Cache(now_fn=lambda: fake[0])`)
   instead of real sleeps — advance the fake clock manually to assert
   expiry behavior deterministically and fast.
7. Re-run tests; both previously-failing tests now pass.
8. A strong candidate also notices, while working on the bug fix, that if
   they choose to actively re-cache on write (`cache.set(...)`) instead of
   deleting, they must be careful to cache the *persisted* value (the
   repository's return value, post-normalization) rather than the raw
   request body — and either tests this directly or reasons through the
   "disable all three channels" normalization case out loud.

A strong candidate reaches a correct fix for Part A within 15-20 minutes
and a correct TTL implementation for Part B within another 20-30 minutes,
leaving time to add tests and verify both together (e.g. that a write
still correctly invalidates/repopulates even with a TTL active).
