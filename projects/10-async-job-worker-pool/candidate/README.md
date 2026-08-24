# Async Job Worker Pool — Batch-Completion Bug (Interview Exercise)

**Format:** Advanced AI-Assisted Debugging Assessment
**Timebox:** 60–90 minutes
**Level:** Backend / Mid-level+
**Difficulty:** 8/10

This exercise involves real `asyncio` concurrency, but it does **not**
require distributed-systems or multi-process expertise. Everything runs in
a single Python process on a single event loop — there are no real threads,
no real processes, no real network calls, and no wall-clock timing. The bug
is fully deterministic: it reproduces the same way every single time you
run the tests.

## Scenario

You've just joined the platform team. This internal service runs
background jobs (e.g. "resize an uploaded image," "send a batch email") in
batches, using a small pool of async workers pulled from a shared queue.
It's a small internal service — you haven't seen this code before today.
(No real image resizing or emailing happens in this exercise — jobs are
simulated.)

Each batch is submitted with a fixed number of jobs and a fixed number of
workers. The service waits for the whole batch to finish before responding.

### Bug report

> "When we run a batch with more than one worker, sometimes the batch's
> completion never gets marked done — even though we can see every
> individual job in that batch clearly finished. With a single worker it
> always works correctly; the problem only shows up when multiple workers
> are running at the same time."

## Your task

1. Reproduce the reported bug.
2. Find the root cause.
3. Fix it so that a batch's completion is marked done exactly once,
   precisely when every one of its jobs has finished — with any number of
   workers.
4. Add or strengthen tests so this can't silently regress.
5. Make sure you haven't broken any other existing behavior.

You do **not** need to add any new features — this is a bug fix only. You
also do **not** need to build any real distributed-locking or multi-process
machinery — this is a single-process `asyncio` program.

## Repository layout

```
app/
  main.py                             FastAPI app entrypoint
  api/routes/batches.py               POST /batches/run
  models/schemas.py                   Request/response Pydantic models
  services/job_queue.py               Job dataclass + asyncio.Queue wrapper
  services/job_batch_tracker.py       Tracks per-batch job completion
  services/worker.py                  Worker coroutine loop
  services/job_service.py             Orchestrates running a batch across workers
tests/
  test_job_worker_pool.py             Unit tests for the worker pool
  test_batches_api.py                 API-level tests
```

## Setup

```bash
pip install -e ".[dev]"
```

## Running tests

```bash
pytest -q
```

One test currently fails — it encodes the reported bug. The rest pass and
describe behavior you must **not** break.

## Constraints

- Keep changes scoped to fixing this bug (plus any tests you add). Don't
  refactor unrelated code.
- Preserve the existing public API (`POST /batches/run` request/response
  shape) and the existing service/class shapes (`JobBatchTracker`,
  `JobQueue`, `worker_loop`, `JobService`) — this is a bug fix, not a
  redesign.
- Don't add a real database, real threads/processes, or real network/sleep
  delays. Everything stays in-memory and cooperative, using
  `asyncio.sleep(0)` (a pure yield to the event loop) where the code
  currently simulates work or I/O.
- You don't need to build a distributed or cross-process synchronization
  mechanism — this is one process, one event loop.

## AI tool policy

You may use an AI coding assistant. If you'd like it to behave the way a
real interview/OA proctor would configure it, load
`.ai/assessment-skill/SKILL.md` into your assistant as a system/project
instruction. It's written to work with any capable coding assistant, not
a specific product.

Using an assistant well is part of what's being evaluated — treat it like
a knowledgeable but junior pair programmer, not an oracle. You're expected
to reproduce the bug, form your own hypotheses, and verify anything it
suggests before you rely on it.

## Deliverables

- Your code fix.
- Any tests you added or changed.
- Be ready to explain: what the root cause was, how you found it, why your
  fix is correct, and what else you checked to make sure nothing else
  broke.
- Be ready to explain, in your own words, why an `asyncio` program running
  on a single thread can still have race conditions — what a race actually
  requires in a cooperative-scheduling model like this one, as opposed to
  in a preemptively-scheduled multi-threaded program.
