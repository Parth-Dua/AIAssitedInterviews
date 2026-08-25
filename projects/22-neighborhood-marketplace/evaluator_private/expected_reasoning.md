# Expected Reasoning Path

1. Start the app (`npm run dev`), open `http://localhost:3000`, and use it
   the way the README suggests: look at the listings, open one to see its
   details, reserve it, purchase it, create a new listing, try the "Advance
   time" and "Reset data" buttons in the Testing tools panel. Nothing
   crashes and everything looks superficially fine on any single action
   taken in isolation.
2. Notice that reserving a listing correctly updates the list view right
   away — that's the easy, expected happy path. The interesting behavior
   is what happens to a reservation that's never explicitly purchased and
   simply runs out on its own. A careful candidate specifically goes
   looking for this, since the README (and the reservation feature itself)
   implies it should "become available again" eventually — the natural
   next question is: what does "eventually" actually look like, and where
   does it show up first?
3. Use the "Advance time" debug control rather than waiting in real time —
   this is explicitly what it's for. Reserve a listing, advance time by
   enough to comfortably pass its reservation window, then check what
   happens.
4. The key discovery step: check *both* views of the same listing after
   the time advance, not just one. Open the listing's detail view — it
   correctly shows `available`. Then go back to the list view *without
   doing anything else* — it still shows `reserved`. This is the moment a
   candidate who only checks one view (e.g., only the detail view, since
   that's the more "specific" thing to check) will miss the bug entirely.
   A candidate who methodically re-checks the list after any state change
   they've made — good practice regardless — stumbles into this
   immediately.
5. Turn this into a minimal, deterministic reproduction — ideally scripted
   with `curl` or a quick `supertest`/Jest snippet rather than repeated by
   hand in the browser: `POST /listings/:id/reserve` → `GET /listings`
   (confirms `reserved`) → `POST /debug/advance-time` with an amount past
   the reservation window → `GET /listings/:id` (confirms `available`) →
   `GET /listings` again (still shows `reserved` — the bug).
6. Form and test hypotheses before diving into code:
   - "Is the reservation expiry timing itself wrong — maybe the comparison
     is off, or `reservedUntil` is computed incorrectly?" Checked by the
     detail-view result in step 5: it's correct, immediately, every time.
     Ruled out.
   - "Does reserving actually update the list correctly at all?" Checked
     by reserving a *different* listing and confirming the list updates
     right away. It does. Ruled out as a general reserve-path problem —
     the issue is specific to the *passive* expiry, not reserving itself.
   - "Is there some caching or staleness issue on reads?" — this is the
     productive hypothesis, and the one to start pulling on: what's
     different between how `GET /listings/:id` and `GET /listings` fetch
     their data?
7. Trace the request paths for both endpoints:
   `GET /listings/:id` → `listingController.getListing` →
   `ListingService.getListing` → `ListingRepository.getById` — reads live
   every time, applies the lazy-expiry check as part of that read.
   `GET /listings` → `listingController.listListings` →
   `ListingService.getListings` — and here's the branch point: it checks a
   cache first, and only calls `repository.getAll()` if the cache is
   empty.
8. Read `listingsCache.ts`: a deliberately simple `get`/`set`/`invalidate`
   store with no logic of its own about *when* to invalidate — realize
   that responsibility lives entirely in the service.
9. Read `reserveListing` and `purchaseListing` in `listingService.ts`: both
   explicitly call `cache.invalidate()` right after changing a listing's
   status. This explains why explicit actions correctly refresh the list.
   The critical realization: *nothing* calls `cache.invalidate()` when a
   reservation lapses on its own — that state change only ever happens
   inside `repository.getById`/`getAll`'s lazy-expiry logic, which the
   cache-populated branch of `getListings` never even reaches once the
   cache is warm.
10. Articulate the invariant being violated: the list must never diverge
    from the true state of any listing for longer than an explicit write
    takes to happen — but a *lazy, read-triggered* status change is
    exactly the kind of write the current code doesn't know how to notice.
11. Design and implement a fix that closes this gap in general, not just
    for the one listing/scenario first noticed — e.g., bound how long a
    cached snapshot may be trusted by the earliest reservation expiry it
    captured (using the repository's own injectable clock, not real time),
    or have the repository notify the cache whenever a lazy expiry
    actually happens. See `bug_design.md`'s "Acceptable fixes" for both.
12. A candidate who reaches for the more obvious lever first — "just make
    the cache go stale faster" (a real-world-time-based TTL) — will notice
    it does reduce how often the bug shows up in manual testing. A strong
    candidate tests this against the *deterministic* debug-clock advance
    (not real waiting) and notices the bug is still fully present: the
    cache is still trusted, because its own staleness check never looked
    at the same clock the reservation itself is measured against. This is
    the moment that most distinguishes a strong candidate on this project —
    recognizing that a fix must be judged against the underlying invariant,
    not against how often the symptom happens to be observed in casual use.
13. Re-run the reproduction against the real fix: the list now correctly
    shows `available` with no further explicit action, and stays correct
    on repeated calls. Extend the reproduction to a second, harder scenario
    — two listings, only one of which has actually expired — to confirm
    the fix updates selectively rather than either staying stale or
    incorrectly disturbing the still-active reservation.
14. Consider the edge case of purchasing a listing whose reservation lapsed
    moments before the purchase attempt itself — decide and verify a
    single, clear, documented behavior (reject as not-purchasable, exactly
    as if it had never been reserved), rather than leaving it ambiguous.
15. Add regression test(s) that encode what was actually found — reserve,
    advance the debug clock, check the list with no further action — verify
    they fail against the original code and pass against the fix.
16. Explain: the cache-invalidation discipline that already existed
    (explicit actions correctly invalidate) was sound but incomplete — it
    covered every *explicit* write but not the *implicit* one that happens
    when a reservation expires on its own, and the fix restores "the list
    reflects the true state" as a general guarantee, not a special case for
    whichever listing happened to be reserved when the candidate first
    noticed the bug.

A strong candidate reaches step 5 (a minimal, scripted repro using the
debug clock) within the first 25-35 minutes, given the added discovery
overhead this project's harder bug shape requires versus Project 21. They
reach step 11 (the actual fix) within 55-75 minutes, and step 12's
recognition that a TTL-shortening approach is insufficient — ideally by
testing it against the fake clock themselves before or instead of being
told — within the full 105-minute timebox. Noticing and rejecting the
TTL-shortening path on their own, rather than only after being prompted in
the debrief, is the strongest single signal this project is designed to
surface.
