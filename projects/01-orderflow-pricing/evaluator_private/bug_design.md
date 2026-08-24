# Bug Design (private — do not expose to candidate)

## Expected behavior
Free-shipping eligibility is determined by the order's **pre-discount**
subtotal. `total = subtotal - discount + shipping`, where `shipping = 0` iff
`subtotal_cents >= FREE_SHIPPING_THRESHOLD_CENTS`, else `FLAT_SHIPPING_CENTS`.

## Actual (buggy) behavior
`app/services/pricing_service.py::PricingService.price_order` computes
`effective_subtotal = subtotal_cents - discount_cents` and checks
`effective_subtotal >= FREE_SHIPPING_THRESHOLD_CENTS` for the shipping
decision. Any order whose subtotal is above the threshold but whose
post-discount amount drops below it incorrectly loses free shipping.

## Root cause
Variable misuse: the shipping-threshold comparison uses `effective_subtotal`
(post-discount) instead of `subtotal_cents` (pre-discount). Plausible
provenance: `effective_subtotal` was introduced later for the *total*
calculation and got reused a line above for the *shipping* decision by
mistake — the classic "reused the wrong nearby variable" bug.

## Violated invariant
"Free shipping threshold is evaluated against the pre-discount subtotal; a
discount code must never cause loss of free shipping the order already
qualified for." (Business rule confirmed by PM, stated in the candidate
README.)

## Relevant execution path
`POST /orders/price` (app/api/routes/orders.py) → `PricingService.price_order`
(app/services/pricing_service.py) → `PricingRepository.get_discount_percent`
(app/repositories/pricing_repository.py, for the discount lookup) →
constants in `app/domain/constants.py`. The bug is entirely within
`pricing_service.py`; the repository and route are correct but must be read
to understand where `discount_code` and the threshold constant come from.

## Evidence available to the candidate
- The failing public test `test_free_shipping_preserved_when_discount_applied`
  reproduces the exact reported scenario with concrete numbers.
- The README states the business policy explicitly.
- Reading `pricing_service.py` end-to-end reveals the two nearby
  `>=` comparisons using different subtotal variables.

## Reasonable hypotheses
1. (Correct) The shipping threshold check uses the wrong (post-discount)
   subtotal variable.
2. (Plausible, wrong) The discount is being computed incorrectly (e.g. wrong
   percentage) — ruled out because `discount_cents == 520` is exactly correct
   in the failing test; only `shipping_cents` is wrong.
3. (Plausible, wrong) The discount repository is returning a stale/incorrect
   percent for `WELCOME10` — ruled out by reading `pricing_repository.py`
   (static in-memory dict, correct value).

## Intended regression test
`test_free_shipping_preserved_when_discount_applied` (already present as a
public test) plus hidden tests covering the boundary and multiple discount
codes (see `hidden_tests/`).

## Acceptable fixes
- Change the shipping-threshold comparison to use `subtotal_cents` instead of
  `effective_subtotal`.
- Equivalent: introduce a clearly named variable (e.g.
  `shipping_qualifying_subtotal_cents = subtotal_cents`) used only for the
  threshold check, as long as the value used is the pre-discount subtotal.
- `total_cents` must still equal `subtotal_cents - discount_cents +
  shipping_cents` in all cases.

## Tempting but incomplete/wrong fix
Capping `discount_cents` so it never pushes `effective_subtotal` below the
threshold (i.e., silently reducing the discount to "protect" free shipping).
This makes the reported test pass but violates
`test_discount_code_reduces_subtotal_correctly`-style hidden tests that check
the discount amount is always exactly `subtotal * percent / 100` regardless
of the shipping outcome — the discount and shipping decisions are supposed to
be independent, not mutually adjusting. Flag this as a red flag during
review if a candidate does it: it "solves" the visible test while breaking a
stated, testable invariant (discount is a pure percentage of subtotal).

## Why this is interview-appropriate
Classic "read code across 3 small files, find a one-variable logic bug from
a plausible business bug report" — a very common real-world SWE
intern/new-grad interview and OA shape. No specialist knowledge required;
fully discoverable from the code, the failing test, and the README.
