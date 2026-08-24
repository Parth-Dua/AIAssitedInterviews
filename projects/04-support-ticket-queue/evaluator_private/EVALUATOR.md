# Evaluator Guide — Project 4: Support Ticket Queue

## Format & target
AI-Assisted Debugging Assessment. SWE Intern / New Grad / Backend. ~45-60
min. Difficulty 6/10 — the hardest of the fundamentals tier (Projects 1-4):
it requires recognizing a specific, well-known but easy-to-miss Python
behavior (mutable default arguments) and reasoning about shared mutable
state, not just spotting a one-line logic swap.

## How to grade

1. Read the candidate's diff to `app/services/ticket_service.py` (and any
   other files they touched — flag if they touched unrelated files).
2. Copy `hidden_tests/test_ticket_hidden.py` into `candidate/tests/` and run
   `pytest -q` from `candidate/`. All public + hidden tests should pass for
   a fully correct fix, including the caller-list-mutation test.
3. Compare their fix against `reference_solution/ticket_service.py` and
   `bug_design.md`'s "Acceptable fixes" section — several phrasings are
   fine, only the semantics matter (no shared default across calls, no
   caller-list mutation).
4. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of root cause and verification.
5. Score with `scoring_rubric.md`.
6. Ask 2-3 questions from `DEBRIEF.md`.

## Interview-realism audit (private)

1. **Format simulated:** AI-assisted debugging OA / first-round debugging
   interview.
2. **Role level:** Intern / new grad / early-career backend.
3. **Why feasible in 45-60 min:** Single-function root cause, three small
   supporting files, two clear failing tests that together reproduce both
   angles of the reported bug. A candidate who reads `create_ticket`
   carefully — and who either knows or can look up the mutable-default
   gotcha — should locate it in 15-25 minutes, leaving time to fix, test,
   and explain, including the caller-mutation subtlety.
4. **Signal obtained:** Whether the candidate can read unfamiliar business
   logic, connect a plain-English bug report to code, recognize a specific
   Python language pitfall rather than just a business-logic slip, and
   produce a minimal correct fix that doesn't just replace one form of
   shared-state bug with another.
5. **Coding vs. reasoning split:** ~25% coding (a small, targeted fix to
   one function + maybe a test), ~75% reasoning/verification — slightly
   more reasoning-heavy than Projects 1-3 because the "obvious" fix
   (`None` sentinel) is necessary but not sufficient.
6. **Would a top company use a close variant:** Yes — "here's a function
   with a subtly wrong default argument causing shared state across
   requests, a user reported weird cross-contamination, find and fix it"
   is a genuinely common OA/phone-screen and code-review shape, and the
   mutable-default-argument pitfall specifically is one of the most
   frequently cited real-world Python gotchas.
7. **Anything included for production education rather than signal:** No —
   the auto-watch-email business rule exists only to give the default
   argument a reason to be mutated in the first place (so the bug is
   *triggered*, not just latent); it isn't itself a lesson.

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, identify the
defect, and fix it." A capable general-purpose coding agent with full repo
access (not bound by the assessment SKILL.md) can plausibly solve the
*first* layer of this bug (the shared default) in one shot, since the two
failing tests pin down the symptom precisely and a mutable default argument
is a well-known pattern most coding agents are trained to recognize.
However, the *second* layer — that the `None`-sentinel fix must also avoid
mutating a caller-supplied list — is easy for an agent to miss too unless
explicitly prompted to think about it, since none of the public tests
exercise it (only a hidden test does). This makes the exercise somewhat
more AI-resistant than Projects 1-3: even an unconstrained agent has a
plausible path to a fix that looks complete but isn't.

This is expected and acceptable for a *Level 4 (last of the fundamentals
tier)* project — the interview signal here is not "can the AI find it" but
"can the candidate direct their assistant well, recognize when a fix
suggested by the assistant might be incomplete, and verify it against the
stated invariant rather than just against the two tests they already know
about." Under the assessment SKILL.md, the assistant is additionally
constrained not to just hand over the diff, which restores the intended
signal for candidates using an assistant: they still have to drive
reproduction, hypothesis confirmation, and verification themselves. See
`ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.

## Fresh solver simulation (validation record)

Run per rule 34: an isolated agent received only `candidate/README.md`,
`candidate/.ai/assessment-skill/SKILL.md`, and repo access — no bug design,
hidden tests, reference solution, or evaluator notes. Result: it correctly
diagnosed the mutable-default-argument root cause (including the caller-list-
mutation subtlety) and implemented a fully correct fix (all public + its own
added regression tests passed) in an estimated 15-25 minutes of investigation
— comfortably inside the 45-60 minute timebox. It confirmed the README/SKILL
did not hint at the answer and that the failing-test evidence was sufficient
to diagnose without guessing. It confirmed it never accessed anything outside
`candidate/`. One incidental finding: in its sandbox, plain `pytest` resolved
to a different Python environment than the installed deps, requiring
`python3 -m pytest`; this is a generic environment quirk (now noted in the
root `CURRICULUM.md`), not a flaw in this exercise. No revisions to the
exercise were needed as a result of this simulation. (Its edits to
`candidate/` were reverted after the simulation to restore the original
buggy starting state.)
