# Interview Follow-Up Questions (private)

1. **State the invariant your fix restores, in one sentence.**
   Strong answer along the lines of: "The list view must always reflect
   the true current status of every listing, including a reservation that
   lapsed purely from the passage of time, not just changes made through
   an explicit reserve or purchase call." A candidate who can only say
   "the list wasn't updating" without the "including time-driven changes,
   not just explicit ones" qualifier hasn't fully generalized past the one
   symptom they noticed.

2. **Why does the list view diverge from the detail view specifically, and
   not some other pair of endpoints?**
   Strong answer: because the detail view (`GET /listings/:id`) reads live
   from the repository on every call — the lazy-expiry logic runs as part
   of that exact read, so it's always current by construction. The list
   view (`GET /listings`) is the only endpoint backed by a cache, and that
   cache is only told about state changes that go through the service's
   own explicit mutation methods (reserve, purchase, create) — it has no
   way to learn about a state change that happens purely inside the
   repository's own lazy-expiry logic during some other read. Any other
   pair of endpoints in this app either both read live (no divergence
   possible) or aren't comparing the same underlying state.

3. **Why is shortening the cache's TTL not a real fix?**
   Strong answer: it narrows the *window* in which the wrong answer is
   observable but does nothing to the actual cause — the cache still has
   zero awareness that a lazy expiry happened, it just gets thrown away
   and rebuilt more often "just in case." Concretely: (a) the list and the
   true state can still diverge for up to the TTL window, so the
   invariant is still violated, just less often; (b) if the TTL is
   measured against real wall-clock time rather than the same clock the
   reservation itself is measured against, it isn't even properly testable
   — a test that deterministically fast-forwards the reservation's own
   clock past expiry, with zero real time elapsed, will still observe the
   stale cache, because the TTL check and the expiry check are now
   measuring two different notions of time that don't stay in sync. A
   candidate who says "it makes the bug less likely" without also
   identifying that it remains fully present under deterministic testing
   is only halfway to the real answer.

4. **What would you need to add if this were a shared cache serving many
   simultaneous users, rather than one in-process cache with a single
   debug-controllable clock?**
   Strong answer touches on: the core fix (whatever notices a lazy expiry
   and treats the cache as stale) generalizes conceptually, but a
   real-world shared cache (e.g. Redis) serving concurrent requests raises
   new questions this toy app doesn't have to answer — who's responsible
   for detecting the expiry and invalidating the shared cache when no
   single request "owns" a listing at read time (a background sweep? every
   reader competing to invalidate?), how to avoid a thundering-herd of
   cache rebuilds when many concurrent readers all discover the same
   staleness at once, and whether near-real-time correctness is even
   worth the cost for every consumer, or whether some consumers could
   tolerate a documented, bounded staleness window instead. A candidate
   who says "nothing changes" is missing the concurrency dimension; one who
   redesigns a full distributed cache invalidation protocol unprompted is
   overengineering for what was actually asked — the strong answer names
   the real new problems without trying to fully solve them on the spot.

5. **You noticed the tempting fix (shortening the TTL) reduces how often
   the bug is visible in casual manual testing. Why is that observation
   itself worth taking seriously as a warning sign, even separate from the
   test failures?**
   Strong answer: because it's exactly the kind of change that could make
   a bug *look* fixed during manual QA or a demo — a developer clicks
   around, doesn't happen to catch the stale window, ships it — while the
   underlying invariant is still violated and will eventually cause a real
   support ticket ("I saw this was reserved but it let me try to buy it
   anyway" or similar). It's a useful heuristic for the candidate to
   internalize generally: a fix that makes a bug's *symptom* rarer without
   changing why it happens is a red flag worth being suspicious of on its
   own, independent of whether you happen to have a deterministic test
   ready to prove it.

6. **If you'd found this bug by reading the code first, before ever
   running the app — do you think you'd have caught it? Why or why not?**
   Strong answer: acknowledges that `listingService.ts` read in isolation
   looks like ordinary, correct-looking code — `reserveListing` and
   `purchaseListing` both explicitly invalidate the cache, and
   `getListings`'s cache-check-then-fetch shape is a completely standard,
   unremarkable memoization pattern. The gap only becomes visible once you
   specifically ask "what happens when a listing's status changes through
   some path other than these two methods?" — which requires already
   knowing the lazy-expiry mechanism exists and specifically wondering
   whether the cache knows about it, rather than something a linear read
   of the file would surface on its own. A candidate who claims high
   confidence they'd have caught it from a code read alone should be
   pushed on specifically what would have triggered that question in their
   head before they'd seen the app misbehave.
