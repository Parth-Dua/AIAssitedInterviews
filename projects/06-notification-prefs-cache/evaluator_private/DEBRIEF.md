# Interview Follow-Up Questions (private)

1. **What was the root cause of the stale-preferences bug?**
   Strong answer: the write path (`update_preferences`) persisted the new
   value to the repository but never invalidated or updated the
   corresponding cache entry, so a cache entry populated before the write
   kept being served indefinitely (there was no TTL yet either).

2. **What are the general strategies for keeping a cache consistent with
   its source of truth, and which did you use here?**
   Strong answer: the common strategies are (a) invalidate-on-write
   (delete the cache entry so the next read repopulates from the source
   of truth — simplest, what this fix likely used), (b) update-on-write
   (write the new value directly into the cache at write time, avoiding
   an extra read but requiring care that the cached value exactly matches
   what was persisted), and (c) TTL/expiry as a backstop that bounds
   staleness even if (a) or (b) is missed somewhere. This exercise asked
   for (a) or (b) plus (c) — the fix addresses the immediate bug, and the
   TTL is defense in depth for the next time someone forgets.

3. **Why is caching the request body instead of the persisted value risky
   in general, beyond this specific normalization rule?**
   Strong answer: any time the server does something to the data between
   receiving a request and persisting it — validation that mutates
   defaults, normalization, computed/derived fields, timestamps assigned
   server-side, id generation — caching the request means the cache and
   the database can diverge silently, and it will look correct in testing
   until someone happens to exercise the specific case where server-side
   logic changes the value. The safe pattern is to always cache what the
   write operation actually returns/persists, not what was sent in.

4. **How did you test the TTL behavior without making the test suite slow
   or flaky?**
   Strong answer: injected a fake clock (a callable returning a
   controllable value) into `Cache` instead of using real
   `time.sleep()`; the test can then jump the fake clock forward by any
   amount instantly and assert expiry deterministically.

5. **How would you extend this if preferences could be updated by
   multiple concurrent requests?**
   Strong answer (design-forward-thinking): in the current single-process,
   in-memory setup there's no real concurrency hazard beyond normal
   Python execution order, but in a real system with a shared cache
   (e.g. actual Redis) and multiple app instances, a read that races with
   a write could still observe a stale value between the write's DB
   commit and its cache invalidation — the usual mitigations are keeping
   the invalidation-after-write window as short as possible, considering
   a short TTL specifically to bound that race (which this exercise
   already does), and for stricter consistency needs, techniques like
   versioned cache keys or read-your-writes guarantees scoped to the
   requesting client.

6. **If a different endpoint needed to read the same preferences data,
   how would you avoid re-deriving the cache-invalidation logic there
   too?**
   Strong answer (design-forward-thinking): centralize writes through a
   single method (as `update_preferences` already is) so there's exactly
   one place that must remember to invalidate/update the cache, rather
   than duplicating "write to repo + touch cache" logic at each call
   site; a repository-level or cache-aware write helper is one way to
   make forgetting the invalidation call structurally harder.
