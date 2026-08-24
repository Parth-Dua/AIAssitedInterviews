# Evaluator Guide — Project 19: Product Price Lookup Service

## Format & target
AI-Assisted Debugging Assessment. Backend / Full-stack, mid-level. 60-75
min. Difficulty 8/10 — calibrated to Amazon-style repo-based debugging OAs
(fourth of the Node/Express track, Projects 16-20; toolchain and structure
copied from Project 16).

## How to grade

1. Read the candidate's diff to `src/services/priceService.ts` (and any
   other files they touched — flag if they touched `cache/priceCache.ts`,
   `clients/pricingClient.ts`, or `repositories/lastKnownPriceRepository.ts`,
   all of which are correct as given).
2. Copy `hidden_tests/priceHidden.test.ts` into `candidate/tests/` and run
   `npm test` from `candidate/` after applying a candidate's fix. All
   public + hidden tests should pass for a fully correct fix.
3. Compare their fix against `reference_solution/` and `bug_design.md`'s
   "Acceptable fixes" section — several phrasings are fine (any
   delimiter-safe composite key), only the semantics matter. If the
   candidate removed or inlined `buildCacheKey`, use the black-box
   behavioral hidden test (`getPrice — end-to-end collision safety...`) to
   judge collision-safety rather than the direct import, which depends on
   the function still existing under that name.
4. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of root cause and verification,
   including whether they ruled out the two plausible-wrong hypotheses.
5. Score with `scoring_rubric.md`.
6. Ask 2-3 questions from `DEBRIEF.md`.

## Interview-realism audit (private)

1. **Format simulated:** Amazon-style repo-based debugging OA — a small,
   unfamiliar multi-layer Express/TypeScript service (route → controller →
   service → cache/client/fallback-repository), a plain-English bug
   report, public tests that partially reproduce it, hidden tests that
   probe for a specific incomplete fix.
2. **Role level:** Backend / full-stack, mid-level (SDE2-leaning) —
   noticeably deeper than Project 16: the root cause requires ruling out
   two additional files (the pricing client, the fallback repository)
   before landing on the actual defect, and the "acceptable fix" bar
   includes reasoning about composite-key delimiter safety, not just
   restoring a dropped field.
3. **Why feasible in 60-75 min:** Single-function root cause
   (`buildCacheKey`) in one already-isolated helper, five small supporting
   files that are each straightforward to read once you know what you're
   looking for, two failing tests (one unit, one HTTP) that already
   reproduce the bug precisely, and public tests that directly supply the
   evidence needed to rule out both wrong hypotheses (a direct
   `pricingClient.fetchPrice` test, and a `source: 'live'` first-request
   test). A candidate who reads `getPrice` and `buildCacheKey` carefully
   should locate the root cause in 20-30 minutes, leaving time to fix,
   reason about delimiter safety, test, and explain.
