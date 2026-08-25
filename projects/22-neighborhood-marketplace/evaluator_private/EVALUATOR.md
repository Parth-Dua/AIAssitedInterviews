# Evaluator Guide — Project 22: Neighborhood Marketplace

## Format & target

Black-Box Full-App Debugging Assessment. Backend / Full-Stack, New Grad+ to
Mid-level. ~105 min. Difficulty 9/10 — the hardest project in the entire
22-project curriculum, deliberately above typical intern/new-grad OA
difficulty, calibrated for skill-building. Second and final project of the
"black-box full-app debugging" tier (Projects 21-22); structurally
different from Projects 1-20 (no pre-identified failing test, no named bug
in the README, a real minimal frontend the candidate is expected to
actually use), and structurally distinct from Project 21's bug mechanism
(a stale full-object overwrite) — this project's bug is a cache-
invalidation gap on a lazy-expiry-on-read path, a genuinely different and
harder-to-spot failure mode.

## How to grade

1. Read the candidate's diff. Expect the core change in
   `src/services/listingService.ts` — some mechanism that stops
   `getListings()` from trusting a populated cache indefinitely. A
   candidate may instead (or additionally) touch `listingRepository.ts` to
   add an expiry-notification mechanism; that's an equally valid approach
   — see `bug_design.md`'s "Acceptable fixes" section. Flag if they touched
   `listingsCache.ts`'s public interface unnecessarily, rewrote the
   repository's core `Map`-based storage, or added an unrelated
   authentication/websocket/live-sync feature.
2. Copy `hidden_tests/listingsHidden.test.ts` into `candidate/tests/` and
   run `npm test` from `candidate/` after applying a candidate's fix. All
   public + hidden tests should pass for a fully correct fix (30/30).
3. Compare their fix against `reference_solution/listingService.ts` and
   `bug_design.md`'s "Acceptable fixes" section — several implementation
   shapes are fine; what matters is that the *invariant* holds under the
   hidden tests, not the specific mechanism chosen.
4. **Verify the candidate's own regression test actually catches the bug.**
   This project's public tests deliberately don't encode the bug, so a
   candidate's added test(s) are real signal about whether they understood
   what they found. Temporarily revert their fix (keep their test) and
   confirm their test fails against the original buggy `getListings`; then
   restore their fix and confirm it passes. A candidate whose "regression
   test" would pass against the original buggy code (e.g., it only checks
   the detail view, or only checks the list immediately after an *explicit*
   reserve/purchase, never after a *time-driven* expiry with no further
   action) has not demonstrated the skill this project is testing, even if
   their production fix happens to be correct.
5. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of how they found the bug, the root
   cause, and their verification — this project weights the *discovery
   process* itself even more heavily than Project 21 (see
   `scoring_rubric.md`).
6. Ask specifically whether the candidate considered (or fell into, then
   climbed out of) the TTL-shortening tempting fix, and whether they can
   explain in their own words why it's insufficient even though it reduces
   real-world symptom visibility. This is the single strongest
   differentiator this project is designed to surface — see
   `scoring_rubric.md`'s communication category.
7. Score with `scoring_rubric.md`.
8. Ask 3-4 questions from `DEBRIEF.md`.

## Interview-realism audit (private)

1. **Format simulated:** a "here's a running app, something's wrong, figure
   out what and fix it" black-box exercise — closer to a real bug report or
   an on-call investigation than a repo-debugging OA with a named failing
   test, same shape as Project 21 but with a materially harder underlying
   defect. This format exists at real companies as "explore this staging
   environment and file/fix what you find" exercises, informal bug bashes,
   and real caching-correctness incidents (a stale list view diverging from
   a correct detail view is a very common real production bug shape).
2. **Role level:** Backend/full-stack, new grad+ to mid-level — but at the
   upper end of that band; this project is meaningfully harder than
   Project 21 and is intended to differentiate strong mid-level candidates
   from merely competent ones, by design.
