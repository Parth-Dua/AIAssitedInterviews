# Evaluator Guide — Project 15: Job Processing Platform (Capstone)

## Format & target
AI-Assisted Debugging + Feature Assessment. Backend / Mid-level+. ~75-90
min. Difficulty 9/10 — the hardest exercise in this 15-project suite.

## How to grade

1. Read the candidate's diff to `app/services/job_service.py` and
   `app/api/routes/jobs.py` (and any other files they touched — flag if
   they touched `job_repository.py`, `job.py`, or `export_worker.py`
   without justification; those three are correct in the starting code).
2. Copy `hidden_tests/test_jobs_hidden.py` into `candidate/tests/` and run
   `pytest -q` from `candidate/`. All public + hidden tests should pass
   for a fully correct submission (20 total: 9 public + 11 hidden).
3. Compare their `finish_job` fix and `cancel_job` implementation against
   `reference_solution/` and `bug_design.md`'s "Acceptable fixes" /
   "Acceptable implementations" sections — several phrasings are fine,
   only the semantics matter.
4. Specifically check whether `cancel_job` has a real status guard or is
   unconditional (the tempting-but-incomplete trap — see `bug_design.md`
   Part B) and whether `start_job` was also fixed (the secondary,
   partial-credit gap — see Part C). These are graded by the dedicated
   "Generalization / consistency" rubric category, independent of whether
   the literal bug fix and literal feature request are otherwise correct.
5. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of root cause, verification, and why
   the fix generalizes.
6. Score with `scoring_rubric.md`.
7. Ask 3-5 questions from `DEBRIEF.md` — this project's README explicitly
   tells the candidate to be ready for design follow-up questions as part
   of the deliverable, so budget time for this, not just a fixed 2-3.

## Interview-realism audit (private)

1. **Format simulated:** Capstone AI-assisted debugging + feature OA /
   senior-adjacent mid-level backend debugging interview — the integrated
   final assessment of a 15-project curriculum.
2. **Role level:** Backend / mid-level+, deliberately harder than every
   other project in the suite (Projects 9 and 10, the prior "advanced" tier,
   are 8/10; this is 9/10).
3. **Why feasible in 75-90 min despite the difficulty:** The bug is a
   single-method, single-line boolean-logic error in one service file; the
   feature is a small, well-scoped addition following an existing
   route/service pattern already visible three times over (`create`,
   `start`, `finish`). What makes this hard isn't code volume — it's
   fully sequential and deterministic, no concurrency, no database, five
   small files total — it's that the correct solution requires recognizing
   one underlying invariant and applying it consistently across three call
   sites, one of which (`cancel_job`) the candidate writes themselves from
   nothing. A candidate who reads `finish_job` carefully should locate the
   bug in 15-25 minutes; the harder, higher-signal part is whether they
   then write `cancel_job` with the same rigor they just applied to the
   fix, without being told to.
4. **Signal obtained:** Whether the candidate can (a) trace a subtly wrong
   boolean condition to its precise logical flaw rather than pattern-
   matching a fix that merely makes one test pass, (b) correctly rule out
   plausible alternative explanations using evidence already in the repo,
   and (c) — the capstone-specific signal — recognize and apply a general
   invariant consistently across multiple call sites, including new code
   they write themselves, rather than treating "the reported bug" and "the
   requested feature" as unrelated tasks.
5. **Coding vs. reasoning split:** ~30% coding (a one-line guard fix, a new
   method + route, a guard for `start_job`, tests), ~70%
   reasoning/verification — similar split to Project 9, but the reasoning
   is spread across three call sites instead of one, which is what makes
   it the hardest project in the suite despite a comparable amount of code.
6. **Would a top company use a close variant:** Yes — "a status guard that
   looks complete but has a boolean-logic hole, plus a same-shaped feature
   request that tempts the same mistake" is an extremely realistic
   capstone/onsite-round shape: state-machine guards with subtly incomplete
   conditions are a common real production bug class (order/payment/job
   status machines especially), and "we just added a new transition and it
   needs the same guard" is exactly how these bugs propagate in real
   codebases.
