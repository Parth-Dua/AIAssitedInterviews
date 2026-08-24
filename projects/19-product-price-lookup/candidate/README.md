# Product Price Lookup Service — Currency-Blind Cache Bug (Interview Exercise)

**Format:** AI-Assisted Debugging Assessment
**Timebox:** 60–75 minutes
**Level:** Backend / Full-stack, mid-level
**Difficulty:** 8/10 — calibrated to Amazon-style SWE repo-debugging online
assessments (repo-based, unfamiliar code, one reported bug, public + hidden
tests). This project does not assume you've attempted any other project in
this curriculum.

## Scenario

You've joined the internal platform team that owns a product-pricing
lookup service. It fetches current prices from an external pricing
provider (mocked here — no real network calls), caches results briefly to
avoid redundant provider calls, and falls back to a last-known price if the
provider is temporarily unavailable. It's a small internal service — you
haven't seen this code before today.

Support has escalated a customer complaint:

> "A customer switched their storefront's display currency from USD to
> EUR, but the price shown for a product didn't change — it kept showing
> the exact same number as before, which can't be right, since USD and EUR
> prices for the same product are never numerically identical in our
> system."

## Your task

1. Reproduce the reported bug.
2. Find the root cause.
3. Fix it so that looking up a product's price in one currency can never
   return a price that was actually fetched for a different currency.
4. Add or strengthen tests so this can't silently regress.
5. Make sure you haven't broken any other existing behavior (caching,
   fallback, or otherwise).

You do **not** need to add any new features — this is a bug fix only.

## Repository layout

```
src/
  app.ts                                 Express app setup (middleware, routes)
  server.ts                              Entrypoint — imports app, calls .listen()
  routes/prices.ts                       Router for GET /products/:productId/price
  controllers/priceController.ts         Request/response handling
  services/priceService.ts               Price lookup business logic
  cache/priceCache.ts                    In-memory TTL cache (injectable clock)
  clients/pricingClient.ts               Fake external pricing provider client
  repositories/lastKnownPriceRepository.ts  Last-known-price fallback store
  types.ts                               Shared request/response shapes
tests/
  priceService.test.ts                   Unit tests against the service directly
  pricesApi.test.ts                      HTTP-level tests against the Express app (supertest)
```

## Setup

```bash
npm install
```

## Running tests

```bash
npm test
```

Two tests currently fail (one unit-level, one HTTP-level) — both encode the
same reported bug. The rest pass and describe behavior you must **not**
break.

## Constraints

- Keep changes scoped to fixing this bug (plus any tests you add). Don't
  refactor unrelated code.
- Preserve the existing API request/response shape (`GET
  /products/:productId/price?currency=...`, defaulting to `USD` when
  `currency` is omitted).

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
