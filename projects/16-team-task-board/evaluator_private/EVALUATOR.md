# Evaluator Guide — Project 16: Team Task Board API

## Format & target
AI-Assisted Debugging Assessment. SWE Intern / New Grad / Backend. ~45-60
min. Difficulty 6/10 — calibrated to Amazon-style repo-based debugging OAs
(first project of the Node/Express track; template for Projects 17-20).

## How to grade

1. Read the candidate's diff to `src/services/taskService.ts` (and any other
   files they touched — flag if they touched unrelated files, e.g.
   `taskRepository.ts` or the `GET`/`POST` routes).
2. Copy `hidden_tests/taskHidden.test.ts` into `candidate/tests/` and run
   `npm test` from `candidate/` after applying a candidate's fix. All
   public + hidden tests should pass for a fully correct fix.
3. Compare their fix against `reference_solution/` and `bug_design.md`'s
   "Acceptable fixes" section — several phrasings are fine (service-layer
   validation vs. a new middleware), only the semantics matter.
4. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of root cause and verification.
5. Score with `scoring_rubric.md`.
6. Ask 2-3 questions from `DEBRIEF.md`.

## Interview-realism audit (private)

1. **Format simulated:** Amazon-style repo-based debugging OA — a small,
   unfamiliar multi-layer Express/TypeScript service, a plain-English bug
   report, public tests that partially reproduce it, hidden tests that
   probe for an incomplete fix.
2. **Role level:** Intern / new grad / early-career backend (SDE1-leaning).
3. **Why feasible in 45-60 min:** Single-field root cause in one function,
   four small supporting files (route, one middleware, controller,
   repository) that are each trivial to read, two failing tests (one unit,
   one HTTP) that already reproduce the bug precisely. A candidate who
   reads `updateTask` carefully should locate it in 10-20 minutes, leaving
   time to fix, close the validation gap, test, and explain.
4. **Signal obtained:** Whether the candidate can read unfamiliar
   Express/TypeScript middleware-controller-service-repository code, trace
   a request through several thin layers, connect a plain-English bug
   report to a specific line, rule out a plausible-but-wrong hypothesis by
   actually reading the relevant file, and produce a fix that's both
   correct *and* doesn't stop at the first green test run.
5. **Coding vs. reasoning split:** ~30% coding (a 1-2 line fix in the merge
   + a small validation addition + a test or two), ~70%
   reasoning/verification.
6. **Would a top company use a close variant:** Yes — "trace a PATCH
   request through an Express service's layers, a user complained one
   field silently doesn't update, find and fix it, and don't stop at the
   surface fix" is a very common Amazon-style OA/phone-screen shape for
   backend/full-stack roles.
7. **Anything included for production education rather than signal:** No —
   the in-memory `Map` repository, the thin controller, and the
   class-based service are included only because they're the minimal
   realistic shape of a small Express service, not as a lesson in Express
   idioms for their own sake.

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, identify the
defect, and fix it." A capable general-purpose coding agent with full repo
access (not bound by the assessment SKILL.md) can plausibly find and fix
the literal hardcoded-`status` line in one shot, since the two failing
tests pin it down precisely — this mirrors Project 1's finding for the
equivalent Python fundamentals-tier project. What is *not* trivially
one-shotted even by an unconstrained agent is the second half: recognizing
and closing the validation gap (no enum check on `PATCH`) that the naive
fix leaves open, since nothing in the repo or the failing tests points at
it directly — only the hidden test does, which the agent doesn't have
access to. This is expected and acceptable for a *Level 1-2 (Node-track
fundamentals)* project: the interview signal is not "can the AI find the
literal line" but "can the candidate direct their assistant well, verify
the suggested fix against the stated invariant, and — critically — think
past the first green test run to what else the change might have opened
up." Under the assessment SKILL.md, the assistant is constrained not to
just hand over the diff, which restores the intended signal: the candidate
still has to drive reproduction, hypothesis confirmation, and verification
themselves, including deciding whether "the test passes now" actually means
"the bug is fully fixed." See `ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.