3. **Why feasible in 105 min:** The reproduction sequence is short and
   fully deterministic once found (reserve a listing, advance the debug
   clock past its window, open the detail view, go back to the list) — no
   real concurrency, no multi-tab timing, no flakiness, no real waiting.
   The root cause is isolated to a small number of files once the
   candidate is looking at the right subsystem. The extended 105-minute
   budget (vs. Project 21's 90) accounts for the added conceptual load of
   reasoning about the interaction between two independently-correct
   subsystems, and for exploring/ruling out the TTL-shortening tempting
   fix, rather than any added mechanical complexity.
4. **Signal obtained:** Whether the candidate can (a) use an unfamiliar
   running application deliberately enough to notice a divergence between
   two views of the same data, (b) turn that into a minimal, reliable,
   deterministic reproduction using the app's own time-control debug tool
   rather than real waiting, (c) trace that reproduction through an
   unfamiliar Express/TypeScript service+cache+repository layering to the
   specific missing invalidation path, (d) write a regression test that
   actually encodes the time-driven divergence (not just a smoke test of
   explicit actions), and (e) recognize — ideally on their own — that a fix
   which merely narrows the failure window (shortening a cache TTL) is not
   the same as closing the invariant gap, and can articulate why.
5. **Coding vs. reasoning split:** ~15% coding (the core fix is a compact,
   well-scoped mechanism in one or two files, plus tests), ~85%
   reasoning/exploration/verification — even more reasoning-weighted than
   Project 21, reflecting both the added discovery difficulty and the
   requirement to reason explicitly about *why* a plausible-looking
   alternative fix is wrong, not just *that* it is.
6. **Would a top company use a close variant:** Yes — "a cached list view
   quietly drifts out of sync with a time-driven state change that doesn't
   go through the normal write path" is an extremely common real-world bug
   shape (any system with both a cache and any kind of expiry/TTL/lazy
   cleanup logic is at risk of exactly this class of bug), and "notice it,
   reproduce it deterministically, and reject the first fix that just
   makes it rarer" is a realistic differentiator for backend/full-stack
   roles at companies that value practical debugging and system-level
   correctness reasoning over algorithmic puzzles.
7. **Anything included for production education rather than signal?** No —
   the in-memory `Map` repository, the injectable/advanceable clock, the
   deliberately dumb list cache, the thin controller, and the plain
   static-file frontend are included only because they're the minimal
   realistic shape needed to host a discoverable, deterministically
   reproducible cache-invalidation bug, not as a lesson in Express,
   caching, or vanilla-JS idioms for their own sake.

## AI-trivialization check

Tested prompt: "Explore this running application, figure out what's wrong,
and fix it." A capable general-purpose coding agent with full repo access
(not bound by the assessment SKILL.md) still has to *do* the exploration —
start the dev server, drive the reserve/advance-time/detail-view/list-view
sequence (or replay it via direct HTTP calls), and specifically notice that
two different reads of the same listing, taken moments apart with no
explicit action in between, disagree — because the bug does not manifest in
any single function read in isolation. Reading `listingService.ts` in
isolation shows three methods (`reserveListing`, `purchaseListing`,
`getListings`) that each look locally reasonable: the first two explicitly
call `cache.invalidate()` after mutating state, and `getListings` looks like
an unremarkable, textbook memoization pattern ("if cached, return it;
otherwise compute and cache it") — nothing about it looks wrong *unless* you
already know to ask "what happens to a listing that changes status without
going through `reserveListing` or `purchaseListing`?" This is a genuinely
harder bug to shortcut via code-reading alone than Project 21's, because
Project 21's fix required noticing a single *absent* check in a function
whose contract (accepting and requiring a `version` field) hinted at what
was missing; this project's fix requires noticing an *interaction gap*
between two files (`listingsCache.ts` and `listingRepository.ts`) that are
each independently correct and give no local hint that anything is wrong.
A code review pass alone, without actually running the app through the
specific interaction sequence (or at minimum simulating it via direct HTTP
calls including a debug clock advance), is a very weak signal for finding
this class of bug. This is the central design goal of the black-box tier,
taken to its hardest point in the curriculum: reading code well is
necessary but nowhere near sufficient; the agent (and the candidate
directing it) has to actually generate and observe behavior across two
different read paths, over a simulated passage of time. Under the
assessment SKILL.md, the assistant is additionally constrained not to name
the bug or the endpoint/file to look at until the candidate has reported
concrete observations from their own exploration — see the "Black-box
discovery phase" section — which further restores the intended signal: the
candidate must drive the discovery themselves even if their assistant could
technically find the bug quickly once told to run the actual reproduction
sequence.

## Fresh black-box solver simulation (validation record)

Run per rules 14/34, applying the same black-box standard established on Project 21:
an isolated agent received only `candidate/README.md` and
`candidate/.ai/assessment-skill/SKILL.md`, was explicitly instructed not to read
`src/`/`tests/` until after exploring the running app, and had no access to
`evaluator_private/`. Result: this is the strongest validation in the whole
curriculum for the discovery format specifically. The agent's FIRST reproduction
attempt looked clean (the list "self-corrected") purely because of call ordering
(it hadn't populated the list cache before advancing time); it recognized this,
deliberately varied the ordering ("compare views, vary ordering" — a strategy it
attributes to the task's own instruction to compare views across time, not
something it stumbled onto by luck), and found the real divergence on the second
attempt. It independently formed and disproved a wrong hypothesis (wall-clock TTL
cache — disproved by polling for 30 real seconds with no change) before reserving
an unrelated listing to confirm invalidation is write-triggered, exactly the
evidence-gathering sequence `bug_design.md`'s "expected reasoning" describes. It
considered and explicitly rejected the TTL-shortening fix with the correct
reasoning (decoupled from *when* a specific reservation actually expires; hides
rather than fixes the defect). All in a full, clean session; `npm test` 28/28 (25
public + 3 of its own regression tests) across 3 consecutive runs.

No leakage was found. It explicitly flagged `ListingsCache`'s own doc comment
("no logic of its own about when a snapshot should be considered stale — that's
entirely the caller's responsibility") as accurate context read only AFTER it had
already found the bug through the app, not a giveaway — consistent with how
similarly-worded, honestly-documented GIVEN/correct code has been judged
throughout this curriculum (e.g. Projects 4, 10, 14). It rated the 105-minute
timebox as "about right, maybe slightly generous" for a candidate who reads the
README's cross-view-comparison guidance carefully, but "tight" for one who
doesn't immediately think to vary call ordering around the time-advance — judged
an accurate, not alarming, characterization of an intentionally hard, final
project, not a signal requiring revision.

No revisions to the exercise were needed. It confirmed it never accessed
anything outside `candidate/`, and confirmed the dev server was killed and its
absence verified via `ps`, `lsof`, and a refused `curl`. (Its code edits were
reverted after the simulation, restoring the original buggy starting state,
re-verified at 25/25 public tests passing.)

This is the final solver simulation of the full 22-project curriculum. All 12
Python-track (Projects 4-15), 5 Node-track (Projects 16-20), and 2 black-box-tier
(Projects 21-22) fresh solver simulations are now complete and recorded.

## Agent independence

No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.

## Fresh solver simulation (validation record)

Run per rule 34 (the standard applied to every project in this suite): this
build's author (not a separate isolated agent instance, but functionally
equivalent — no access to `bug_design.md`, `hidden_tests/`, or
`reference_solution/` was assumed while designing the candidate-facing
artifacts) verified end-to-end that: (a) all 25 public tests pass against
the unmodified buggy `candidate/` code, confirmed three times via
`npm test` for full determinism; (b) the symptom reproduces against a real
running `npm run dev` server via `curl`, simulating the exact
reserve → advance-time → detail-view → list-view sequence a UI user would
trigger — confirmed, the list view remains stuck on `reserved` after the
detail view has already correctly moved to `available`; (c) during this
process, an incidental object-aliasing bug in the initial implementation
(mutating a `Listing` in place rather than replacing it) was caught because
it silently masked the intended bug — documented and fixed in
`bug_design.md`'s validation log, and re-verified after the fix; (d) the
reference fix, applied in an isolated scratch copy with the hidden tests
copied in, passes all 30 tests (25 public + 5 hidden), run three times with
identical results, and the same `curl` reproduction against the fixed
server now shows the list correctly reflecting the expiry; (e) the hidden
tests were confirmed to actually fail against the *original, unfixed* code
(4 of 5 fail, the 5th being a sanity check that doesn't depend on expiry);
(f) the TTL-shortening tempting fix, applied in a separate isolated scratch
copy in place of the reference fix, passes 26/30 (25/25 public — ordinary
usage is entirely unaffected — and exactly 1/5 hidden, the sanity check)
and fails specifically the four expiry-divergence hidden tests that
distinguish it from a correct fix, for the documented reason (a real
wall-clock TTL cannot detect a purely fake-clock-driven expiry with zero
real time elapsed); (g) `candidate/` was restored to its original,
untouched buggy state after all scratch-copy work, and both `npm test`
(25/25, re-run) and the `curl` reproduction were re-verified against the
restored state. See `bug_design.md`'s "Validation log" section for the full
detail.

**Findings that caused revisions during this build (applied and
re-verified):**
- The object-aliasing issue described above (item (c)) was found and fixed
  before any test files were written against the final behavior — the
  lazy-expiry logic in `listingRepository.ts` and the explicit-mutation
  logic in `listingService.ts` were both changed to construct new `Listing`
  objects rather than mutate existing ones in place, specifically so that
  an object reference captured inside an already-cached list snapshot
  cannot be silently corrected by an unrelated later read.
- The README was drafted with the exclusion list (no mention of "cache,"
  "invalidat-," "TTL," "lazy expir-," or any specific endpoint/file name in
  a way that narrows the search) checked directly against the final text
  before publishing — the product-level concept of a reservation expiring
  is described plainly, since that's a real, intended product feature, but
  nothing about *how* expiry or listing is implemented is disclosed.
- The SKILL.md was checked for Python/FastAPI/Pydantic leftovers from the
  shared template (none found — copied from Project 21's already-
  genericized version, with only the final "Scope of this exercise"
  paragraph rewritten for this project's stack and domain).
