# Order Notification Service — Hung Request Bug (Interview Exercise)

**Format:** AI-Assisted Debugging Assessment
**Timebox:** 45–60 minutes
**Level:** SWE Intern / New Grad / Backend
**Difficulty:** 7/10 — calibrated to Amazon-style SWE repo-debugging online
assessments (repo-based, unfamiliar code, one reported bug, public + hidden
tests). This tests your application-level async-flow reasoning — how a
request moves through an Express app and what happens when a step in that
flow fails — not obscure Node.js event-loop trivia. You don't need to know
anything about microtasks, the event queue, or scheduling internals to solve
this; you need to read the code path a request travels through and think
about what happens when one of its steps doesn't succeed. This project does
not assume you've attempted any other project in this curriculum.

## Scenario

You've just joined the team behind an internal order-placement API. When an
order is created, the service notifies the warehouse-fulfillment system so
it knows to start picking and packing. It's a small internal service — you
haven't seen this code before today.

Support has escalated a user complaint:

> "When the warehouse system can't be reached for a particular order,
> placing that order never completes — the client just waits and
> eventually times out. Orders where the warehouse is reachable work
> completely fine."

## Your task

1. Reproduce the reported bug.
2. Find the root cause.
3. Fix it so that placing an order always results in a response being sent
   back to the client — success or a clear, correctly-shaped error — even
   when the warehouse system can't be reached.
4. Add or strengthen tests so this can't silently regress.
5. Make sure you haven't broken any other existing behavior.

You do **not** need to add any new features — this is a bug fix only.

## Repository layout

```
src/
  app.ts                              Express app setup (middleware, routes)
  server.ts                           Entrypoint — imports app, calls .listen()
  routes/orders.ts                    Router for POST /orders
  middleware/requestLogger.ts         Logs each incoming request
  middleware/validateOrderCreate.ts   Validation for order creation
  middleware/errorHandler.ts          Central error-handling middleware
  controllers/orderController.ts      Request/response handling
  services/orderService.ts            Order creation logic
  services/warehouseNotifier.ts       Fake client for the warehouse system
  repositories/orderRepository.ts     In-memory order store
  types.ts                            Order interface and request/response shapes
tests/
  orderController.test.ts             Unit-ish tests against the service/notifier directly
  ordersApi.test.ts                   HTTP-level tests against the Express app (supertest)
```

## Setup

```bash
npm install
```

## Running tests

```bash
npm test
```

One test currently fails — it encodes the reported bug. The rest pass and
describe behavior you must **not** break.

## Constraints

- Keep changes scoped to fixing this bug (plus any tests you add). Don't
  refactor unrelated code.
- Preserve the existing API request/response shape for `POST /orders`,
  including the error response shape produced for known failure cases.

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
