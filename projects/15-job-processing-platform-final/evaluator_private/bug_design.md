# Bug + Feature Design (private — do not expose to candidate)

This project bundles a state-corruption bug and a feature-implementation
task that share the same underlying invariant, so they're documented
together. This is the capstone (Project 15 of 15) and is intentionally the
hardest exercise in the suite.

## Lifecycle recap

```
queued --start--> running --finish(result)--> completed
   \                             \---finish(error)--> failed
    \--cancel--> cancelled
```

`completed`, `failed`, and `cancelled` are all terminal. `Job` fields: `id`,
`status`, `payload`, `result`, `error`, `attempt_count`.

## Part A — The duplicate-finish state-corruption bug

### Expected behavior
A job's status may only transition `running -> completed` or
`running -> failed` **exactly once**. Any subsequent `finish_job` call for a
job that is not currently `"running"` — including a second call for a job
that is already `"completed"` or `"failed"` — must be rejected, not
silently accepted. This matters because the worker fleet's callback
delivery is at-least-once, not exactly-once (established in the candidate
README's Scenario section): a duplicate or delayed "job finished" callback
is a realistic, expected occurrence, not an edge case that can be ignored.

### Actual (buggy) behavior
`app/services/job_service.py::JobService.finish_job` in the starting code:

```python
def finish_job(self, job_id: str, result: str | None, error: str | None) -> Job:
    job = self._repository.get(job_id)
    if job.status != "running" and job.status == "queued":
        raise InvalidJobStateError(job_id, job.status)
    job.status = "completed" if result is not None else "failed"
    job.result = result
    job.error = error
    self._repository.save(job)
    return job
```

### Root cause — the exact boolean-logic error

The guard is `job.status != "running" and job.status == "queued"`. Walk
through both branches:

- If `job.status == "queued"`: then `job.status != "running"` is trivially
  `True` (queued is not running), so the guard reduces to
  `True and True == True` — the guard fires and the call is (correctly)
  rejected. But the first clause did no real work here; it was always
  going to be `True` whenever the second clause was `True`.
- If `job.status` is anything **other than** `"queued"` (including
  `"running"`, `"completed"`, or `"failed"`): the second clause
  `job.status == "queued"` is `False`, and `False` short-circuits the
  `and` to `False` regardless of what the first clause evaluates to — so
  the guard **never fires**, no matter what the first clause says.

In other words, `(A and B)` where `B` implies `A` (here, `status == "queued"`
implies `status != "running"`) is logically equivalent to just `B` alone.
The clause `job.status != "running"` is dead weight that makes the
condition *look* like it's checking two things, when it's actually only
ever checking one: `job.status == "queued"`. The guard therefore only ever
rejects finishing a job that hasn't started yet — it does **not** reject
finishing a job that has already reached a terminal state. A second
`finish_job` call on an already-`"completed"` (or `"failed"`) job sails
straight through, overwrites `job.result`/`job.error` with whatever the
second call sent, and returns success.

### Violated invariant
"A job's status may only transition `running -> terminal` (`completed` /
`failed`) exactly once; any subsequent `finish` call for a job that is not
currently `running` must be rejected, not silently accepted." (Implied
directly by the bug report and the README's at-least-once-delivery
background.)

### Relevant execution path
`POST /jobs/{id}/finish` (`app/api/routes/jobs.py`) →
`JobService.finish_job` (`app/services/job_service.py`, the bug) →
`JobRepository.get` / `.save` (`app/repositories/job_repository.py`,
correct — must be read to rule out a repository-level explanation) → `Job`
dataclass (`app/domain/job.py`, correct). `app/workers/export_worker.py`
(correct, deterministic) is a separate, unrelated module that must be read
and ruled out as the source of the "wrong result" symptom.

### Evidence available to the candidate
- The failing public test
  `test_job_service.py::test_duplicate_finish_does_not_overwrite_completed_result`
  reproduces the exact reported scenario: finish a job once (correct
  result persists), finish it again with a different result, and assert
  the *first* result is still what's stored and the second call is
  rejected.
- The passing public test
  `test_job_service.py::test_finish_queued_job_that_never_started_is_rejected`
  establishes that *some* guard already exists and already works for one
  case — this rules out "there's no validation at all" as the shape of the
  problem and should redirect a candidate toward "the guard exists but is
  incomplete," not "add a guard from scratch."
- The passing public `test_export_worker.py` tests establish the worker
  function is deterministic, directly ruling out Hypothesis 1 below.
- Reading `job_service.py::finish_job` line by line and manually
  evaluating the boolean guard for `status in {"queued", "running",
  "completed", "failed", "cancelled"}` (a truth table) reveals it only
  ever evaluates `True` for `"queued"`.

