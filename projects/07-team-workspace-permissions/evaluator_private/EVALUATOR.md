# Evaluator Guide — Project 7: Team Workspace Permissions

## Format & target
Debugging + Feature Implementation. SWE Intern / New Grad / Backend.
60-75 min. Difficulty 7/10.

## How to grade

1. Read the candidate's diff to `app/services/permission_service.py` and
   `app/models/schemas.py` (and any other files they touched — flag if
   they touched unrelated files, e.g. the repository layer or response
   schemas).
2. Copy `hidden_tests/test_permissions_hidden.py` into `candidate/tests/`
   and run `pytest -q` from `candidate/`. All public + hidden tests should
   pass for a fully correct fix-plus-feature.
3. Compare their fix against `reference_solution/permission_service.py`
   and `reference_solution/schemas.py`, and `bug_design.md`'s "Acceptable
   fixes" / "Acceptable implementations" sections — several phrasings are
   fine, only the semantics matter.
4. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of root cause, fix, and feature design.
5. Score with `scoring_rubric.md`.
6. Ask 2-3 questions from `DEBRIEF.md`.

## Interview-realism audit (private)

1. **Format simulated:** AI-assisted debugging + feature-implementation OA
   / mid-stage backend interview.
2. **Role level:** Intern / new grad / early-career backend.
3. **Why feasible in 60-75 min:** The bug fix is a small, single-method
   change once the candidate reads `permission_service.py` next to
   `membership_repository.py` (both short files); the failing tests
   reproduce the exact reported scenario. The feature is a one-line schema
   change plus a small, well-scoped edit to two authorization methods. A
   candidate who reads carefully should locate the bug in 15-25 minutes
   and complete the feature in another 15-20, leaving time to test and
   explain.
4. **Signal obtained:** Whether the candidate can read unfamiliar
   authorization logic, recognize an unscoped-query pattern as a
   multi-tenant security bug (not just a "wrong output" bug), fix it
   without regressing an adjacent legitimate capability, and extend the
   permission model correctly under a subtle ordering constraint (viewer
   check must precede the ownership shortcut).
5. **Coding vs. reasoning split:** ~35% coding (a small, targeted fix plus
   a small feature addition), ~65% reasoning/verification — locating the
   right method among several similarly-named ones, understanding why the
   naive complete fix (owner_id only) is wrong, and reasoning about check
   ordering for the new role.
6. **Would a top company use a close variant:** Yes — "a role check isn't
   scoped to the right tenant/resource, a customer is hitting privilege
   escalation across accounts/workspaces, fix it and add a new
   restricted role" is an extremely common real-world backend bug and
   follow-up feature shape, especially in B2B SaaS.
7. **Anything included for production education rather than signal:** No
   — the `X-User-Id` header stand-in for real auth is included only to
   avoid building a real auth system that would be orthogonal to the
   tested skill, not as a lesson in itself.

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, identify the
authorization defect, and implement the requested viewer role." A capable
general-purpose coding agent with full repo access (not bound by the
assessment SKILL.md) can plausibly solve most of this in one or two passes
— the bug is a single clearly-misused repository method, and the feature
is a schema change plus a symmetric edit to two short functions. The
subtlest part (viewer-check-must-precede-ownership-check) is exactly the
kind of thing a capable model would get right by default reasoning through
the "regardless of any other condition" requirement in the README, but
also exactly the kind of thing a rushed human candidate skips.

This is expected and acceptable for a *Level 2 (harder debugging + code
modification)* project — the interview signal here is not "can the AI find
it" but "can the candidate direct their assistant well, catch the
overcorrection trap by actually running the given public tests, and
explain why the workspace-owner escape hatch needed to be scoped rather
than removed." Under the assessment SKILL.md, the assistant is constrained
not to hand over the diagnosis or the fix, which restores the intended
signal: the candidate still has to drive reproduction, hypothesis
confirmation, and verification themselves. See `ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.

## Fresh solver simulation (validation record)

Run per rule 34: an isolated agent received only `candidate/README.md`,
`candidate/.ai/assessment-skill/SKILL.md`, and repo access — no bug design,
hidden tests, reference solution, or evaluator notes. Result: it correctly
diagnosed the unscoped-role-lookup root cause (immediately noticing
`can_manage_document` used `get_memberships_for_user` where its siblings
used the correctly-scoped `get_membership`), correctly implemented the
viewer role without overcorrecting (explicitly kept the
workspace-owner-manages-any-document-in-their-workspace behavior and added
its own regression test for it), and did so in an estimated 35-50 minutes —
inside the 60-75 minute timebox. No spoiler issues were found this time —
it explicitly noted the docstring ambiguity on `can_manage_document` reads
as intentional subtlety rather than a leak, and confirmed the failing-test
evidence was fully sufficient without hints. It confirmed it never accessed
anything outside `candidate/`. No revisions to the exercise were needed.
(Its edits to `candidate/` were reverted after the simulation, restoring
the original buggy/incomplete starting state, re-verified at 3 failed / 10
passed.)
