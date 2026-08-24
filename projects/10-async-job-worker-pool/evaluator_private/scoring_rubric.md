# Scoring Rubric — Project 10 (100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the API → `JobService.run_batch` → `worker_loop` → `JobBatchTracker` flow, and read `JobQueue` closely enough to rule it out, before editing. |
| Debugging process | 15 | Reproduced the bug via the failing test (or an equivalent manual repro / added logging), used the passing "call count" test as evidence against the off-by-one hypothesis, before making changes; didn't shotgun-edit multiple files. |
| Root-cause reasoning | 20 | Correctly identifies the `await` sitting between the read and the write of `self._remaining[batch_id]` in `mark_job_done` as a real suspension point that lets two workers interleave; can articulate why this causes a *lost update*, and why it never shows up with a single worker. |
| Correctness of fix | 25 | Public test passes; all hidden tests pass, including the generalization test (different job/worker counts) and the concurrent-distinct-batches test; `call_count` invariant untouched; no new `await` reintroduced inside the critical section. |
| Tests added/improved | 10 | Added at least one regression test beyond the given failing one (e.g. a different job_count/num_workers combination, or a concurrent-multiple-batches case), or meaningfully strengthened existing coverage. |
| Scope discipline | 5 | Did not modify unrelated files/behavior (API shape, `JobQueue`, `worker_loop`'s external contract) without justification; did not introduce real threads, processes, or real sleeps. |
| Communication / explanation | 15 | Can clearly state expected vs. actual behavior, root cause (in terms of `await` = suspension point, not "async is buggy"), why the fix is correct, and what they checked to rule out breaking other behavior. Can explain in their own words why a single-threaded `asyncio` program can still race. |

**Passing bar (strong mid-level+ signal):** ≥75, all hidden tests pass, and
candidate can explain root cause without prompting.

**Red flags:**
- Fix passes the given public test but fails
  `test_new_lock_per_call_does_not_provide_exclusion` — i.e. added a lock
  that provides no real exclusion (see `bug_design.md`, "Tempting but
  incomplete/wrong fix"). This is the single most important trap to check
  for in this project.
- Fix passes the public test and the generalization hidden test but fails
  `test_concurrent_distinct_batches_do_not_cross_contaminate` — usually
  means the candidate introduced a bug in how the lock/critical section is
  keyed (e.g. accidentally sharing one counter across batch_ids), not just
  a coarser-but-correct global lock (which is fine and should NOT be
  penalized).
- Candidate cannot explain *why* the bug happened, only that adding
  `asyncio.Lock()` somewhere made the test pass.
- Candidate introduces real threading/multiprocessing primitives
  (`threading.Lock`, `multiprocessing`, real `time.sleep`) — unnecessary
  for this exercise and a sign of not understanding the actual (asyncio
  cooperative-scheduling) mechanism at play.
- Candidate rewrites large parts of the service "to be safe" (e.g.
  restructuring `JobService` or `JobQueue`, which were not buggy).
