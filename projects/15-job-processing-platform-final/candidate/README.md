# Job Processing Platform — Duplicate-Finish Bug + Cancellation (Interview Exercise)

**Format:** AI-Assisted Debugging Assessment — Capstone
**Timebox:** 75–90 minutes
**Level:** Backend / Mid-level+
**Difficulty:** 9/10 (hardest exercise in this series)

## Scenario

You've just joined the internal data-export platform team. Users request a
CSV export of their data; a fleet of worker processes picks up queued jobs,
does the export work, and reports back through a small callback-style API.
It's a small internal service — you haven't seen this code before today.

A job moves through a simple lifecycle:

```
queued --start--> running --finish(success)--> completed
                       \----finish(failure)---> failed
```

Workers report back via `POST /jobs/{id}/finish`, sending either a `result`
(on success) or an `error` (on failure). The worker fleet's callback
delivery is **at-least-once, not exactly-once, by design** — if a worker
doesn't get a fast enough acknowledgement, it may deliver the same "job
finished" notification more than once for the same job. This is documented,
expected behavior on the worker fleet's end, not a bug on its side.

### 1. A bug report

> "One of our export jobs completed successfully and had the right result
> file linked. A few minutes later, the same job's result silently changed
> to a different (incorrect, older) file — nobody re-ran it on purpose. We
> think our worker fleet's callback mechanism occasionally delivers a 'job
> finished' notification more than once for the same job, and something in
> our system just... accepted the second one."

### 2. A feature request

> "We'd like to let users cancel an export job while it's still waiting in
> the queue — before a worker has picked it up. Once a worker has started
> on it, we don't support interrupting it; the user just has to wait for it
> to finish (or fail). A job that's already completed, failed, or been
> cancelled obviously can't be cancelled again."

## Your task

1. Reproduce the reported bug.
2. Find its root cause.
3. Fix it so a job's result can never be silently changed after the job has
   already reached a terminal state.
4. Implement `POST /jobs/{id}/cancel`: a queued job can be cancelled; a
   running, completed, failed, or already-cancelled job must reject
   cancellation with a clear error. A cancelled job is terminal — like any
   other terminal state, it can't later be started or finished.
5. Add or strengthen tests so neither the bug nor an incomplete
   cancellation implementation can silently regress.
6. Make sure you haven't broken any other existing behavior.

This exercise has **two deliverables**, not one: the state-corruption bug
fix and the cancellation feature. Both touch the same lifecycle logic —
budget your time for both, and think about whether they should be fixed
independently or share a common mechanism.

## Repository layout

```
app/
  main.py                              FastAPI app entrypoint
  api/routes/jobs.py                   POST /jobs, /start, /finish, GET /jobs/{id}
  models/schemas.py                    Request/response Pydantic models
  services/job_service.py              Job lifecycle orchestration
  repositories/job_repository.py       In-memory job storage
  domain/job.py                        Job dataclass
  workers/export_worker.py             Deterministic fake export-processing
                                        logic run by the (simulated) worker
                                        fleet before it calls back
tests/
  test_job_service.py                  Unit tests for the job lifecycle logic
  test_jobs_api.py                     API-level tests
  test_export_worker.py                Unit tests for the worker function
```

There are no real worker threads or processes in this exercise — the
"worker fleet" is simulated by calling `/start` and `/finish` directly, the
same way a real worker's callback would.

## Setup

```bash
pip install -e ".[dev]"
```

## Running tests

```bash
pytest -q
```

Some tests currently fail — they encode the reported bug and the missing
cancellation feature. The rest pass and describe behavior you must **not**
break.

## Constraints

- Keep changes scoped to the bug fix and the requested feature (plus any
  tests you add). Don't refactor unrelated code.
- Preserve the existing request/response shapes for `POST /jobs`,
  `POST /jobs/{id}/start`, `POST /jobs/{id}/finish`, and `GET /jobs/{id}`.
- Don't add a real database or real concurrency/threads — the repository
  stays in-memory, pure Python, fully sequential.
- This is a bounded bug fix plus one feature, not a rewrite of the
  lifecycle logic.

## AI tool policy

You may use an AI coding assistant. If you'd like it to behave the way a
real interview/OA proctor would configure it, load
`.ai/assessment-skill/SKILL.md` into your assistant as a system/project
instruction. It's written to work with any capable coding assistant, not
a specific product.

Using an assistant well is part of what's being evaluated — treat it like
a knowledgeable but junior pair programmer, not an oracle. You're expected
to reproduce the bug, form your own hypotheses, design the feature, and
verify anything it suggests before you rely on it.

## Deliverables

- Your bug fix.
- Your `POST /jobs/{id}/cancel` implementation.
- Any tests you added or changed.
- Be ready to explain:
  - What the root cause of the reported bug was, precisely.
  - Why your fix is correct.
  - Why your fix **generalizes** — i.e. it isn't a patch that only handles
    the one reported scenario, but addresses the underlying rule wherever
    it applies across the lifecycle.
  - What else you checked to make sure nothing else broke.
- Be ready to answer a small number of design follow-up questions about
  your fix and how you'd evolve this system further — this is part of the
  deliverable, not just a formality.
