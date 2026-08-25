# Bug Design (private — do not expose to candidate)

## Expected behavior

`GET /listings` (the list view) must, at all times, reflect the true
current status of every listing — including a reservation that has lapsed
purely from the passage of time, with no explicit reserve/purchase/create
action having happened. Invariant: **"the cached list view must never
diverge from the true state of any individual listing for longer than it
takes an explicit write to occur — ANY code path that changes a listing's
status, including a lazy, read-triggered one, must keep the list cache
consistent."**

## Actual (buggy) behavior

`GET /listings/:id` (`ListingService.getListing` →
`ListingRepository.getById`) reads live, in-memory state every time. Part of
that live read applies a lazy-expiry rule (correct, given, and not the bug):
if a listing is `'reserved'` and its `reservedUntil` clock value has passed,
it's flipped back to `'available'` right then, persisted, and the corrected
listing is returned. This mechanism is entirely correct in isolation — a
direct `GET /listings/:id` taken at any moment always shows the true state.

`GET /listings` (`ListingService.getListings`), by contrast, is backed by an
in-memory cache of the *full* listings array
(`src/cache/listingsCache.ts`, a deliberately dumb store with no opinion of
its own about when to invalidate). The starting `getListings` is:

```ts
getListings(): Listing[] {
  const cached = this.cache.get();
  if (cached) {
    return cached;
  }
  const fresh = this.repository.getAll();
  this.cache.set(fresh);
  return fresh;
}
```

`reserveListing` and `purchaseListing` are both correct — each calls
`this.cache.invalidate()` immediately after changing a listing's status, so
any *explicit* user action (reserving, purchasing, creating a listing) is
reflected in the very next `GET /listings` call. But when a reservation
simply **expires with the passage of time** — discovered lazily, whenever
anything happens to read that listing via the repository, or whenever
`getAll()` itself re-scans everything — nothing tells the cache. Once
`GET /listings` has cached a snapshot that includes a listing as
`'reserved'`, that snapshot keeps showing `'reserved'` forever, until some
*unrelated* explicit reserve/purchase/create action on *any* listing
happens to invalidate the whole cache as a side effect. Meanwhile
`GET /listings/:id` on that exact same listing, taken at any point after
expiry, correctly shows `'available'` — because it never goes through the
cache at all.

## Root cause

