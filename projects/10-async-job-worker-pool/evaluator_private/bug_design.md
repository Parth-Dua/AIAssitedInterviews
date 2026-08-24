# Bug Design (private — do not expose to candidate)

## Expected behavior

A batch's completion must be finalized **exactly once**, precisely when
every one of its jobs has completed. Concurrently completing jobs for the
same batch must never lose or duplicate a decrement of the batch's
remaining-job counter. This holds regardless of how many workers are
processing the batch at once.

## Actual (empirically observed buggy) behavior

`app/services/job_batch_tracker.py::JobBatchTracker.mark_job_done` performs
a **read-then-await-then-write** on `self._remaining[batch_id]`:

```python
async def mark_job_done(self, batch_id: str) -> None:
    self._call_count[batch_id] = self._call_count.get(batch_id, 0) + 1

    remaining = self._remaining[batch_id]
    await asyncio.sleep(0)
    remaining -= 1
    self._remaining[batch_id] = remaining
    if remaining == 0:
        self._finalize_count[batch_id] = self._finalize_count.get(batch_id, 0) + 1
```

`await asyncio.sleep(0)` is a pure cooperative yield to the event loop —
no real delay — but it is still a genuine suspension point: any other
ready task (in this case, another worker calling `mark_job_done` for the
*same* `batch_id`) can run before this coroutine resumes. Two workers can
both read the same `remaining` value before either writes back the
decremented value, silently losing one decrement.

This was verified empirically (5+ runs each, byte-identical results every
time — CPython's asyncio event loop schedules a fixed sequence of
`asyncio.sleep(0)` yields deterministically, so this is not flaky):

| job_count | num_workers | `remaining` ends at | `finalize_count` ends at | `mark_job_done` call count |
|---:|---:|---:|---:|---:|
| 1 | 1 | 0 | 1 | 1 |
| 5 | 1 | 0 | 1 | 5 |
| 2 | 2 | **1** | **0** | 2 |
| 3 | 3 | **2** | **0** | 3 |
| 4 | 2 | **2** | **0** | 4 |
| 6 | 3 | **4** | **0** | 6 |

With exactly one worker, there is never a second task contending for the
same batch's counter, so the read-await-write sequence always completes
without interference — the single-worker case is always correct, matching
the bug report. With more than one worker sharing a batch, the observed
failure mode in every configuration tested is **the batch never finalizes**
(`finalize_count` stays `0`) and `remaining` gets stuck strictly above `0`
even though `mark_job_done` was called exactly `job_count` times. This
project's worded bug report ("the batch's completion doesn't fire even
though every job clearly finished") matches this exact, reproducible
symptom — not the "finalizes more than once" variant, which does not occur
with this queue/worker-loop shape (a worker's fast-path, non-suspending
`queue.get()` when the queue is non-empty, combined with `asyncio.gather`'s
task-creation order, consistently produces lost decrements, never a false
extra one).

## Root cause

A classic **check-then-act / lost-update race condition** on a shared
mutable counter (`JobBatchTracker._remaining[batch_id]`), caused by an
`await` sitting between the read and the write of that counter with no
synchronization protecting the critical section.

