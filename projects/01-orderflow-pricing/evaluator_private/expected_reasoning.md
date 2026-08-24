# Expected Reasoning Path

1. Run `pytest -q`; observe `test_free_shipping_preserved_when_discount_applied`
   fails while everything else passes.
2. Read the assertion: subtotal 5200, discount 520 (both correct), but
   shipping is 499 instead of 0.
3. Open `app/services/pricing_service.py`; find `price_order`. Notice two
   `>=` comparisons close together: one implicitly for the discount
   calculation context, one for shipping.
4. Notice the shipping check uses `effective_subtotal` (already has the
   discount subtracted) rather than `subtotal_cents`.
5. Cross-check against the stated policy in the README/bug report: "based on
   the order's subtotal before any discount."
6. Change the shipping comparison to use `subtotal_cents`. Recompute
   `total_cents` using the corrected `shipping_cents` (should still be
   `subtotal_cents - discount_cents + shipping_cents`).
7. Re-run tests; all pass. Manually reason through 1-2 additional cases
   (e.g., a small order with a discount, to confirm shipping is still
   charged when genuinely below threshold) or add a test for it.
8. Explain: the discount and shipping decisions are independent business
   rules that got coupled by reusing the wrong variable.

A strong candidate reaches step 6 within 15-20 minutes given the failing
test as a starting point.
