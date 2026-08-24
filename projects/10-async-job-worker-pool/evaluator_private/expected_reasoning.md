# Expected Reasoning Path

1. Run `pytest -q`; observe
   `test_multi_worker_batch_finalizes_once_when_all_jobs_complete` fails
   while everything else passes.
2. Read the assertion: `tracker.call_count("batch-3") == 2` passes (both
   jobs really were processed), but `result.remaining` is not `0` and
   `result.finalize_count` is not `1` — the batch's completion never got
   marked, even though both jobs finished.
3. Notice `test_mark_job_done_called_exactly_job_count_times` and
   `test_single_worker_batch_finalizes_exactly_once` both pass — this
   rules out "the worker loop isn't calling `mark_job_done` enough times"
   and confirms the bug only shows up with more than one worker sharing a
   batch.
4. Trace the execution path: `POST /batches/run` → `JobService.run_batch`
   (seeds the queue, spins up `num_workers` copies of `worker_loop` via
   `asyncio.gather`) → `worker_loop` (pulls a job, does a fake unit of
   work, calls `tracker.mark_job_done(job.batch_id)` once) →
   `JobBatchTracker.mark_job_done`.
5. Read `job_queue.py` and notice it's a thin, correct wrapper around
   `asyncio.Queue` (which is itself coroutine-safe) — this should rule out
   "maybe the queue is delivering the same job twice" or "the queue is
   dropping jobs" as a cause.
6. Read `job_batch_tracker.py::mark_job_done` closely and notice: it reads
   `self._remaining[batch_id]` into a local variable, then `await`s
   (`asyncio.sleep(0)`), *then* decrements the local variable and writes it
   back. Recognize that the `await` is a real point where another task can
   run — specifically, another worker's own call to `mark_job_done` for
   the *same* `batch_id` — before this one writes its decremented value
   back.
7. Reason through (or instrument/log) what happens with 2 workers and 2
   jobs for the same batch: both workers can read the same starting
   `remaining` value before either has written back, so one decrement gets
   lost — `remaining` never reaches `0`, so the `if remaining == 0:` check
   never fires, so the batch never finalizes. This matches the report
   ("every job completed but the batch never finalized") precisely.
8. Fix it — either by removing the `await` from the read-modify-write
   critical section entirely (reordering so the "simulate work" yield
   happens after the state update), or by protecting the whole critical
   section with a single shared `asyncio.Lock()` created once on the
   tracker instance (not a new lock per call).
9. Re-run tests; confirm the previously-failing test now passes, and the
   rest still pass. Add or strengthen a test with different
   job_count/num_workers numbers to confirm the fix isn't just tuned to
   the original failing test's exact values, and ideally a test with
   several concurrent distinct batches.
10. Explain: this is a lost-update race on a shared counter, made possible
    because `await asyncio.sleep(0)` is a genuine (if delay-free)
    suspension point in `asyncio`'s cooperative scheduler — not because
    of real threads or wall-clock timing.

A strong candidate reaches step 6-7 within 25-35 minutes given the failing
test and the passing "call count" test as starting evidence.

## Anti-pattern to watch for

A candidate who "fixes" this by adding `async with asyncio.Lock():` but
constructs a *new* `Lock()` object inside `mark_job_done` on every call has
not actually fixed anything — every call gets its own uncontended lock, so
there is no real mutual exclusion, and the batch will still fail to
finalize under this exercise's tests. This should read as a genuine
misunderstanding of what a lock protects (shared state must be protected
by *one* shared lock instance, not a fresh one per critical-section entry),
not as a stylistic quibble.
