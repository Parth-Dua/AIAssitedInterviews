# Evaluator Guide — Project 1: OrderFlow Pricing Service

## Format & target
AI-Assisted Debugging Assessment. SWE Intern / New Grad / Backend. ~45-60 min.
Difficulty 5/10.

## How to grade

1. Read the candidate's diff to `app/services/pricing_service.py` (and any
   other files they touched — flag if they touched unrelated files).
2. Copy `hidden_tests/test_pricing_hidden.py` into `candidate/tests/` and run
   `pytest -q` from `candidate/`. All public + hidden tests should pass for a
   fully correct fix.
3. Compare their fix against `reference_solution/pricing_service.py` and
   `bug_design.md`'s "Acceptable fixes" section — several phrasings are fine,
   only the semantics matter.
4. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of root cause and verification.
5. Score with `scoring_rubric.md`.
6. Ask 2-3 questions from `DEBRIEF.md`.

## Interview-realism audit (private)

1. **Format simulated:** AI-assisted debugging OA / first-round debugging
   interview.
2. **Role level:** Intern / new grad / early-career backend.
3. **Why feasible in 45-60 min:** Single-file root cause, three small
   supporting files, one clear failing test that already reproduces the bug.
   A candidate who reads the service function carefully should locate it in
   10-20 minutes, leaving time to fix, test, and explain.
4. **Signal obtained:** Whether the candidate can read unfamiliar business
   logic, connect a plain-English bug report to code, and produce a minimal
   correct fix without breaking adjacent behavior.
5. **Coding vs. reasoning split:** ~30% coding (a 1-3 line fix + maybe a
   test), ~70% reasoning/verification.
6. **Would a top company use a close variant:** Yes — "read this pricing/fee
   function, a customer complained about X, find and fix it" is a very common
   OA/phone-screen shape.
7. **Anything included for production education rather than signal:** No —
   cents-based arithmetic is included only because it's the natural way to
   avoid distracting float bugs, not as a lesson in itself.

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, identify the defect,
and fix it." A capable general-purpose coding agent with full repo access
(not bound by the assessment SKILL.md) can plausibly solve this in one shot
since the bug is a single clear variable swap and the failing test pins it
down precisely.

This is expected and acceptable for a *Level 1-2 (fundamentals)* project —
the interview signal here is not "can the AI find it" but "can the candidate
direct their assistant well, verify the suggested fix against the stated
policy, and explain it." Under the assessment SKILL.md, the assistant is
constrained not to just hand over the diff, which restores the intended
signal: the candidate still has to drive reproduction, hypothesis
confirmation, and verification themselves. See `ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade the
candidate's diff, tests, and explanation only.
