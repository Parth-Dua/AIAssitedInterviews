# Inventory Reservations — Pagination Bug + Category Filter (Interview Exercise)

**Format:** Debugging + Feature Implementation
**Timebox:** 60–75 minutes
**Level:** SWE Intern / New Grad / Backend
**Difficulty:** 6/10

## Scenario

You've just joined the warehouse systems team. The inventory API tracks
*reservations* — units of a SKU that have been set aside against an
outgoing order. It's a small internal service — you haven't seen this code
before today.

One endpoint powers the warehouse dashboard's reservations list:
`GET /reservations?cursor=<id>&limit=<n>`, which pages through reservations
in the order they were created.

The warehouse app team has filed two things against this endpoint.

### 1. A bug report

> "When we paginate through reservations 10 at a time, the last item from
> page 1 also shows up as the first item of page 2 — so we're seeing
> duplicates and our total displayed count doesn't add up."

### 2. A feature request

> "It would also be really useful if we could filter the reservations list
> down to a single category — e.g. just `electronics` — while we're paging
> through it, so we can triage one category at a time instead of scrolling
> past everything else."

## Your task

1. Reproduce the reported pagination bug, find its root cause, and fix it.
2. Implement the requested `category` filter as an optional query
   parameter on `GET /reservations`, making sure it composes correctly
   with cursor pagination — paging through a filtered category should
   return every matching item exactly once, with no duplicates and no
   gaps.
3. Add or strengthen tests so neither the bug nor an incomplete filter
   implementation can silently regress.
4. Make sure you haven't broken any other existing behavior.

This exercise has **two deliverables**, not one: the bug fix and the
feature. Budget your time for both.

## Repository layout

```
app/
  main.py                                   FastAPI app entrypoint
  api/routes/reservations.py                GET /reservations
  models/schemas.py                         Reservation / ReservationPage Pydantic models
  services/reservation_service.py           Thin orchestration layer
  repositories/reservation_repository.py    In-memory store + pagination query
tests/
  test_reservations_service.py              Unit tests against the service/repository
  test_reservations_api.py                  API-level tests
```

## Setup

```bash
pip install -e ".[dev]"
```

## Running tests

```bash
pytest -q
```

Some tests currently fail — they encode the reported bug and the missing
feature. The rest pass and describe behavior you must **not** break.

## Constraints

- Keep changes scoped to the bug fix and the requested feature (plus any
  tests you add). Don't refactor unrelated code.
- Preserve the existing response shape (`{"items": [...], "next_cursor":
  ...}`) and the existing meaning of `cursor` and `limit`.
- The `category` filter must apply *before* pagination is computed for
  that request — a page returned under a category filter should always
  contain up to `limit` matching items (fewer only once you've reached the
  end of that category), not fewer items because non-matching items were
  paginated out first.
- An unrecognized `category` value should return an empty result set, not
  an error.

## AI tool policy

You may use an AI coding assistant. If you'd like it to behave the way a
real interview/OA proctor would configure it, load
`.ai/assessment-skill/SKILL.md` into your assistant as a system/project
instruction. It's written to work with any capable coding assistant, not
a specific product.

Using an assistant well is part of what's being evaluated — treat it like
a knowledgeable but junior pair programmer, not an oracle. You're expected
to reproduce the bug, form your own hypotheses, design the feature, and
verify anything the assistant suggests before you rely on it.

## Deliverables

- Your bug fix.
- Your `category` filter implementation.
- Any tests you added or changed.
- Be ready to explain: what the pagination bug's root cause was, how you
  found it, why your fix is correct, how you designed the category filter
  to compose correctly with pagination, and what else you checked to make
  sure nothing else broke.
