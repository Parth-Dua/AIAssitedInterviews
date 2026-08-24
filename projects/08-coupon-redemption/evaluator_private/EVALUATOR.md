# Evaluator Guide — Project 8: Coupon Redemption

## Format & target
Debugging + Feature Implementation. SWE Intern / New Grad / Backend.
60-75 min. Difficulty 7/10.

## How to grade

1. Read the candidate's diff to `app/services/coupon_service.py` (and any
   other files they touched — flag if they touched unrelated files, e.g.
   the repository layer's defensive-copy behavior, or response schemas).
2. Copy `hidden_tests/test_coupon_hidden.py` into `candidate/tests/` and
   run `pytest -q` from `candidate/`. All public + hidden tests should
   pass for a fully correct fix-plus-feature.
3. Compare their fix against `reference_solution/coupon_service.py` and
   `bug_design.md`'s "Acceptable fixes" / "Acceptable implementations"
   sections — several phrasings are fine, only the semantics matter.
4. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of root cause, fix, and feature design.
5. Score with `scoring_rubric.md`.
6. Ask 2-3 questions from `DEBRIEF.md`.

## Interview-realism audit (private)

1. **Format simulated:** AI-assisted debugging + feature-implementation OA
   / mid-stage backend interview.
2. **Role level:** Intern / new grad / early-career backend.
3. **Why feasible in 60-75 min:** The bug fix is a small, single-method
   reordering once the candidate reads `coupon_service.py` next to
   `coupon_repository.py` (both short files); the failing tests reproduce
   the exact reported scenario. The feature is a small, well-scoped
   addition of one `if` branch to `apply_discount`. A candidate who reads
   carefully should locate the bug in 15-25 minutes and complete the
   feature in another 10-15, leaving time to test and explain.
4. **Signal obtained:** Whether the candidate can read unfamiliar service
   code next to its repository, recognize a "mutated after handoff to a
   copy-on-write store" pattern as the actual defect (not just "wrong
   output"), verify a fix from a *fresh, independent read* rather than
   trusting a call's own return value, and correctly handle a numeric
   boundary condition (clamping) in the new feature that the obvious
   manual test cases don't surface.
5. **Coding vs. reasoning split:** ~30% coding (a small reordering plus a
   three-line feature branch), ~70% reasoning/verification — understanding
   why `save()`'s defensive copy makes the ordering matter at all, and
   recognizing that the naive unclamped implementation looks completely
   correct until tested against the right edge case.
6. **Would a top company use a close variant:** Yes — "a status
   transition doesn't persist because it's applied after the object was
   already saved, and the store defensively copies on write" is a
   realistic backend bug (any ORM/cache/repository that snapshots on
   write can produce it), and "add a second option to a business rule,
   with a numeric edge case at the boundary" is an extremely common
   feature-request shape.
7. **Anything included for production education rather than signal:** No
   — the in-memory repository stands in for a real datastore only to
   avoid building actual persistence infrastructure that would be
   orthogonal to the tested skill, not as a lesson in itself.

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, identify the
coupon redemption defect, and implement the requested fixed-amount
discount type." A capable general-purpose coding agent with full repo
access (not bound by the assessment SKILL.md) can plausibly solve most of
this in one or two passes — the bug is a small, local reordering once the
repository's `save()`/`get_by_code()` methods are read, and the feature is
a three-line branch. The subtlest part (the clamp-to-zero edge case) is
exactly the kind of boundary condition a capable model would get right by
default reasoning through "must never return a negative total," but is
also exactly the kind of thing a rushed human candidate skips because
every "obvious" manual test case (a modest discount against a normal
order) happens to pass without it.

This is expected and acceptable for a *Level 2 (harder debugging + code
modification)* project — the interview signal here is not "can the AI
find it" but "can the candidate direct their assistant well, verify
persisted state from a fresh read rather than trusting a call's own
return value, and think through the edge case that separates the
tempting implementation from the correct one." Under the assessment
SKILL.md, the assistant is constrained not to hand over the diagnosis or
the fix, which restores the intended signal: the candidate still has to
drive reproduction, hypothesis confirmation, and verification themselves.
See `ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.

## Fresh solver simulation (validation record)

Run per rule 34: an isolated agent received only `candidate/README.md`,
`candidate/.ai/assessment-skill/SKILL.md`, and repo access — no bug design,
hidden tests, reference solution, or evaluator notes. Result: it correctly
diagnosed the mutate-after-defensive-copy-save root cause, explicitly
recognized the bug is invisible in the redeem response and only shows via a
fresh read, and correctly implemented the clamped fixed-amount discount
without disturbing percentage behavior — all in an estimated 35-50 minutes,
inside the 60-75 minute timebox.

**Finding that caused a revision:** it flagged `CouponRepository`'s
docstring as "very close to a direct hint" — the original wording ("mutating
a `Coupon` object a caller happens to be holding can never silently change
what's persisted, and vice versa — the stored record only ever changes via
an explicit `save()` call") explains the defensive-copy design in terms
close enough to the bug's exact mechanism (mutate-after-save doesn't
persist) that it meaningfully shortens the investigation. **Fix applied:**
trimmed the docstring to state only the legitimate, necessary fact (copies
are returned, not live references) without narrating the save-ordering
consequence. Public test pass/fail split re-verified unchanged (6 failed /
8 passed) after the edit. Test docstrings describing expected behavior
(e.g. "a fresh repository read must show the coupon as exhausted") were
left as-is — the solver noted these as fair since they state requirements,
not the fix mechanism, consistent with how prior projects' test docstrings
have been judged.

It confirmed it never accessed anything outside `candidate/`. (Its edits to
`candidate/` were reverted after the simulation, then the docstring fix was
applied and re-validated, restoring the original buggy/incomplete starting
state.)
