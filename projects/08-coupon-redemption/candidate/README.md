# Coupon Redemption — Exhaustion Bug + Fixed-Amount Discount (Interview Exercise)

**Format:** Debugging + Feature Implementation
**Timebox:** 60–75 minutes
**Level:** SWE Intern / New Grad / Backend
**Difficulty:** 7/10

## Scenario

You've just joined the promotions platform team. This internal service
tracks promo coupons and their redemption state — how many times each
coupon has been used, and whether it's still `active`, has become
`exhausted`, or was manually `cancelled`. It's a small internal service —
you haven't seen this code before today.

The promotions team has escalated a bug report, and product has a
follow-up feature request.

### 1. A bug report

> "A coupon with a redemption limit of 100 was redeemed well over 150
> times before someone on the promotions team noticed — the system was
> supposed to stop allowing redemptions once the limit was hit."

### 2. A feature request

> "Right now every coupon is a percentage off. Can we support a flat
> fixed-amount discount too — like '$5 off' instead of '10% off'? And make
> sure it behaves sensibly if the discount is bigger than the order total —
> we don't want a negative total."

## Your task

1. Reproduce the reported bug, find its root cause, and fix it.
2. Add support for a `"fixed_amount"` discount type alongside the existing
   `"percentage"` type, with sensible, non-negative behavior when the
   fixed discount exceeds the order subtotal.
3. Add or strengthen tests so neither the bug nor an incomplete
   fixed-amount implementation can silently regress.
4. Make sure you haven't broken any other existing behavior — in
   particular, existing percentage-coupon pricing must compute exactly the
   same totals it did before.

This exercise has **two deliverables**, not one: the redemption bug fix
and the fixed-amount discount feature. Budget your time for both.

## Repository layout

```
app/
  main.py                              FastAPI app entrypoint
  api/deps.py                          Shared repository/service instances
  api/routes/coupons.py                GET/POST endpoints for coupons
  models/schemas.py                    Request/response Pydantic models
  domain/coupon.py                     Coupon domain object
  services/coupon_service.py           Redemption + discount-pricing logic
  repositories/coupon_repository.py    In-memory coupon store
tests/
  test_coupon_service.py               Unit tests for the coupon service
  test_coupons_api.py                  API-level tests for coupon routes
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
fixed-amount feature. The rest pass and describe behavior you must **not**
break.

## Constraints

- Keep changes scoped to the bug fix and the requested feature (plus any
  tests you add). Don't refactor unrelated code.
- Preserve the existing request/response shapes for the coupon endpoints.
- Existing `"percentage"` coupon pricing behavior (including rounding)
  must compute exactly the same totals it did before this change.
- All monetary values are integer cents — don't introduce floats for
  money.
- Don't add a real database — the repository stays in-memory, pure
  Python.

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

- Your redemption bug fix.
- Your fixed-amount discount implementation.
- Any tests you added or changed.
- Be ready to explain: what the bug's root cause was, how you found it,
  why your fix is correct, how you designed the fixed-amount discount
  behavior, and what else you checked to make sure nothing else broke.
