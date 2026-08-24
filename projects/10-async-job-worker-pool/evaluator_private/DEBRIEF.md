# Interview Follow-Up Questions (private)

1. **Why can `asyncio` code have race conditions even though it's
   single-threaded?**
   Strong answer: `asyncio` is cooperatively scheduled — only one coroutine
   ever executes at a time, and the event loop only switches which
   coroutine is running at an `await` point that actually suspends. But
   between the moment a coroutine suspends and the moment it resumes,
   *any other ready task* can run, including one that reads or writes the
   same shared state. That's exactly what a race condition needs: two
   logical operations that can interleave around a shared piece of state.
   No real parallelism (multiple threads/cores executing simultaneously)
   is required for that — only the *possibility* of one operation being
   suspended in the middle of another.

2. **Why doesn't creating a new `asyncio.Lock()` per call actually protect
   anything?**
   Strong answer: a lock only provides mutual exclusion between callers
   that are contending for the *same lock object*. If every call to
   `mark_job_done` constructs its own, brand-new `Lock()`, no two calls are
   ever waiting on the same lock — each one always finds "its" lock
   unlocked and proceeds immediately, exactly as if there were no lock at
   all. To protect shared state, the lock has to be shared: created once
   (e.g. in `__init__`) and reused across every call that touches that
   state.

3. **How would this need to change if workers ran in separate OS processes
   instead of one event loop?**
   Strong answer: an `asyncio.Lock()` only coordinates coroutines within a
   single process's event loop — it has no effect across process
   boundaries. A multi-process version would need real cross-process
   coordination: e.g. a `multiprocessing.Lock`/shared memory primitive if
   still in one machine, or — more realistically for a real job-processing
   system — pushing the shared counter into something that natively
   supports atomic operations across processes/machines (a database row
   with an atomic decrement, or an atomic increment/decrement command in a
   store like Redis), rather than an in-process Python dict guarded by an
   in-process lock at all.

4. **What tests would you add, and why?**
   Strong answer: a case with different job_count/num_workers numbers than
   the given failing test (to make sure the fix isn't just tuned to those
   exact numbers); a case with several distinct `batch_id`s running
   concurrently, to confirm they don't cross-contaminate each other's
   counts; ideally something that would catch a "looks like locking but
   isn't" fix specifically (a new-lock-per-call).

5. **Is there another valid way to implement this fix?**
   Strong answer: yes — either remove the `await` from the critical
   section entirely (do the read-modify-write-and-finalize-check
   synchronously, then do any "simulate work" yield afterward), or keep
   the `await` inside the critical section but protect the whole thing
   with one shared `asyncio.Lock()`. Both are acceptable; the first is
   simpler when nothing genuinely needs to `await` in the middle of the
   update, the second is necessary if something (a real persistence call,
   say) truly does.

6. **If we later wanted a single global lock to feel too coarse (e.g. it
   serializes unrelated batches' completions behind each other under heavy
   load), how would you make it more fine-grained without reintroducing the
   original bug?**
   Strong answer (design-forward-thinking): key the lock per `batch_id`
   (e.g. a `dict[str, asyncio.Lock]`, created lazily/once per batch_id and
   reused for every call on that batch — critically, *not* a new lock per
   call), so that unrelated batches can proceed concurrently while calls
   for the *same* batch are still serialized. The key invariant is the
   same as in the original bug: whichever locks exist must be shared and
   reused across every call that touches the state they protect.
