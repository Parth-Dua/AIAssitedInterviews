# Expected Reasoning Path

## Bug fix (finish_job)

1. Run `pytest -q`; observe
   `test_job_service.py::test_duplicate_finish_does_not_overwrite_completed_result`
   and `test_jobs_api.py::test_cancel_queued_job_is_accepted` fail (2
   failed, 9 passed). Recognize these as two separate problems — a bug and
   a missing feature — not one issue.
2. Focus on the bug first. Read the failing test: finish a job once
   (result persists correctly), finish it again with a different result,
   expect the second call to be rejected and the first result to remain.
3. Open `app/services/job_service.py::finish_job`. Notice the guard:
   `if job.status != "running" and job.status == "queued": raise ...`.
4. Build a mental (or literal, on paper) truth table for
   `job.status in {"queued", "running", "completed", "failed"}` against
   this condition. Notice it only evaluates `True` for `"queued"` — the
   first clause is redundant whenever the second is true, and the `and`
   short-circuits to `False` for every other status.
5. Before committing to this hypothesis, rule out the two plausible
   alternatives:
   - Check `app/workers/export_worker.py` and its tests — confirm
     `compute_export_result` is a pure, deterministic function, unrelated
     to `finish_job`.
   - Check `app/repositories/job_repository.py` — confirm `save`/`get`
     don't alias or lose writes, and confirm (via the passing happy-path
     tests) that the *first* `finish_job` call's write is correctly
     visible before any second call happens.
6. Fix the guard to `if job.status != "running": raise
   InvalidJobStateError(job_id, job.status)`.
7. Re-run tests. The duplicate-finish test now passes. Manually reason
   through (or add a test for) the `"failed"`-terminal-state case too, not
   just `"completed"` — the fix must generalize to any non-`"running"`
   status, not just the one in the given failing test.

## Feature (cancel_job) — and recognizing the shared invariant

8. Read the README's feature request: cancel only while `"queued"`;
   rejected otherwise; cancelled is terminal.
9. Add `JobService.cancel_job` and wire `POST /jobs/{id}/cancel` in
   `app/api/routes/jobs.py`, following the existing route/service pattern
   for `start`/`finish`.
10. The key moment: recognize that `cancel_job` needs *the same kind of
    guard* just written for `finish_job` — reject from any status other
    than the one valid precondition (`"queued"`) — rather than writing an
    unconditional `status = "cancelled"` that happens to pass the one
    obvious public test (cancel a freshly created job).
11. A candidate who has fully internalized the underlying invariant should
    also notice `start_job` has no guard at all, and that this is the same
    class of gap (it just doesn't have an obvious failing public test
    pointing at it) — and fix it too: `if job.status != "queued": raise
    ...`.
12. Add tests: cancelling a running/completed/failed/already-cancelled job
    is rejected; a cancelled job can't later be started or finished;
    starting an already-completed job is rejected.
13. Re-run the full suite. Explain: the root cause was a boolean guard that
    only handled one of several invalid preconditions; the fix and the new
    feature both enforce the same rule — "a transition is only valid from
    its one legal source status" — applied consistently to `start`,
    `finish`, and `cancel`.

A strong candidate reaches step 6 (the finish_job fix) within roughly the
first third of the timebox, and reaches step 10-11 (recognizing the shared
invariant, not just patching the reported spot) within the remainder,
leaving time to add tests and prepare to explain generalization — the
single hardest thing this project is testing for.
