# Evaluator Guide — Project 3: Profile Settings API

## Format & target
AI-Assisted Debugging Assessment. SWE Intern / New Grad / Backend. ~45-60 min.
Difficulty 6/10.

## How to grade

1. Read the candidate's diff to `app/services/profile_service.py` (and any
   other files they touched — flag if they touched unrelated files).
2. Copy `hidden_tests/test_profile_hidden.py` into `candidate/tests/` and run
   `pytest -q` from `candidate/`. All public + hidden tests should pass for a
   fully correct fix — pay particular attention to
   `test_patch_explicit_null_clears_nullable_field`, which is the test that
   separates a correct `exclude_unset=True` fix from the tempting
   `exclude_none=True` fix.
3. Compare their fix against `reference_solution/profile_service.py` and
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
   A candidate who reads the service function and the request schema
   carefully should locate the mechanism in 15-25 minutes, leaving time to
   fix, test, and explain the `exclude_unset` vs. `exclude_none` distinction.
4. **Signal obtained:** Whether the candidate can read unfamiliar CRUD code,
   connect a plain-English bug report to a specific library-semantics gap,
   and produce a fix that is correct in a subtler sense than "makes the
   given test pass" — i.e., whether they understand *why* the fix works
   well enough to not fall for the exclude_none trap.
5. **Coding vs. reasoning split:** ~25% coding (a 1-line fix + maybe a few
   tests), ~75% reasoning/verification — slightly more reasoning-heavy than
   Project 1 because the tempting wrong fix requires the candidate to think
   past "the given test now passes."
6. **Would a top company use a close variant:** Yes — "implement/fix a PATCH
   partial-update endpoint" is an extremely common real-world task and the
   `exclude_unset`/`exclude_none`/plain-`model_dump()` distinction is a
   genuine, frequently-hit Pydantic/FastAPI gotcha, not a contrived trick.
7. **Anything included for production education rather than signal:** No —
   the in-memory repository is included only to remove database setup as a
   distraction, not as a lesson in itself.

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, identify the defect,
and fix it." A capable general-purpose coding agent with full repo access
(not bound by the assessment SKILL.md) can plausibly locate and patch the
*reported* symptom in one shot — the failing test and the small surface
area make that easy. However, an agent working quickly is also plausibly
tempted toward `exclude_none=True` (it "obviously" fixes the visible
symptom and is a common first instinct), and would only be caught by
actually writing and running a null-clearing test case, which a
shortcut-taking agent may skip. This makes the exercise mildly
AI-trivialization-resistant even in an unguarded setting, and strongly
resistant under the guarded SKILL.md.

This is expected and acceptable for a *Level 3 (subtle library-semantics)*
project — the interview signal here is not "can the AI find it" but "can
the candidate direct their assistant well, push past a plausible-looking
fix, and verify against the *actual* stated invariant (only explicitly-sent
fields change) rather than just the one reported symptom." Under the
assessment SKILL.md, the assistant is constrained not to just hand over the
diff and is instructed to discuss concepts like `exclude_unset` only in
generic terms, which restores the intended signal: the candidate still has
to drive reproduction, hypothesis confirmation, and verification — including
thinking of and testing the null-clearing edge case — themselves. See
`ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade the
candidate's diff, tests, and explanation only.
