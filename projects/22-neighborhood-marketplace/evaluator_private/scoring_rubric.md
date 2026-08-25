# Scoring Rubric — Project 22 (100 points)

As the final and hardest project in this curriculum, this rubric weights
the *discovery process* and the ability to reason about (and reject) a
plausible-but-wrong fix even more heavily than Project 21's.

| Category | Points | Notes |
|---|---|---|
| Exploratory debugging / recognizing incorrect behavior | 15 | Did the candidate actually use the running app (UI, or direct HTTP calls replaying UI actions, including the debug time-advance tool) rather than jumping straight to reading source looking for "the bug"? Can they describe what they did and what they observed — specifically, a divergence between two different views of the same listing — that first looked wrong? |
| Reproduction quality & determinism | 15 | Reduced what they noticed to a minimal, deterministic, repeatable sequence using `/debug/advance-time` (not real waiting, not a flaky `setTimeout`) rather than something that "sometimes happens" or takes minutes of real time to observe. Correctly isolates which specific sequence of actions and time advance triggers the divergence. |
| Hypothesis formation & evidence gathering | 15 | Considered more than one explanation before settling on the real one — specifically, did they test and rule out "the expiry timing itself is wrong" (by checking the detail view shows correct expiry) and "the explicit reserve action doesn't update the list" (by reserving a different listing and seeing it work) before concluding the gap is specific to the passive, time-driven expiry path? |
| Root-cause reasoning & identifying the invariant | 20 | Correctly identifies that the list cache is invalidated on every explicit reserve/purchase/create call but never by the lazy-expiry-on-read mechanism, and can state the general invariant this violates (not just describe the one symptom they happened to find). Weighted higher than Project 21's equivalent category because the root cause here requires reasoning about the *interaction* between two independently-correct subsystems, not locating one missing check in one function. |
| Fix correctness & completeness | 15 | Public tests pass; hidden tests pass — including the multi-listing selective-update test and the purchase-just-expired edge case, which specifically catch a fix that's too narrowly scoped to the exact symptom first noticed. The fix does not merely shorten the window in which staleness is observable; it closes the gap so that the list is provably correct arbitrarily long after a time-driven expiry, verified via the deterministic debug clock, not real waiting. |
| Regression tests added | 10 | Candidate added at least one test that actually encodes the discovered divergence — using the debug time-advance tool deterministically, not a real sleep — and checks the *list* view specifically after a *time-driven* (not explicit-action-driven) status change. Verified by evaluator reverting the candidate's fix and confirming the candidate's test then fails (see `EVALUATOR.md` step 4). |
| Communication / explaining the invariant and rejecting the tempting fix | 10 | Can state, in their own words, the invariant their fix enforces, and — critically — can explain concretely why a fix that merely shortens the cache's real-world TTL would be insufficient, even though it would make the bug harder to notice in casual manual testing. This is the single highest-signal question this project is designed to surface. |

**Passing bar (strong new-grad+/mid-level signal):** ≥75, hidden tests
pass, candidate's own regression test independently fails against the
unfixed code, and candidate can explain both the invariant and why a
TTL-shortening approach would be insufficient, without prompting.

**Red flags:**
- Fix passes the core divergence scenario but fails the multi-listing
  selective-update test or the purchase-just-expired edge case (the fix
  was scoped too narrowly to the exact symptom first noticed, rather than
  the general invariant).
- Fix relies on real wall-clock time (`Date.now()`, `setTimeout`,
  `setInterval`) anywhere in its staleness logic instead of the
  repository's injectable clock — this is close to the TTL-shortening
  tempting fix even if the candidate arrived at it independently, and will
  fail the hidden tests' deterministic-fake-clock checks. Ask the
  candidate directly whether they considered this and why they chose (or
  rejected) it.
- Candidate's added test would also pass against the *original buggy* code
  (i.e., it doesn't actually exercise the time-driven divergence) — this
  scores near-zero on "regression tests added" regardless of whether the
  production fix itself is correct.
- Candidate jumped straight to reading `listingService.ts` without ever
  running the app or making any HTTP request/debug-clock-advance that would
  surface the actual discrepancy — even if they land on the right file by
  luck or pattern-matching cache code across their prior experience, this
  is weak signal for the discovery skill this project targets.
- Candidate cannot explain, in their own words, why the TTL-shortening
  approach is insufficient — only that a suggested change made tests pass.
- Candidate makes `GET /listings` always bypass caching entirely with no
  articulated reasoning (e.g., just deletes the cache), which happens to
  pass every test but demonstrates they treated "make it pass" as the goal
  rather than understanding and fixing the actual invariant gap. Probe this
  in the debrief rather than penalizing it outright if the candidate can
  still correctly explain the invariant — but flag it.
- Candidate rewrites large parts of the service/repository/cache/frontend
  "to be safe," or introduces a database/ORM-style abstraction, real
  authentication, or a websocket-based live-sync feature unprompted — well
  beyond the scope of the reported problem.