This is possible in `asyncio` despite it being single-threaded because
`asyncio`'s concurrency model is *cooperative*, not preemptive: the event
loop only ever switches which coroutine is running at an `await` point
that actually suspends. Two `await`-ing coroutines can still interleave
arbitrarily around such a point, exactly like two threads can interleave
around an unprotected memory access — the mechanism ("who can run between
my read and my write") is the same; only the reason a switch can happen
differs (explicit yield vs. preemption). `asyncio.Queue.get()` on a
non-empty queue does *not* suspend (it takes a synchronous fast path), so
it does not introduce this hazard — only the explicit
`await asyncio.sleep(0)` calls inside the workers' fake-work step and
inside `mark_job_done` do.

## Violated invariant

"A batch's completion must be finalized exactly once, precisely when every
one of its jobs has completed — concurrent job completions for the same
batch must not lose or duplicate a decrement."

## Relevant execution path

`POST /batches/run` (`app/api/routes/batches.py`) → `JobService.run_batch`
(`app/services/job_service.py`, orchestration only — seeds the queue,
starts `num_workers` copies of `worker_loop` via `asyncio.gather`, waits
for them to finish; **not buggy**) → `worker_loop`
(`app/services/worker.py`, pulls jobs and calls `mark_job_done` once per
job; **not buggy**) → `JobBatchTracker.mark_job_done`
(`app/services/job_batch_tracker.py`; **the bug**). `JobQueue`
(`app/services/job_queue.py`) wraps `asyncio.Queue`, which is itself
coroutine-safe — reading it should help a candidate rule out the queue as
a source of the problem.

## Evidence available to the candidate

- The failing public test
  `test_multi_worker_batch_finalizes_once_when_all_jobs_complete`
  reproduces the reported scenario with concrete, small numbers (2 jobs, 2
  workers) and shows `tracker.call_count(...) == 2` (all jobs really were
  processed) alongside `result.remaining != 0` and
  `result.finalize_count != 1`.
- The passing public test
  `test_mark_job_done_called_exactly_job_count_times` establishes that
  `mark_job_done` really is invoked once per completed job even with
  multiple workers, which rules out an off-by-one in the worker loop.
- The passing public test `test_single_worker_batch_finalizes_exactly_once`
  establishes the single-worker case is always correct, matching "the
  problem only shows up with multiple workers" from the bug report.
- Reading `job_batch_tracker.py` end-to-end reveals the `await` sitting
  between the read and the write of `self._remaining[batch_id]`.
- Reading `job_queue.py` shows `JobQueue` is a thin, correct wrapper around
  `asyncio.Queue` — nothing there explains a lost count.

## Documented hypotheses

1. **(Plausible, wrong)** "`mark_job_done` isn't actually being called once
   per completed job — an off-by-one in the worker loop." Ruled out by the
   passing test asserting `tracker.call_count(batch_id) == job_count` (and,
   separately, by reading `worker.py`, which calls `mark_job_done` exactly
   once per non-sentinel item it pulls off the queue).
2. **(Correct)** A race condition: concurrent calls to `mark_job_done` for
   the same `batch_id` interleave around the `await` inside it, causing a
   lost update to the shared `remaining` counter.

## Intended regression tests

- `test_multi_worker_batch_finalizes_once_when_all_jobs_complete` (public,
  already present — the exact reported scenario).
- Hidden: the same race reproduced with a different job_count/worker_count
  combination, to confirm a fix generalizes rather than special-casing the
  public test's numbers.
- Hidden: the tempting-but-incomplete "new lock per call" fix fails while
  both acceptable fixes pass (see below).
- Hidden: multiple different batches run concurrently don't cross-
  contaminate each other's counts under a correct fix.

## Acceptable fixes

1. **Reorder (preferred, simplest, most idiomatic):** compute the
   decrement, write it back, and do the finalize check — all synchronously,
   with no `await` in between — then do any "simulate work/persist
   progress" await afterward, once the state is already correctly updated.
   Since there is no suspension point between the read and the write, no
   other task can ever observe a stale value; this requires no lock at all.
   See `reference_solution/job_batch_tracker.py`.
2. **Shared, instance-level lock:** if there's a reason the await must stay
   inside the critical section (e.g. a real "persist progress" call that
   must complete before the decrement is considered durable), protect the
   whole read-modify-write-and-check block with a single `asyncio.Lock()`
   created once in `__init__` and held via `async with self._lock:` on
   every call. A single lock shared across *all* batches is coarser than
   necessary (it serializes unrelated batches' critical sections behind
   each other) but is still fully **correct** — it is not penalized by any
   test in this exercise. See
   `reference_solution/job_batch_tracker_lock_variant.py`.

Either fix must preserve: `remaining(batch_id)` ends at `0` and
`finalize_count(batch_id)` ends at exactly `1` for any batch that actually
had `job_count` calls to `mark_job_done`, for any `job_count` /
`num_workers` combination, including when multiple distinct batches run
concurrently.

## Tempting but incomplete/wrong fix

Adding "a lock" but instantiating a **new** `asyncio.Lock()` on every call,
inside `mark_job_done`, instead of reusing one shared instance-level lock:

```python
async def mark_job_done(self, batch_id: str) -> None:
    ...
    lock = asyncio.Lock()          # <- new, uncontended lock every call
    async with lock:
        remaining = self._remaining[batch_id]
        await asyncio.sleep(0)
        ...
```

This *looks* like a real fix — it "adds locking" — but provides **zero**
actual mutual exclusion: every call gets its own independent lock object,
so no two calls are ever contending for the same lock, and
`asyncio.Lock.acquire()` on an uncontended lock returns immediately without
suspending, so this doesn't even change the scheduling. Empirically
verified (5+ runs, byte-identical) to reproduce the *exact same* lost-
update numbers as the original bug for every job_count/num_workers
combination tested. Caught by
`hidden_tests/test_job_worker_hidden.py::test_new_lock_per_call_does_not_provide_exclusion`
(and, incidentally, also still fails the public
`test_multi_worker_batch_finalizes_once_when_all_jobs_complete` and the
other two hidden tests, since nothing about the race actually changed).

Flag this during review as a real red flag if a candidate ships it and
claims the batch-completion bug is fixed: it demonstrates they added
*something that looks like* synchronization without understanding *what*
a lock actually needs to share to provide exclusion.

## Why this is interview-appropriate

This does not require "deep specialist distributed-systems knowledge." It
requires: (a) recognizing that `await` is a real suspension point even
when the delay is zero, (b) noticing a read and a write of shared state
that have an `await` between them, and (c) knowing that either removing
the `await` from the critical section or protecting it with one shared
lock closes the window. All three are fully discoverable from the code
itself (`job_batch_tracker.py` is ~35 lines), the failing public test's
exact numbers, and the README's plain-English bug report — no knowledge of
threads, processes, distributed consensus, or real network/timing behavior
is needed, and the exercise explicitly rules those out as unnecessary in
both the README and the SKILL.md scope note. This is what distinguishes it
from genuinely distributed-systems-flavored problems: everything here is
one process, one event loop, fully deterministic, and fully reproducible
by running `pytest` — the "concurrency" is real but entirely mechanical
once a candidate understands that `await` is where control can change
hands.
