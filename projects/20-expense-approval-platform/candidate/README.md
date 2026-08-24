# Expense Approval Platform — Cross-Manager Approval Bug + Delegation (Interview Exercise)

**Format:** AI-Assisted Debugging + Feature Assessment — Capstone
**Timebox:** 60–90 minutes
**Level:** Backend / New Grad+ to Mid-level
**Difficulty:** 8.5/10 — the hardest exercise in this Node/TypeScript track,
calibrated to Amazon-style repo-based debugging OAs (repo-based, unfamiliar
code, one reported bug, a follow-on feature, public + hidden tests). This
project does not assume you've attempted any other project in this
curriculum.

## Scenario

You've just joined the internal tools team supporting a small expense-report
approval tool. Employees submit expense reports; each report is assigned to
one manager, who (or an admin) approves or rejects it. It's a small internal
service — you haven't seen this code before today. There's no real
authentication system: requests identify their caller with an `X-User-Id`
header, which is enough for this exercise.

### 1. A bug report

> "An employee noticed that a completely different manager — not their own
> manager — approved one of their expense reports. Approvals are supposed to
> only come from the employee's actual assigned manager, or an admin."

### 2. A feature request

> "We'd like managers to be able to delegate approval of a specific pending
> expense report to another manager — for example, while they're out of
> office. Once a manager delegates a report, the person they delegated to
> should be able to approve or reject that report themselves, the same way
> the original assigned manager could. Delegation should only be settable by
> the report's own assigned manager (or an admin), and only while the report
> is still pending."

## Your task

1. Reproduce the reported bug.
2. Find its root cause.
3. Fix it so approving or rejecting a report only succeeds for someone who is
   actually authorized to act on *that specific report*.
4. Implement `POST /expense-reports/:id/delegate` per the feature request
   above, and make sure approval/rejection actually honor a delegation once
   one exists.
5. Add or strengthen tests so neither the bug nor an incomplete delegation
   implementation can silently regress.
6. Make sure you haven't broken any other existing behavior.

This exercise has **two deliverables**, not one: the authorization bug fix
and the delegation feature. Both touch the same authorization logic — budget
your time for both, and think about whether your fix needs to apply in more
than one place.

## Repository layout

```
src/
  app.ts                                    Express app setup (middleware, routes)
  server.ts                                 Entrypoint — imports app, calls .listen()
  routes/expenseReports.ts                  Router for /expense-reports
  middleware/attachUser.ts                  Reads X-User-Id and attaches req.user
  middleware/requireRole.ts                 Coarse-grained role gate (employee/manager/admin)
  controllers/expenseReportController.ts    Request/response handling
  services/expenseReportService.ts          Expense report business logic
  repositories/expenseReportRepository.ts   In-memory expense report store
  repositories/userRepository.ts            In-memory user store (seeded with sample users)
  types.ts                                  Domain types and request/response shapes
tests/
  expenseReportService.test.ts              Unit tests against the service directly
  expenseReportsApi.test.ts                 HTTP-level tests against the Express app (supertest)
```

## Setup

```bash
npm install
```

## Running tests

```bash
npm test
```

Some tests currently fail — they encode the reported bug and the missing
delegation feature. The rest pass and describe behavior you must **not**
break.

## Constraints

- Keep changes scoped to the bug fix and the requested feature (plus any
  tests you add). Don't refactor unrelated code.
- Preserve the existing request/response shapes for `POST /expense-reports`,
  `GET /expense-reports/:id`, `POST /expense-reports/:id/approve`, and
  `POST /expense-reports/:id/reject`.
- Don't add a real authentication system, database, or ORM — the `X-User-Id`
  header and the in-memory repositories stay as they are.
- This is a bounded bug fix plus one feature, not a rewrite of the
  authorization logic.

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
- Your `POST /expense-reports/:id/delegate` implementation.
- Any tests you added or changed.
- Be ready to explain:
  - What the root cause of the reported bug was, precisely.
  - Why your fix is correct.
  - Why your fix **generalizes** — i.e. it isn't a patch that only handles
    the one reported scenario, but addresses the underlying rule everywhere
    it applies, including once delegation exists.
  - What else you checked to make sure nothing else broke.
- Be ready to answer a small number of design follow-up questions about
  your fix and how you'd evolve this system further — this is part of the
  deliverable, not just a formality.