### Reasonable hypotheses

1. **(Wrong) The worker's result-computation logic is non-deterministic** —
   maybe the same job re-processed by a worker just computes a different
   result each time, which would explain "the result changed" without any
   bug in the finish endpoint at all. Ruled out: `compute_export_result` in
   `app/workers/export_worker.py` is a pure function of `payload` only — no
   randomness, no timestamps, no I/O — and the public
   `test_export_worker.py` tests confirm this by calling it directly in
   isolation and asserting the same payload always yields the same
   string. This module is entirely unrelated to the `finish_job` bug.

2. **(Wrong) The repository has a save/aliasing bug that loses the first
   write** — maybe `JobRepository.save` doesn't really persist, or hands
   back a stale/copied reference, so the *first* `finish_job` call's write
   never actually lands and only the second one "sticks," which could also
   look like "the result changed." Ruled out: the first `finish_job` call's
   result is immediately visible via `GET /jobs/{id}` (exercised by every
   happy-path test in the suite) — the problem only appears when
   `finish_job` is called a **second** time for the same job. Reading
   `job_repository.py` also shows `save` and `get` both operate directly on
   a single dict keyed by `job.id`, with no copying or aliasing involved.

3. **(Correct) `finish_job`'s status guard has a boolean-logic bug.** The
   condition `job.status != "running" and job.status == "queued"` only ever
   rejects the `"queued"` case (see Root cause above); it does not reject
   `"completed"` or `"failed"`.

### Intended regression tests
`test_duplicate_finish_does_not_overwrite_completed_result` (already
present as a public test) plus the hidden
`test_duplicate_finish_after_failed_is_also_rejected`, which generalizes
the check to the `"failed"` terminal state — this catches a narrow fix that
happens to special-case `"completed"` only (e.g. `if job.status ==
"completed": raise ...`) instead of fixing the general "not currently
running" rule.

### Acceptable fixes
- `if job.status != "running": raise InvalidJobStateError(job_id, job.status)`
  — the direct fix, checking the one condition that actually needs
  checking.
- Equivalent: `if job.status == "queued" or job.status in ("completed",
  "failed", "cancelled"): raise ...` — more verbose, same semantics, as
  long as it rejects every non-`"running"` status. (Note: once `cancel_job`
  is added, `"cancelled"` becomes a real status `finish_job` must also
  reject — the more precise `!= "running"` version handles this
  automatically and doesn't need updating when `"cancelled"` is
  introduced, which is a small but real advantage a strong candidate may
  notice.)
- Not acceptable: any fix that only special-cases `"completed"` (fails the
  hidden `"failed"`-generalization test) or that changes the meaning of the
  `"queued"` rejection (must still reject finishing a never-started job).

### Stretch-goal design observation (not required for a passing fix)
A single inline boolean per method (as in the starting code, and as in the
minimal one-line fix above) is easy to get subtly wrong, as this bug
demonstrates. A more robust design defines, once, which source statuses are
valid preconditions for each transition — e.g. a small mapping like
`{"start": {"queued"}, "finish": {"running"}, "cancel": {"queued"}}` — and
has each method look itself up in that table rather than hand-writing a
boolean each time. This doesn't change the correct *behavior* for this
exercise, and is not required for a passing solution; it's worth
mentioning if a candidate raises it (see `DEBRIEF.md`) as a sign of
forward-looking design thinking, not as a scored requirement — grade the
behavior, not the presence of this refactor.

## Part B — The cancellation feature, and its own version of the same trap

### Requested behavior
`POST /jobs/{id}/cancel`: a job may only be cancelled while it is still
`"queued"`. Once a worker has started it (`"running"`) or it has reached
any terminal state (`"completed"`, `"failed"`, or already `"cancelled"`),
cancellation must be rejected with a clear error — this system does not
support interrupting an in-progress job. A cancelled job must behave as
terminal going forward: attempting to `start` or `finish` a cancelled job
must be rejected, exactly like any other terminal state.

### Starting (missing) state
There is no `cancel_job` method on `JobService` and no
`POST /jobs/{id}/cancel` route at all in the starting code — this is a
feature to add from scratch, not a bug to fix in existing code. The
candidate must add both the service method and the route.

### Tempting but incomplete/wrong implementation
Implement `cancel_job` with **no status guard at all** — mirroring the
*shape* of the original `finish_job`/`start_job` bugs, just in the new
method instead of an existing one:

```python
def cancel_job(self, job_id: str) -> Job:
    job = self._repository.get(job_id)
    job.status = "cancelled"
    self._repository.save(job)
    return job
```

