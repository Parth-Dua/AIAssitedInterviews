# Library Loan Tracker — Overdue Loans Bug (Interview Exercise)

**Format:** AI-Assisted Debugging Assessment
**Timebox:** 45–60 minutes
**Level:** SWE Intern / New Grad / Backend
**Difficulty:** 5/10

## Scenario

You've just joined the internal tools team that maintains the library
system's backend API. One endpoint powers the librarian dashboard's overdue
list: `GET /loans/overdue?as_of=YYYY-MM-DD`, which returns every loan a
librarian should follow up on. It's a small internal service — you haven't
seen this code before today.

A librarian has filed a bug report:

> "A patron renewed their loan last week, which should have pushed the due
> date out two weeks. The book is still showing up in the librarian's
> overdue list using the original due date, even though the renewal was
> recorded in the system."

## Your task

1. Reproduce the reported bug.
2. Find the root cause.
3. Fix it.
4. Add or strengthen tests so this can't silently regress.
5. Make sure you haven't broken any other existing behavior.

You do **not** need to add any new features — this is a bug fix only.

## Repository layout

```
app/
  main.py                             FastAPI app entrypoint
  api/routes/loans.py                 GET /loans/overdue
  models/orm.py                       SQLAlchemy Loan model
  models/schemas.py                   API response schema
  services/loan_service.py            Thin orchestration over the repository
  repositories/loan_repository.py     Overdue-loan query
  db/base.py, db/session.py           SQLAlchemy engine/session setup
tests/
  conftest.py                         Test fixtures (isolated in-memory DB per test)
  test_loans_service.py               Unit tests against the service/repository
  test_loans_api.py                   API-level tests
```

Note that `as_of` is always passed explicitly (as a query parameter, then
threaded through the service and repository) rather than read from the
system clock — this keeps overdue calculations reproducible for a given day
and makes the tests deterministic.

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
- Preserve the existing public API (`GET /loans/overdue` request/response
  shape).
- Don't introduce any dependency on the system clock (`datetime.now()` /
  `date.today()`) inside the business logic — `as_of` must stay an explicit,
  passed-in parameter.

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