4. **Signal obtained:** Whether the candidate can read unfamiliar
   Express/TypeScript route-controller-service-cache-client-repository
   code, trace a request through several thin layers, connect a
   plain-English bug report to a specific line, rule out two independently
   plausible-but-wrong hypotheses by actually reading/testing the relevant
   files (not just asserting they're fine), and produce a fix that not
   only makes the reported case pass but is *actually* collision-safe in
   general — not stopping at the first green test run.
5. **Coding vs. reasoning split:** ~20% coding (a one-line fix to a single
   return statement, plus a test or two), ~80% reasoning/verification —
   more reasoning-heavy than Project 16, appropriate for the higher
   difficulty tier.
6. **Would a top company use a close variant:** Yes — "a cache key doesn't
   encode every dimension the cached value actually varies by, find and fix
   it, and make sure your fix doesn't just move the bug into a delimiter
   collision" is a very common Amazon-style OA/phone-screen shape for
   backend roles working with caching, idempotency keys, or partition keys.
7. **Anything included for production education rather than signal?** No —
   the injectable-clock cache, the fake deterministic pricing client, and
   the separately-keyed fallback repository are included only because
   they're the minimal realistic shape of a small caching service with a
   fallback path, and because they're each necessary to give the candidate
   evidence to rule out (or confirm) a specific hypothesis — not as a
   lesson in Express/caching idioms for their own sake.

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, identify the
defect, and fix it." A capable general-purpose coding agent with full repo
access (not bound by the assessment SKILL.md) can plausibly find and fix
the literal `buildCacheKey` defect in one or two shots, since the two
failing tests pin down the exact wrong-vs-right (`source`, `price`) pair
precisely. What is *not* trivially one-shotted even by an unconstrained
agent is the second half: recognizing that a naive `` `${productId}${currency}` ``
fix, while making the reported tests pass, reintroduces a *different*
collision risk — nothing in the repo or the failing public tests points at
delimiter safety directly, only the hidden collision tests do, which the
agent doesn't have access to. This is expected and acceptable for this
tier: the interview signal is not "can the AI find the literal line" but
"can the candidate direct their assistant well, verify the suggested fix
against the actual stated invariant (not just the literal failing
assertions), and think about what a 'safe' composite key construction
requires in general." Under the assessment SKILL.md, the assistant is
constrained not to just hand over the diff, which restores the intended
signal: the candidate still has to drive reproduction, hypothesis
confirmation (including ruling out the pricing client and the fallback
repository), and verification themselves, including deciding whether "the
two originally-failing tests pass now" actually means "the fix is
correct in general." See `ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.

## Fresh solver simulation (validation record)

Run per rule 34: an isolated agent received only `candidate/README.md`,
`candidate/.ai/assessment-skill/SKILL.md`, and repo access — no bug design,
hidden tests, reference solution, or evaluator notes. Result: it correctly
diagnosed the currency-blind cache key, correctly used the already-passing
"pricing client differentiates by currency" test as evidence ruling out
the wrong hypothesis, and — when explicitly prompted by the simulation
instructions to think about composite-key construction (see below) —
chose a collision-safe key (`JSON.stringify([productId, currency])`) over
naive delimited concatenation, in an estimated 30-50 minutes, inside the
60-75 minute timebox.

**No revision needed, but one methodology note worth recording:** the
simulation's own instructions (written by the orchestrator to probe
whether the collision-safety angle is discoverable at all) included a
direct nudge — "what happens if you just concatenate strings together?"
— that is NOT present anywhere in the actual candidate-facing
`README.md` or `SKILL.md` (grepped for "concatenat", "delimiter",
"collision": zero matches in both). The solver explicitly flagged that
without such a nudge, a plain delimited-concatenation fix (`` `${a}:${b}`
``) would pass every PUBLIC test and "look done," and that the delimiter-
collision hidden test is what's actually responsible for catching that —
exactly as designed: this is hidden-test-carried signal, not something the
public materials are supposed to spell out, so no candidate-facing change
was warranted. It also independently rated the bug itself as easy to spot
by inspection alone (an unused function parameter) — consistent with this
project's documented design (`bug_design.md` calls this "the tell" on
purpose) and with this curriculum's established pattern that AI-agent
solve times run faster than the human timebox without indicating
miscalibration (see `MASTER_EVALUATOR.md` §8).

It confirmed it never accessed anything outside `candidate/`. (Its edits
to `candidate/` were reverted after the simulation, restoring the original
buggy starting state, re-verified at 2 failed / 10 passed.)

## Validation record (this build)

No separate isolated fresh-solver agent pass was run for this project (that
step was not part of this build's brief, unlike Project 16's originating
validation). The validation actually performed — applying the reference fix
and the tempting-but-incomplete fix to clean copies of the starting
repository and confirming the exact pass/fail split against both the public
and hidden suites — is recorded below and should be treated as this
project's validation record.

- Buggy starting `candidate/`: `npm test` → **2 failed, 10 passed** (12
  total), both failures reproducing the currency-blind cache bug at the
  service and HTTP layers respectively.
- Reference fix (`reference_solution/priceService.ts`) applied to a clean
  copy, plus `hidden_tests/priceHidden.test.ts` copied in: `npm test` →
  **17 passed, 17 total** (12 public + 5 hidden).
- Tempting-but-incomplete delimiter-less fix (`` `price:${productId}${currency}` ``)
  applied to a separate clean copy, plus the same hidden tests: `npm test`
  → **15 passed, 2 failed** — all 12 public tests pass (including the
  originally-failing USD-then-EUR test, since currency is now part of the
  key, just unsafely) and 3/5 hidden tests pass (cross-product isolation,
  per-currency TTL expiry, currency-correct fallback), but exactly the two
  collision-detection hidden tests fail
  (`buildCacheKey — composite key collision safety` and
  `getPrice — end-to-end collision safety for concatenation-alike inputs`),
  as designed.
- `candidate/` was restored to its original buggy starting state after
  validation; `npm test` reconfirmed the same 2-failed/10-passed split.
