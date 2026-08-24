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

## Fresh solver simulation (validation record)

Run per rule 34 (and this project's own build brief, which required the same
standard for the new Node track): an isolated agent received only
`candidate/README.md`, `candidate/.ai/assessment-skill/SKILL.md`, and repo
access — no bug design, hidden tests, reference solution, or evaluator
notes. Result: it correctly diagnosed the hardcoded `status: existing.status`
root cause and fixed it, in an estimated 15-25 minutes — comfortably inside
the 45-60 minute timebox. It deliberately did NOT add status-enum
validation, reasoning (correctly, per the README's own scope-discipline
wording) that doing so unprompted would be scope creep beyond the reported
bug — and explicitly flagged the gap as a discussion point rather than
silently leaving it. This is a legitimate candidate judgment call, not a
defect in the exercise: `scoring_rubric.md` and `DEBRIEF.md` already treat
"did the candidate proactively raise the validation gap, even if their PR
doesn't close it" as a real (if partial) signal, so this outcome was
already anticipated.

**Findings that caused revisions (both applied and re-verified, README-only
and SKILL.md-only, no code touched):**
1. `.ai/assessment-skill/SKILL.md`, which is otherwise Project 1's exact
   text reused across the whole suite, still carried two references to
   "Python, FastAPI, Pydantic" from that Python-track origin — inert here
   (not a leak, since they don't reference the bug) but a confusing
   copy-paste artifact in a Node/TypeScript project, and worth fixing before
   this became the copy-template for Projects 17-20. **Fix applied:**
   genericized both to stack-neutral wording ("the language, framework, or
   library syntax... used in this repository"; "a partial-update check,"
   dropping "in Pydantic"). This restores the property that the SKILL.md
   body is truly byte-for-byte reusable across both the Python and Node
   tracks, not just within one track.
2. The README claimed "One test currently fails" but two fail (one
   unit-level, one HTTP-level, both encoding the same bug). **Fix applied:**
   corrected to "Two tests currently fail (one unit-level, one HTTP-level)
   — both encode the same reported bug."

Public test pass/fail split re-verified unchanged (2 failed / 10 passed)
after both edits — neither touched candidate code.

It confirmed it never accessed anything outside `candidate/`. (Its edits to
`candidate/` were reverted after the simulation, then the README/SKILL.md
fixes were applied and re-validated, restoring the original buggy starting
state.)
