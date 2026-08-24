# Evaluator Guide — Project 5: Inventory Reservations

## Format & target
AI-Assisted Debugging + Feature Implementation Assessment. SWE Intern / New
Grad / Backend. ~60-75 min. Difficulty 6/10.

## How to grade

1. Read the candidate's diff across
   `app/api/routes/reservations.py`, `app/services/reservation_service.py`,
   and `app/repositories/reservation_repository.py` (and any other files
   they touched — flag if they touched unrelated files, e.g. `main.py` or
   the seed data).
2. Copy `hidden_tests/test_reservations_hidden.py` into `candidate/tests/`
   and run `pytest -q` from `candidate/`. All public + hidden tests should
   pass for a fully correct submission (12 total: 8 public + 4 hidden).
3. Compare their bug fix and feature implementation against
   `reference_solution/` and `bug_design.md`'s "Acceptable fixes" /
   "Acceptable implementations" sections — several phrasings are fine, only
   the semantics matter (filter before paginate; strict cursor boundary).
4. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of root cause, feature design, and
   verification.
5. Score with `scoring_rubric.md`.
6. Ask 2-3 questions from `DEBRIEF.md`, covering both the bug and the
   feature.

## Interview-realism audit (private)

1. **Format simulated:** AI-assisted debugging-plus-feature OA / first or
   second-round backend interview. This is deliberately a step up from a
   pure debugging exercise (Project 1/2) — one reported bug plus one
   requested feature sharing the same code path.
2. **Role level:** Intern / new grad / early-career backend.
3. **Why feasible in 60-75 min:** Small, three-file execution path; the
   bug is a single-character boundary fix with a clear failing test; the
   feature requires touching the same three files but each change is small
   (add a param, thread it, add a filter). A candidate who reads carefully
   should find the bug in 15-20 minutes and have 30-45 minutes left for the
   feature plus tests.
4. **Signal obtained:** Whether the candidate can (a) diagnose a
   cursor-pagination boundary bug from a plausible bug report, and (b)
   design and implement a filter that composes correctly with existing
   pagination — specifically, recognizing that filter-then-paginate and
   paginate-then-filter are *not* equivalent, which is a common real-world
   mistake with list/search APIs.
5. **Coding vs. reasoning split:** ~40% coding (a 1-line bug fix + a small,
   three-file feature), ~60% reasoning/design/verification — slightly more
   coding-weighted than the pure-debugging tier (Projects 1-4), consistent
   with this being an "implementation" type project.
6. **Would a top company use a close variant:** Yes — "here's a pagination
   endpoint with a subtle boundary bug, and here's a filter the product
   team wants added to it" is an extremely common backend interview and
   real-sprint-ticket shape.
7. **Anything included for production education rather than signal:** No —
   the integer `sequence` field (in place of real timestamps) exists only
   to keep tests deterministic, not as a lesson in itself; it's called out
   explicitly in the README/model docstring so it doesn't read as an
   unexplained quirk.

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, fix the reported
bug, and implement the requested category filter." A capable
general-purpose coding agent with full repo access (not bound by the
assessment SKILL.md) can plausibly one-shot the pagination bug (a clear
failing test pins it down precisely) but is meaningfully more likely to
reach for the filter-after-paginate implementation for the feature, since
it is the more "obvious" one-line addition to already-working pagination
code and looks correct on a quick single-page check — the agent would need
to specifically reason about (or be prompted to verify) full-traversal
correctness under a filter to avoid it. This is exactly the signal this
project is designed to capture.

This is expected and acceptable for a *Level 2 (harder debugging + code
modification)* project — the interview signal is not "can the AI find the
bug" but "does the candidate direct their assistant to verify end-to-end
behavior (not just page 1) once a filter is added, and can they explain
why filter-order matters." Under the assessment SKILL.md, the assistant is
constrained not to hand over the diff outright, which restores the
intended signal: the candidate still has to drive the design decision and
verify it themselves. See `ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.
