# Evaluator Guide — Project 2: Library Loan Tracker

## Format & target
AI-Assisted Debugging Assessment. SWE Intern / New Grad / Backend. ~45-60 min.
Difficulty 5/10.

## How to grade

1. Read the candidate's diff to `app/repositories/loan_repository.py` (and
   any other files they touched — flag if they touched unrelated files,
   e.g. the model, the route, or the response schema).
2. Copy `hidden_tests/test_loans_hidden.py` into `candidate/tests/` and run
   `pytest -q` from `candidate/`. All public + hidden tests should pass for
   a fully correct fix (13 total: 7 public + 6 hidden).
3. Compare their fix against `reference_solution/loan_repository.py` and
   `bug_design.md`'s "Acceptable fixes" section — several phrasings are
   fine (a `coalesce`, an equivalent `case`, or a unioned two-branch
   query), only the semantics matter.
4. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of root cause and verification.
5. Score with `scoring_rubric.md`.
6. Ask 2-3 questions from `DEBRIEF.md`.

## Interview-realism audit (private)

1. **Format simulated:** AI-assisted debugging OA / first-round debugging
   interview.
2. **Role level:** Intern / new grad / early-career backend.
3. **Why feasible in 45-60 min:** One bug, confined to a single query in a
   single repository method; three small supporting files (route, service,
   model) that are correct but must be read to understand where
   `renewed_due_at` comes from; one clear failing test that already
   reproduces the bug with concrete dates. A candidate who reads the four
   files carefully should locate it in 15-25 minutes, leaving time to fix,
   test against edge cases, and explain.
4. **Signal obtained:** Whether the candidate can trace a request across an
   API → service → repository → ORM model stack, connect a plain-English
   bug report to a specific column the model already defines, and produce a
   minimal, boundary-correct SQL fix without breaking adjacent behavior
   (returned-loan exclusion, non-renewed loans, strict inequality at the
   boundary).
5. **Coding vs. reasoning split:** ~30% coding (a one-expression fix to a
   `where()` clause + maybe a test or two), ~70% reasoning/verification —
   slightly more multi-file tracing than Project 1 since the bug sits one
   layer deeper (repository, not service) and depends on noticing an unused
   model field.
6. **Would a top company use a close variant:** Yes — "a query wasn't
   updated when a new column/feature was added, read the model and the
   query and fix the drift" is an extremely common real-world bug shape and
   a natural OA/phone-screen exercise.
7. **Anything included for production education rather than signal:** The
   explicit `as_of` parameter (instead of `date.today()`) is included
   because it's the standard way to keep such a query testable, not as a
   lesson in itself — it also happens to be realistic (any real overdue
   report needs a deterministic "as of" date for scheduled jobs and
   backfills). The SQLAlchemy 2.0 `Mapped`/`mapped_column` style is used
   because it's the current idiomatic API, not to test unrelated ORM
   trivia.

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, identify the
defect, and fix it." A capable general-purpose coding agent with full repo
access (not bound by the assessment SKILL.md) can plausibly solve this in
one or two shots: the bug is a single missing `coalesce` in one `where()`
clause, and the failing test pins down the exact scenario precisely.

This is expected and acceptable for a *Level 1-2 (fundamentals)* project —
the interview signal here is not "can the AI find it" but "can the
candidate direct their assistant well, verify the suggested fix against
edge cases (a shortened loan, the boundary date, mixed loan states) that
aren't spelled out in the bug report, and explain it." Under the assessment
SKILL.md, the assistant is constrained not to just hand over the diff,
which restores the intended signal: the candidate still has to drive
reproduction, hypothesis confirmation, and verification themselves. See
`ai_skill_audit.md`.

A secondary trivialization risk specific to this project: an AI assistant
(or a candidate) might reach for the tempting-but-incomplete Python
post-filter fix (see `bug_design.md`) because it "sounds right" and passes
the one visible failing test. The hidden tests exist specifically to catch
this, and a candidate who blindly accepts an AI-suggested fix without
testing the shortened-loan edge case will fail hidden tests despite the
visible test passing — this is itself part of the intended signal (verify,
don't just trust).

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.