A missing invalidation path, not a miscalculation. The expiry-timing logic
itself (`reservedUntil <= now()`) is correct and provably so on every direct
read. The cache-invalidation discipline on explicit writes is also correct
and provably so (reserving or purchasing any listing immediately and
correctly updates the list). The gap is specifically between these two
otherwise-correct systems: nothing in `getListings`'s "trust the cache while
it's populated" logic accounts for the possibility that the *repository's
own state* changed silently, out from under the cache, via a mechanism
(lazy expiry) that isn't a call to `save()` triggered by the service's own
explicit mutation methods. The buggy code and the correct code
(`reserveListing`/`purchaseListing`'s own `cache.invalidate()` calls) look
structurally identical in shape — the missing piece is an omission, not a
visibly wrong line, which is what makes this bug class hard to catch by
code-reading alone.

## Violated invariant

"The cached list view must never diverge from the true state of any
individual listing for longer than it takes an explicit write to occur —
any code path that changes a listing's status, including a lazy,
read-triggered one, must keep the list cache consistent."

## Relevant execution path

`GET /listings` (`src/routes/listings.ts`) → `listListings` controller
(`src/controllers/listingController.ts`, thin, no logic of its own) →
`ListingService.getListings` (`src/services/listingService.ts`, **the bug**
— trusts a populated cache indefinitely) → `ListingsCache`
(`src/cache/listingsCache.ts`, correct, given — a dumb store with zero
opinion about *when* to invalidate, which is precisely why reading it in
isolation doesn't reveal anything wrong) → `ListingRepository.getAll`/
`.getById` (`src/repositories/listingRepository.ts`, correct, given — the
lazy-expiry mechanism itself, and the injectable clock via `now()`). The
candidate must read and understand all three files together to see the gap:
the cache file alone looks trivially correct ("it's just a get/set/
invalidate store"); the repository file alone looks trivially correct ("it
just fixes up expired reservations on read"); the service file's
`reserveListing`/`purchaseListing` methods look correct and *are* correct.
Only by tracing what happens when a reservation expires *without* going
through `reserveListing` or `purchaseListing` does the gap become visible.

## Evidence available to the candidate through the app

- Reserving a listing and immediately checking the list view: correctly
  shows `'reserved'` right away. This rules out "the explicit reserve
  action doesn't update the list" as a hypothesis.
- Opening that same listing's individual detail view after advancing the
  debug clock past its reservation window: correctly shows `'available'`
  immediately. This rules out "the expiry timing/comparison itself is
  wrong" as a hypothesis — the underlying mechanism is provably correct
  when read directly.
- Going back to the list view after that, with no further explicit action:
  still incorrectly shows `'reserved'`. This is the divergence — two
  different views of the exact same listing disagree, and only one of them
  is telling the truth.
- Reserving or purchasing a *different, previously untouched* listing at
  this point immediately and correctly refreshes the *entire* list,
  including the originally-expired listing — because that explicit action's
  `cache.invalidate()` call clears the whole cache as a side effect. This
  can mislead a candidate into thinking the problem "fixed itself," when
  really an unrelated action just happened to force a fresh fetch.

## Reasonable hypotheses

1. (Wrong, tempting) "Maybe the reservation expiry timing itself is off —
   `reservedUntil` is computed wrong, or the comparison is off-by-one."
   Ruled out: the detail view (`GET /listings/:id`) shows the correct,
   immediate expiry at exactly the right moment, every time, with no
   caching involved on that path at all.
2. (Wrong, tempting) "Maybe the Reserve action itself doesn't correctly
   update the list." Ruled out: reserving a different, previously-untouched
   listing correctly and immediately shows as reserved in the list view —
   the explicit-action invalidation path works fine. It's specifically the
   passive, time-driven expiry that the list never learns about.
3. (Correct) The list is served from a cache that's only invalidated by
   explicit reserve/purchase/create calls, never by the lazy-expiry-on-read
   mechanism — which can silently change a listing's true status without
   any code path knowing to invalidate the cached list.

## Intended regression tests

Public tests (`candidate/tests/`) cover ordinary usage — creating,
listing, fetching a single listing, reserving (with the list immediately
reflecting it), rejecting a double-reserve, purchasing (reflected in both
views), and confirming the detail view shows the correct status immediately
after the debug clock passes a reservation's expiry — and pass unmodified
on the buggy starting code (verified; see the validation log at the end of
this file). None of them ever check the *list* view after a *time-driven*
expiry with no further explicit action, so none of them encode the bug.

Hidden tests (`evaluator_private/hidden_tests/listingsHidden.test.ts`)
cover: the core divergence (reserve → the list correctly shows reserved →
advance the debug clock past expiry → the detail view correctly shows
available → the list must also show available, with no further explicit
action, and stays correct on a repeated call); the same divergence when the
list view was never opened again after the reserve until after the debug
clock advance (rules out a fix that only self-corrects when the detail view
happens to have been visited first); a multi-listing scenario where only
one of two reservations has actually expired, proving a correct fix updates
selectively rather than either staying fully stale or blowing away
unrelated still-active reservations; a listing whose reservation expired
exactly by the time a purchase attempt reads it (see "Edge case" below); and
a sanity check that a fresh reservation still appears correctly in the list
immediately, so an overzealous "fix" that breaks normal caching correctness
altogether doesn't pass by accident.

## Edge case: purchasing a listing whose reservation just expired

Chosen, documented behavior: if a reservation has already lapsed by the
time a purchase attempt reads the listing (via `repository.getById`, which
applies lazy expiry as part of that very read), the listing is, by
definition, no longer `'reserved'` at the moment `purchaseListing` checks
its status — so the purchase is rejected with the same
`ListingNotPurchasableError` (409) used for any other listing that isn't
currently reserved, exactly as if it had never been reserved at all. This
is authoritative and intentional: the lazy-expiry check inside that same
`getById` call is what decides the listing's true state, and
`purchaseListing` must respect it rather than trusting a `'reserved'` status
it might have observed a moment earlier through some other read. This
scenario also happens to be a second manifestation of the exact same root
cause: the failed purchase attempt itself causes a real, lazy,
read-triggered status change (`'reserved'` → `'available'`) via its own
`getById` call, but because `purchaseListing` throws before it ever reaches
its own `cache.invalidate()` line, that change is just as invisible to the
list cache as the original expiry was — which is why a correct fix must
handle "the cache can go stale from *any* lazy expiry, not just the ones
`getListings` itself happens to trigger," not special-case
`getListings`'s own internal `getAll()` call.

## Acceptable fixes

No specific implementation is prescribed — a fix is correct exactly when it
passes all public and hidden tests without breaking the general caching
behavior (a fresh reservation must still appear in the list immediately).
Two broad approaches were validated as acceptable during this project's
build:

1. **Bound the cache's trust window by the earliest reservation it
   captured** (the reference solution's approach — see
   `reference_solution/listingService.ts`). Track, alongside the cached
   snapshot, the earliest `reservedUntil` among the listings that were
   `'reserved'` at the moment the snapshot was taken. On the next
   `getListings` call, only trust the cached snapshot if the repository's
   current clock reading is still before that bound; otherwise treat it as
   stale and refetch. This is deterministic (it uses
   `repository.now()`, the same injectable clock the rest of the app uses,
   never real wall-clock time), requires no change to the repository or
   cache's public interfaces, and correctly narrows to exactly the
   listings whose reservations could plausibly have expired — a snapshot
   with no reservations in it is never treated as stale by this mechanism
   at all (it can only go stale via an explicit invalidate() call, which
   is unchanged and already correct).
2. **Have the repository report when a lazy expiry actually changed
   something**, e.g. `getAll()`/`getById()` accepting an optional
   "on-expiry" callback, or `getAll()` returning
   `{ listings, anyExpired: boolean }`, wired so that any lazy expiry
   anywhere invalidates the list cache immediately, synchronously, the
   moment it happens — not just expiries discovered inside
   `getListings`'s own fetch. This spans `listingRepository.ts` (adding the
   notification) and the composition point where the repository, cache,
   and service are wired together, in addition to `listingService.ts`.
   This approach is equally acceptable, and is the more "obviously general"
   of the two, but is not required — approach 1 above also correctly
   handles every hidden test, including the purchase-just-expired edge
   case, because `getAll()`'s own expiry check is re-evaluated fresh on
   every call once the trust bound is exceeded, independent of whatever
   read path caused the underlying state to change.

Whichever approach a candidate takes, the fix must not be scoped to "the tag
loses on a stale save"-style single symptom — it must hold for any listing,
under any ordering of explicit and lazy state changes, which is exactly
what the hidden test suite checks.

## Tempting but incomplete/wrong fix

A candidate who reproduces the bug by using the app manually (open detail
view after enough real waiting, or by trial and error with the debug clock)
is likely to notice the symptom is easier to observe "the longer you wait
before re-checking the list" and reach for the wrong lever: **shorten the
cache's own lifetime** by adding a real-world time-to-live to the cached
snapshot — e.g., automatically treat the cache as invalid once more than a
couple of seconds of *real* wall-clock time (`Date.now()`) have passed since
it was populated, regardless of what the injectable clock says. This
narrows the window in which a stale list is observable during normal manual
testing (a candidate clicking around in a browser, waiting a few seconds
between actions, would likely stop noticing the bug at all) — but it does
**not** fix the underlying invariant. The cache and the true state can
still diverge for up to that TTL window, and critically, because this
"fix" measures its own staleness using real wall-clock time rather than the
repository's injectable clock, it is not even properly testable or
deterministic: a hidden test that advances the *fake* debug clock (not real
time) past a reservation's expiry and immediately re-checks the list — with
essentially zero real wall-clock time having elapsed during the test itself
— still observes the stale, cached `'reserved'` entry, because the TTL
measured against `Date.now()` has not remotely elapsed in test-execution
time. This is exactly why the core hidden test (see
`hidden_tests/listingsHidden.test.ts`) uses `/debug/advance-time`
exclusively and never `setTimeout`/real sleeps: it is specifically designed
to distinguish "the invariant is actually restored" from "the failure
window was made narrower, but the bug is otherwise unchanged." Verified in
the validation log below: this TTL-shortening patch passes all 25 public
tests (nothing about ordinary usage changes) and exactly 1 of 5 hidden
tests (the sanity check, which never depends on expiry at all) — the other
4 all fail with `'reserved'` where `'available'` was expected, for the
identical reason in each case.

## Why this is calibrated above standard OA difficulty, and why it's the
hardest project in the curriculum

This is the second and final project of the "black-box full-app debugging"
tier (Projects 21-22), and deliberately the hardest project in the entire
22-project curriculum — harder than the earlier Python and Node capstones,
and structurally distinct from Project 21's stale-full-object-overwrite bug
even though both projects share the black-box discovery shape. Three things
compound to make this harder than Project 21:

1. **Two otherwise-correct systems, not one incorrect one.** Project 21's
   bug was a single missing check in a single function. This project's bug
   is the *interaction* between two independently correct-looking
   subsystems (the lazy-expiry mechanism and the explicit-invalidation
   discipline) — reading either one in isolation, or even both, without
   specifically asking "what happens when state changes *without* going
   through the paths that call `cache.invalidate()`?" will not surface it.
   A candidate has to hold both mechanisms in their head simultaneously and
   reason about their interaction, not just find "the missing line."
2. **The symptom requires comparing two live views of state over time**,
   not just noticing one endpoint behaves oddly. The candidate must
   specifically compare the list view against the detail view *at the same
   moment*, after a *time-based*, non-explicit-action state change — a
   genuinely different discovery shape than "click a button, watch the
   wrong thing happen," which is closer to what Project 21 asked for.
3. **A structurally plausible but wrong fix exists and must be explicitly
   argued against**, not just avoided by accident. The TTL-shortening
   tempting fix isn't a strawman — it's the fix most engineers would reach
   for first, it does measurably reduce the bug's real-world visibility,
   and explaining precisely why it's still wrong (using real time instead
   of the domain's own clock; narrowing a window instead of closing a gap)
   requires the same level of invariant-level reasoning as finding the bug
   itself.

The reproduction sequence remains fully deterministic and single-session
(no real concurrency, no multi-tab timing, no flakiness) via the injectable
clock and `/debug/advance-time` — the difficulty is concentrated entirely
in the discovery-and-reasoning dimension, not in getting lucky with timing.

## Validation log

- `npm install && npm test` against the unmodified `candidate/` starting
  code, run three times: **25/25 public tests pass**, every time (2 test
  suites, `listingService.test.ts` and `listingsApi.test.ts`).
- Manual `curl` reproduction against a real running `npm run dev` server:
  reserved `listing-1` → list correctly showed `reserved` → advanced the
  debug clock by 360000ms (past the 300000ms reservation window) →
  `GET /listings/listing-1` (direct) correctly showed `available` →
  `GET /listings` (list) **still incorrectly showed `reserved`** — the bug
  reproduced exactly as designed. Separately confirmed that reserving a
  *different* listing afterward correctly self-corrected the entire list,
  including the originally-stale entry — matching the documented "explicit
  actions elsewhere incidentally mask the bug" behavior.
- **Aliasing pitfall caught and fixed during build:** the first
  implementation of the lazy-expiry logic mutated the `Listing` object in
  place rather than replacing it, which meant an object reference held
  inside an already-cached list array got silently corrected for free the
  moment any other code path (e.g. the detail view) read and expired it —
  completely masking the intended bug. Fixed by having lazy expiry (in the
  repository) and the explicit reserve/purchase mutations (in the service)
  construct new listing objects instead of mutating in place. Re-verified
  the manual `curl` reproduction after this fix; the bug reproduced
  correctly.
- Reference fix (`reference_solution/listingService.ts`) applied over the
  buggy file in an isolated scratch copy, hidden tests copied in:
  **30/30 tests pass** (25 public + 5 hidden), run three times with
  identical results each time. Re-ran the manual `curl` reproduction
  against this fixed server: the list now correctly shows `available`
  immediately, with no further explicit action.
- Confirmed the hidden tests actually catch the *unfixed* bug: copied
  `listingsHidden.test.ts` into the original, untouched buggy
  `candidate/tests/`, ran `npm test` — **4 of 5 hidden tests failed**
  (all four expiry-divergence tests), **1 passed** (the sanity check, which
  never depends on expiry), for **26/30 total**. Removed the hidden test
  file from `candidate/tests/` afterward.
- TTL-shortening tempting fix applied in a separate isolated scratch copy
  (in place of the reference fix), hidden tests copied in: **26/30 tests
  pass** — all 25 public tests pass (ordinary usage is unaffected) and
  exactly 1 of 5 hidden tests passes (the sanity check); the other 4 fail
  identically to the unfixed buggy code, for the reason documented above
  (real-wall-clock TTL vs. a deterministic fake-clock advance with
  effectively zero real time elapsed during the test).
- `candidate/` restored to its original, untouched buggy state throughout
  (all fix/tempting-fix work happened in isolated scratch copies outside
  the repository); re-verified afterward that `npm test` → 25/25 pass and
  the `curl` reproduction still shows the bug against the restored state.
