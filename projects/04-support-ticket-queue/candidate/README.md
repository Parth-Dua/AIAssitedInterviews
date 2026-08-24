# Support Ticket Queue — Watcher List Bug (Interview Exercise)

**Format:** AI-Assisted Debugging Assessment
**Timebox:** 45–60 minutes
**Level:** SWE Intern / New Grad / Backend
**Difficulty:** 6/10

## Scenario

You've just joined the internal tools team that maintains the support-ticket
queue used by the support desk. Each ticket has a subject, a status, and a
list of "watchers" — email addresses of people who get notified whenever the
ticket is updated. It's a small internal service — you haven't seen this code
before today.

Support has escalated a couple of odd reports:

> "Someone noticed that when they added a coworker as a watcher on one
> ticket, that same coworker mysteriously started showing up as a watcher on
> several other, completely unrelated tickets that were created around the
> same time. Also, some newly created tickets already have 3-4 people
> watching them who were never explicitly added."

## Your task

1. Reproduce the reported bug.
2. Find the root cause.
3. Fix it so that each ticket's watcher list behaves independently of every
   other ticket's.
4. Add or strengthen tests so this can't silently regress.
5. Make sure you haven't broken any other existing behavior.

You do **not** need to add any new features — this is a bug fix only.

## Repository layout

```
app/
  main.py                          FastAPI app entrypoint
  api/routes/tickets.py            POST /tickets, GET /tickets/{id}, POST /tickets/{id}/watchers
  models/schemas.py                Request/response Pydantic models
  domain/ticket.py                 Ticket domain object
  services/ticket_service.py       Ticket creation and watcher business logic
  repositories/ticket_repository.py   In-memory ticket store
tests/
  test_ticket_service.py           Unit tests for the ticket service
  test_tickets_api.py              API-level tests
```

## Setup

```bash
pip install -e ".[dev]"
```

## Running tests

```bash
pytest -q
```

Some tests currently fail — they encode the reported bug. The rest pass and
describe behavior you must **not** break.

## Constraints

- Keep changes scoped to fixing this bug (plus any tests you add). Don't
  refactor unrelated code.
- Preserve the existing public API (`POST /tickets`, `GET /tickets/{id}`,
  `POST /tickets/{id}/watchers` request/response shapes).

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
