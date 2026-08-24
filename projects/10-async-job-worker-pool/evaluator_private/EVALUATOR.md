# Evaluator Guide — Project 10: Async Job Worker Pool

## Format & target
Advanced AI-Assisted Debugging Assessment. Backend / Mid-level+. ~60-90 min.
Difficulty 8/10. Second and final project of the "advanced interview
debugging / backend reasoning" tier (Projects 9-10), and the first project
in the suite involving real `asyncio` concurrency.

## How to grade

1. Read the candidate's diff to `app/services/job_batch_tracker.py` (and
   any other files they touched — flag if they touched `job_queue.py`,
   `worker.py`, or `job_service.py` without clear justification; those
   were not buggy).
2. Copy `hidden_tests/test_job_worker_hidden.py` into `candidate/tests/`
   and run `pytest -q` from `candidate/` (use `python3 -m pytest -q` if
   `pytest` on PATH doesn't resolve the environment with `pydantic`/
   `fastapi`/`pytest-asyncio` installed). All public + hidden tests should
   pass for a fully correct fix. Run it more than once — a correct fix
   should be perfectly deterministic; if you see any flakiness, that is
   itself a signal something is off (e.g. a candidate introduced real
   timing dependence).
3. Compare their fix against `reference_solution/job_batch_tracker.py`
   (reorder — no `await` in the critical section) and
   `reference_solution/job_batch_tracker_lock_variant.py` (shared
   instance-level lock) and `bug_design.md`'s "Acceptable fixes" section —
   both shapes are fully acceptable; only the semantics matter (no
   suspension point between reading and writing `self._remaining[batch_id]`
   for a given batch without exclusion).
4. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of root cause and verification.
5. Score with `scoring_rubric.md`.
6. Ask 2-3 questions from `DEBRIEF.md`.

## Interview-realism audit (private)

1. **Format simulated:** AI-assisted debugging OA / mid-level+ debugging
   interview, specifically probing async/concurrency reasoning.
2. **Role level:** Backend / mid-level+ (not entry-level — this assumes
   comfort reading `async`/`await` code, but not specialist distributed-
   systems background).
3. **Why feasible in 60-90 min:** Single-file root cause
   (`job_batch_tracker.py`, ~35 lines), three small supporting files that
   mostly serve to rule out alternative hypotheses, one clear failing test
   that reproduces the exact reported scenario, and a passing test that
   pre-empts the most likely wrong hypothesis (off-by-one in the worker
   loop). A candidate who reads `mark_job_done` carefully should locate the
   race in 25-40 minutes, leaving time to fix, test, and explain.
4. **Signal obtained:** Whether the candidate understands that `asyncio`'s
   single-threaded, cooperative model can still have race conditions at
   `await` points, can locate the specific unsynchronized critical section
   from a plain-English bug report plus a failing test, and can produce a
   fix that is correct (not just "looks like it added locking").
5. **Coding vs. reasoning split:** ~25% coding (a small reorder or a
   3-4 line lock addition, plus a test or two), ~75% reasoning/
   verification — this project weighs conceptual understanding of
   `asyncio` scheduling more than raw code volume.
6. **Would a top company use a close variant:** Yes — "here's an async
   worker pool, a customer-visible symptom, find the race and fix it
   without over-engineering a distributed solution" is a realistic
   mid-level+ backend interview or OA shape, especially at companies with
   async Python services (FastAPI, aiohttp, background job processors).
7. **Anything included for production education rather than signal:** No
   — `asyncio.sleep(0)` is used specifically because it's the only way to
   make the race window both real (a genuine suspension point) and
   perfectly deterministic/non-flaky for automated grading; it is not
   there to teach a lesson about `sleep(0)` itself.

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, identify the
defect, and fix it." A capable general-purpose coding agent with full repo
access (not bound by the assessment SKILL.md) can plausibly locate and fix
the primary race in one or two shots — the file is short and the failing
test pins the symptom down precisely. However, the *tempting-but-wrong*
fix (a new `asyncio.Lock()` per call) is a fix a model can plausibly
propose confidently without checking whether it actually changes anything,
since "added a lock" pattern-matches to "fixed the concurrency bug" without
verifying exclusivity. The hidden test
`test_new_lock_per_call_does_not_provide_exclusion` exists precisely to
catch this even when a candidate's assistant (or the candidate themselves)
is fooled by that surface-level pattern match.

This is expected and, under the assessment SKILL.md, mitigated the same
way as in earlier projects: the assistant is constrained not to hand over
the diagnosis or the fix outright, which preserves the intended signal —
the candidate must still drive reproduction, hypothesis testing (including
verifying their own fix actually removes the race, not just that "a lock"
is present), and explanation themselves. See `ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.

## Fresh solver simulation (validation record)

Run per rule 34: an isolated agent received only `candidate/README.md`,
`candidate/.ai/assessment-skill/SKILL.md`, and repo access — no bug design,
hidden tests, reference solution, or evaluator notes. Result: it correctly
diagnosed the lost-update race (await sitting between read and write of
`_remaining`, no lock), correctly ruled out the off-by-one hypothesis using
the `call_count` evidence, and fixed it with a per-batch `asyncio.Lock`
(one of the two documented acceptable fixes). It independently re-verified
determinism across 8+ runs both before and after its fix, with zero
flakiness observed, confirming the design goal from the build brief. Time
estimate: 30-60 minutes for a candidate with light asyncio exposure —
inside the 60-90 minute timebox.

No leakage or realism issues were found; it explicitly called out that
`JobBatchTracker`'s docstring ("finalized exactly once... regardless of how
many workers are reporting completions... at the same time") is a fair,
necessary specification of the class's contract rather than a hint — the
same judgment call made and validated on Project 1's pricing-rules
docstring precedent. No revisions to the exercise were needed.

It confirmed it never accessed anything outside `candidate/`. (Its edits to
`candidate/` were reverted after the simulation, restoring the original
buggy starting state, re-verified at 1 failed / 5 passed.)
