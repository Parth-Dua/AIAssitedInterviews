# OrderFlow — Pricing Service Bug (Interview Exercise)

**Format:** AI-Assisted Debugging Assessment
**Timebox:** 45–60 minutes
**Level:** SWE Intern / New Grad / Backend

## Scenario

You've just joined OrderFlow's checkout team. The pricing service computes a
price preview (subtotal, discount, shipping, total) for a shopping cart
before the customer confirms checkout. It's a small internal service — you
haven't seen this code before today.

Support has escalated a customer complaint:

> "A customer's cart subtotal was $52.00 (above our $50 free-shipping
> threshold) before applying the `WELCOME10` promo code, but they were
> still charged the $4.99 shipping fee once the promo code was applied."

The team's stated policy (confirmed with the checkout PM) is:

> Free shipping eligibility is based on the order's subtotal **before** any
> discount is applied. A discount should never cause a customer to lose
> free shipping they'd otherwise qualify for.

## Your task

1. Reproduce the reported bug.
2. Find the root cause.
3. Fix it so that the stated policy holds.
4. Add or strengthen tests so this can't silently regress.
5. Make sure you haven't broken any other existing behavior.

You do **not** need to add any new features — this is a bug fix only.

## Repository layout

```
app/
  main.py                       FastAPI app entrypoint
  api/routes/orders.py          POST /orders/price
  models/schemas.py             Request/response Pydantic models
  services/pricing_service.py   Pricing business logic
  repositories/pricing_repository.py   Discount code lookup
  domain/constants.py           Shipping threshold / fee constants
tests/
  test_pricing_service.py       Unit tests for the pricing service
  test_pricing_api.py           API-level tests
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
- Preserve the existing public API (`POST /orders/price` request/response
  shape).
- All monetary values are integer cents — don't introduce floats.

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