This "solves" the literal reported bug (duplicate finish is now correctly
rejected, assuming `finish_job` was fixed properly) and adds a
working-seeming cancel endpoint that passes the naive public test
(`test_cancel_queued_job_is_accepted`, which only ever cancels a freshly
created, still-`"queued"` job). It fails every hidden test that checks
cancellation is rejected once the job has moved past `"queued"`:
`test_cancel_running_job_is_rejected`,
`test_cancel_completed_job_is_rejected`,
`test_cancel_failed_job_is_rejected`,
`test_cancel_already_cancelled_job_is_rejected`, and the API-level
`test_api_cancel_running_job_returns_409`.

This is the central point of the exercise: does the candidate recognize
that the **same underlying invariant** — "only transition out of a status
that's a valid precondition for this transition; every other status must
be rejected" — needs to be enforced consistently across `finish_job`,
`start_job`, and the new `cancel_job`? Or do they fix only the literally-
reported spot (`finish_job`) and then write `cancel_job` fresh, without
recognizing it needs the exact same kind of guard they just added
elsewhere in the same file?

**Validated:** applying this exact unconditional `cancel_job` to a
temporary copy of the candidate repository (with `finish_job` correctly
fixed to `if job.status != "running": raise ...`, and `start_job` left
exactly as the original starting code — unguarded — to also exercise the
secondary gap below), with `hidden_tests/test_jobs_hidden.py` copied in,
and running `pytest -q`, produced **8 failed, 12 passed**. The 12 passes
included all 9 original public tests (in particular, both
`test_duplicate_finish_does_not_overwrite_completed_result` and
`test_cancel_queued_job_is_accepted` now pass) plus the hidden
`test_duplicate_finish_after_failed_is_also_rejected`. The 8 failures were
exactly: `test_cancel_running_job_is_rejected`,
`test_cancel_completed_job_is_rejected`,
`test_cancel_failed_job_is_rejected`,
`test_cancel_already_cancelled_job_is_rejected`,
`test_api_cancel_running_job_returns_409`,
`test_start_already_completed_job_is_rejected`,
`test_api_start_already_completed_job_returns_409`, and
`test_cancelled_job_cannot_be_started_or_finished` — exactly the hidden
tests targeting the un-generalized `cancel_job` and the pre-existing
`start_job` gap, and nothing else.

### Acceptable implementations
- `cancel_job` guards with `if job.status != "queued": raise
  InvalidJobStateError(job_id, job.status)` before setting
  `status = "cancelled"`.
- `reference_solution/job_service.py` implements exactly this, and also
  fixes `start_job` to guard with `if job.status != "queued": raise ...`
  (see Part C).

## Part C — The secondary `start_job` guard gap

`start_job` in the starting code has **no status guard at all** — it
unconditionally sets `status = "running"` and increments `attempt_count`
regardless of current status. This is real and should be fixed, but it is
intentionally *not* the headline bug: calling `start` on an already-
`"running"` job doesn't corrupt anything user-visible by itself (the
status was already `"running"`), so it has no obviously bad visible
symptom the way `finish_job`'s bug does, and there is no public test that
fails because of it. Calling `start` on an already-`"completed"` job,
however, *is* a real problem — it would incorrectly flip a finished job
back to `"running"`, silently un-finishing it. A thorough candidate who has
correctly generalized "guard every transition against its valid
preconditions" should notice and fix this too. It's graded via the hidden
`test_start_already_completed_job_is_rejected` and
`test_api_start_already_completed_job_returns_409` as a **generalization /
partial-credit** signal, not a public, guaranteed-to-fail-first bug — see
`scoring_rubric.md`'s dedicated "generalization" category.

## Why this is interview-appropriate

A boolean guard that *looks* like it covers every invalid precondition but
actually only covers one, because of a redundant clause that silently
implies the other — `(A and B)` where `B` already implies `A` — is a very
common, realistic, and appropriately hard defect: it reads as intentional
and thorough at a glance, and a candidate has to actually trace the truth
table rather than pattern-match "oh, there's a guard, must be fine."
Pairing it with a same-shaped feature request (a new endpoint tempting the
candidate to write the exact same class of missing-guard mistake fresh) is
what makes this a fitting capstone: it isn't one clever bug, it's
recognizing *one* underlying invariant — status-guarded transitions — and
applying it consistently across three call sites (`start`, `finish`,
`cancel`) rather than three independent, unrelated fixes. No specialist
knowledge required — fully discoverable from the code, the failing tests,
and the README's stated at-least-once-delivery and cancellation-scope
background.
