# Evaluator Guide — Project 20: Expense Approval Platform (Capstone)

## Format & target
AI-Assisted Debugging + Feature Assessment. Backend / New Grad+ to
Mid-level. 60-90 min. Difficulty 8.5/10 — the hardest exercise in the
Node/TypeScript track (Projects 16-20), mirroring the role Project 15
(Python) played as that track's capstone.

## How to grade

1. Read the candidate's diff to `src/services/expenseReportService.ts`,
   `src/controllers/expenseReportController.ts`, and
   `src/routes/expenseReports.ts` (and any other files they touched — flag
   if they touched `expenseReportRepository.ts`, `userRepository.ts`,
   `attachUser.ts`, or `requireRole.ts` without justification; those four
   are correct in the starting code).
2. Copy `hidden_tests/expenseReportsHidden.test.ts` into
   `candidate/tests/` and run `npm test` from `candidate/` after applying a
   candidate's fix. All public + hidden tests should pass for a fully
   correct submission (27 total: 19 public + 8 hidden).
3. Compare their `approveReport`/`rejectReport` fix and `delegateApproval`
   implementation against `reference_solution/` and `bug_design.md`'s
   "Acceptable fixes" section — several phrasings are fine, only the
   semantics matter.
4. Specifically check whether the authorization check inside
   `approveReport`/`rejectReport` recognizes `delegatedApproverId` in
   addition to `assignedManagerId` (the tempting-but-incomplete trap — see
   `bug_design.md`), and whether both `approveReport` and `rejectReport`
   were fixed consistently (not just one of the twin functions). These are
   graded by the dedicated "Generalization / consistency" rubric category,
   independent of whether the literal bug fix and literal feature request
   are otherwise correct.
5. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of root cause, verification, and why the
   fix generalizes.
6. Score with `scoring_rubric.md`.
7. Ask 3-5 questions from `DEBRIEF.md` — this project's README explicitly
   tells the candidate to be ready for design follow-up questions as part
   of the deliverable, so budget time for this, not just a fixed 2-3.

## Interview-realism audit (private)

1. **Format simulated:** Capstone AI-assisted debugging + feature OA —
   trace a coarse-vs-resource-level authorization gap through a small,
   unfamiliar multi-layer Express/TypeScript service, then implement a
   feature that tests whether the candidate's own fix generalizes to code
   they write themselves. The integrated final assessment of this Node
   track (Projects 16-20).
2. **Role level:** Backend / new grad+ to mid-level, deliberately the
   hardest in this track (Project 16, the same track's first project, is
   6/10; this is 8.5/10).