7. **Anything included for production education rather than signal?** No —
   the at-least-once delivery framing (background needed to understand why
   duplicate `finish` calls are realistic, not contrived) is necessary
   scenario setup, established the same way Project 9's was; it's not a
   hint at *where* the fix lives, only *why* the scenario is realistic.

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, identify the
defect, implement the requested feature, and fix everything." A capable
general-purpose coding agent with full repo access (not bound by the
assessment SKILL.md) can plausibly diagnose and fix the literal
`finish_job` bug in one shot — the failing test plus a five-line function
is a strong, localized signal, similar to Project 9's `has_seen` gap.

The part an ungoverned agent is **not** guaranteed to get right on a single
pass is exactly this project's central signal: whether it writes
`cancel_job` with a real, consistent status guard, or writes the more
"obvious-looking" unconditional version that merely satisfies the one
naive public test. This is a genuine, non-trivial judgment call even for a
capable agent, which is part of why this project is well-suited as a
capstone rather than an early-tier exercise — the interview signal isn't
just "can the AI find the bug," it's "does the candidate (with or without
AI assistance) recognize the need to generalize a fix to code they are
about to write themselves." Under the assessment SKILL.md, the assistant
is additionally constrained not to hand over the diagnosis or the
implementation outright, which restores the intended signal on the literal
bug-finding side as well. See `ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.

## Why this is a fitting capstone

Every other project in this suite (Projects 1-14) asks the candidate to
find and fix *one* thing — a single bug, or a bug plus one feature that
happens to sit in a different part of the code. This project instead
requires recognizing that a single design principle ("a transition is only
valid from its one legal source status; guard every transition against
every other status") applies identically to three different methods, one
of which the candidate must write from scratch under the same discipline
they just used to fix a bug in a sibling method. That is a materially
different, harder cognitive task than diagnosing a single localized
defect: it's the difference between "fix what's broken" and "notice that
what you just fixed and what you're about to build share a root cause, and
build the new thing correctly the first time." Difficulty 9/10 reflects
that gap, not extra code volume — this project has fewer files and less
code than Project 7 or Project 9.

## Validation performed during authoring

- Ran `pytest -q` on the buggy/incomplete candidate starting code:
  **2 failed, 9 passed** — exactly
  `test_job_service.py::test_duplicate_finish_does_not_overwrite_completed_result`
  and `test_jobs_api.py::test_cancel_queued_job_is_accepted`, reproducing
  the reported bug and the missing feature; every other public test,
  including the "finish a never-started job is rejected" test confirming
  the partial existing guard already works for that one case, passed.
- Applied `reference_solution/job_service.py` and
  `reference_solution/jobs.py` to a temporary copy of the candidate repo,
  copied `hidden_tests/test_jobs_hidden.py` in, and ran `pytest -q`:
  **20 passed** (9 public + 11 hidden).
- Constructed the tempting-but-incomplete unconditional-`cancel_job`
  version (with `finish_job` correctly fixed and `start_job` left exactly
  as the original starting code, unguarded) in a second temporary copy,
  with the same hidden tests copied in, and ran `pytest -q`: **8 failed,
  12 passed** — see `bug_design.md` Part B for the exact list of which
  tests failed (all eight are hidden tests targeting the un-generalized
  `cancel_job` and the pre-existing `start_job` gap; nothing else
  regressed).
- Restored `candidate/` to its original state (it was never modified
  in-place — all validation ran against temporary copies) and re-ran
  `pytest -q`: confirmed the split is exactly **2 failed, 9 passed**,
  unchanged from the first run.
- Reviewed every candidate-visible docstring in `app/` against the
  fresh-solver-simulation lesson learned across this curriculum
  (docstrings that restate a business rule or design hint in language too
  close to the fix mechanism are spoilers): all `app/` docstrings were
  written purely mechanically from the start (state what a function/class
  does structurally, never why a rule exists or what the correct behavior
  should be) rather than authored first and trimmed after finding a leak.
  See `ai_skill_audit.md`'s leakage audit for the file-by-file review. No
  separate isolated fresh-solver agent session was run for this specific
  project during authoring (unlike Project 9's recorded run) — this
  self-review was done directly against the leakage standard that
  simulation established; a future full independent solve is a reasonable
  additional validation step before high-stakes use, but the docstring
  and business-rule placement conventions that past simulations flagged
  were applied preemptively here rather than discovered after the fact.