3. **Why feasible in 60-90 min despite the difficulty:** The bug is a
   two-function, missing-comparison gap in one service file, each function
   five lines long; the feature is a small, well-scoped addition following
   a request/response pattern already visible three times over
   (`createReport`, `approveReport`, `rejectReport`). What makes this hard
   isn't code volume — five small files total, fully synchronous, no
   database, no real auth system — it's that the correct solution requires
   recognizing one underlying invariant ("only the assigned manager, its
   delegate, or an admin may act on this report") and applying it
   consistently across two existing methods and one new one the candidate
   writes from scratch. A candidate who reads `approveReport` carefully
   should locate the bug in 15-25 minutes; the harder, higher-signal part
   is whether they then extend that same check to `delegatedApproverId`
   once they've built delegation, without being told to.
4. **Signal obtained:** Whether the candidate can (a) distinguish a coarse
   role gate from a resource-level authorization check and correctly
   diagnose which one is missing, (b) rule out plausible alternative
   explanations using evidence already in the repo (the role-gate-works
   test, the correct `assignedManagerId` data visible via `GET`), and (c) —
   the capstone-specific signal — recognize and apply a general invariant
   consistently across multiple call sites, including new code they write
   themselves, rather than treating "the reported bug" and "the requested
   feature" as unrelated tasks.
5. **Coding vs. reasoning split:** ~30% coding (a small authorization check
   added to two existing methods + one new method/route + tests), ~70%
   reasoning/verification — comparable to Project 15's split, with the
   reasoning spread across three call sites (`approve`, `reject`,
   `delegate`) instead of one, which is what makes it the hardest project
   in this track despite a comparable amount of code.
6. **Would a top company use a close variant:** Yes — "a coarse
   role-based gate is correctly implemented but a resource-level check on
   top of it is missing, plus a same-shaped feature request that tempts the
   same mistake" is an extremely realistic capstone/onsite-round shape:
   authorization bugs of exactly this class (role-correct,
   record-incorrect) are one of the most common real backend vulnerability
   patterns, and "we just added delegation and it needs the same check" is
   exactly how these gaps propagate in real codebases.
7. **Anything included for production education rather than signal?** No —
   the header-based `X-User-Id` stand-in for authentication exists only so
   the exercise doesn't need a real auth system to test resource-level
   authorization; it's necessary scenario plumbing, not a lesson in
   authentication for its own sake, the same way Project 7's equivalent
   stand-in was scoped in the Python track.

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, identify the
defect, implement the requested feature, and fix everything." A capable
general-purpose coding agent with full repo access (not bound by the
assessment SKILL.md) can plausibly diagnose and fix the literal
`approveReport`/`rejectReport` bug in one shot — the failing tests plus two
five-line functions with an unused parameter are a strong, localized
signal, similar to Project 15's `finish_job` finding.

The part an ungoverned agent is **not** guaranteed to get right on a single
pass is exactly this project's central signal: whether it extends the
authorization check inside `approveReport`/`rejectReport` to also recognize
`delegatedApproverId` once it builds the delegation feature, or writes the
more "obvious-looking" version that only checks `assignedManagerId` and
lets `delegateApproval` set a field nothing else reads. This is a genuine,
non-trivial judgment call even for a capable agent, which is part of why
this project is well-suited as this track's capstone rather than an early
project — the interview signal isn't just "can the AI find the bug," it's
"does the candidate (with or without AI assistance) recognize that a fix
and a feature they're about to build share a root cause, and build the new
thing correctly the first time." Under the assessment SKILL.md, the
assistant is additionally constrained not to hand over the diagnosis or the
implementation outright, which restores the intended signal on the literal
bug-finding side as well. See `ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.

## Validation performed during authoring

- Ran `npm test` on the buggy/incomplete candidate starting code:
  **4 failed, 15 passed** (19 total) — exactly the four tests encoding the
  reported bug (one service-level and one HTTP-level test per
  approve/reject) plus the not-yet-implemented delegate endpoint's public
  test; every other public test, including "rejects approval from a plain
  employee" (confirming the coarse role gate itself works) and "lets an
  admin approve any report" (confirming the admin override already works
  even in the buggy code, since the buggy code checks nothing at all),
  passed.
- Applied `reference_solution/expenseReportService.ts`,
  `expenseReportController.ts`, and `expenseReports.ts` to a temporary copy
  of the candidate repo, copied `hidden_tests/expenseReportsHidden.test.ts`
  in, and ran `npm test`: **27 passed** (19 public + 8 hidden).
- Constructed the tempting-but-incomplete fix (authorization check added to
  `approveReport`/`rejectReport` checking only `assignedManagerId`, with
  `delegateApproval` implemented and functioning as a field-setter but
  never consulted by the approve/reject check) in a second temporary copy,
  with the same hidden tests copied in, and ran `npm test`: **2 failed, 25
  passed** — the two hidden tests directly targeting the un-generalized
  check (`delegated approval — approve path` and `delegated approval —
  reject path`, one per twin function); every other hidden test and all 19
  public tests passed, confirming those two are the only tests capable of
  distinguishing the incomplete fix from the correct one.
- Restored `candidate/` to its original state (it was never modified
  in-place — all validation ran against temporary copies under
  `scratchpad/`) and re-ran `npm test`: confirmed the split is exactly
  **4 failed, 15 passed**, unchanged from the first run.
- Reviewed every candidate-visible comment in `candidate/src/` against the
  fresh-solver-simulation lesson learned across this curriculum (comments
  that restate a business rule or design rationale in language too close to
  the fix or the generalization requirement are spoilers): all comments
  were written purely mechanically (state what a field/function/class IS or
  does structurally — e.g. "in-memory store," "thin controller" — never why
  a rule exists or what the correct authorization behavior should be). See
  `ai_skill_audit.md`'s leakage audit for the file-by-file review.
- Grepped the finished `.ai/assessment-skill/SKILL.md` for "Python",
  "FastAPI", and "Pydantic": zero matches, confirming it was copied from
  Project 16's already-genericized version rather than authored fresh or
  copied from a Python-track project.

No separate isolated fresh-solver agent session was spawned for this
specific project during authoring (this authoring session performed the
self-review and validation steps above directly, applying the leakage and
comment-discipline conventions earlier fresh-solver simulations across this
curriculum established, rather than discovering them after the fact). A
full independent solve by an isolated agent with only
`candidate/README.md`, `candidate/.ai/assessment-skill/SKILL.md`, and repo
access is a reasonable additional validation step before high-stakes use,
following the same pattern Projects 1, 9, and 15 used.

## Why this is a fitting Node-track capstone

Coarse-vs-resource-level authorization — a role check that's correct for
what it checks, paired with a missing per-record check that should sit
somewhere else — is one of the most common real backend vulnerability
classes, distinct in shape from an unscoped repository query (the closest
prior authorization-themed exercise in this curriculum, Python Project 7):
there, the data layer leaked across tenants; here, the data and the coarse
gate are both correct in isolation, and the gap is a check that was simply
never written at the layer responsible for it. Every other project in this
Node track (Projects 16-19) asks the candidate to find and fix *one*
thing. This project instead requires recognizing that a single
authorization invariant applies to two existing methods and one the
candidate must write from scratch under the same discipline — the
delegation feature specifically tests whether the candidate's fix
generalizes rather than just patches the one reported instance. Difficulty
8.5/10 reflects that gap, not extra code volume — this project has fewer
files than most of the earlier projects in the track.
