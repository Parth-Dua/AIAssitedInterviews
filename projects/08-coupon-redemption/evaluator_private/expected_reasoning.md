# Expected Reasoning Path

## Part A — the redemption bug

1. Run `pytest -q`; observe
   `test_redeeming_beyond_max_redemptions_is_rejected` and
   `test_exhausted_coupon_status_is_persisted` (plus their API-level
   twins) fail while most other tests pass (plus the unrelated
   fixed-amount failures, see Part B).
2. Read the failing assertions: a coupon redeemed exactly
   `max_redemptions` times should reject a further redemption and show
   `status == "exhausted"` on a fresh read — but it keeps accepting
   redemptions and a fresh `GET` still shows `"active"`.
3. Trace the call path: `POST /coupons/{code}/redeem` →
   `CouponService.redeem`.
4. Read `redeem()` line by line: `redemption_count` is incremented, then
   `self._repository.save(coupon)` is called, and only *after* that does
   the code check whether the count reached the limit and set
   `coupon.status = "exhausted"`.
5. Open `coupon_repository.py` and read `save()`/`get_by_code()` — notice
   both explicitly make a defensive copy (`copy.deepcopy`) rather than
   storing/returning the exact object passed in or held. This is the key
   insight: the `coupon.status = "exhausted"` line mutates a local object
   that is no longer connected to what's stored, because that connection
   was already severed by the earlier `save()` call.
6. Confirm by checking that `redemption_count` (mutated *before* `save()`)
   *does* persist correctly, while `status` (mutated *after*) does not —
   this asymmetry is the direct evidence that ordering, not the repository
   itself, is the bug. A candidate who only checks the redeem() response
   (rather than a separate `GET`) will miss this, since the returned
   object is the same locally-mutated instance and looks correct.
7. Fix `redeem()` so the `status` mutation happens *before* the `save()`
   call (or add a second `save()` call after it) — either way, the final
   state reaches the store.
8. Re-run the reported-bug tests and their twins; confirm they pass.
   Manually reason through (or add a test for) the exact boundary — does
   the `max_redemptions`-th call exhaust, and does a call one before that
   still succeed as `"active"`? — since an off-by-one in a fix attempt
   (e.g. `>` instead of `>=`) is easy to introduce here.

A strong candidate reaches step 7 within 15-25 minutes given the failing
tests as a starting point, having read `coupon_service.py` and
`coupon_repository.py` side by side.

## Part B — the fixed-amount discount type

1. Read the feature request and the currently-failing
   `test_apply_fixed_amount_discount` / `test_apply_fixed_amount_discount_endpoint`
   tests: applying a `"fixed_amount"` coupon currently raises
   `UnsupportedDiscountTypeError` (400 at the API level).
2. Find `CouponService.apply_discount`; notice it only implements the
   `"percentage"` branch and falls through to the error for anything
   else. Notice also that `Coupon` and the seeded repository data
   (`SAVE5`, `BIGDISCOUNT`) already carry `fixed_amount_cents` — the data
   model is ready, only the business logic is missing.
3. Add a `"fixed_amount"` branch: `subtotal_cents -
   coupon.fixed_amount_cents`. Re-run tests; the public fixed-amount test
   now passes.
4. A strong candidate reads the feature request text again — "make sure
   it behaves sensibly if the discount is bigger than the order total —
   we don't want a negative total" — and proactively tests or reasons
   through the case where `fixed_amount_cents > subtotal_cents`, noticing
   the naive subtraction goes negative. A candidate who stops at step 3
   without considering this has an implementation that passes every
   *public* test but fails the hidden boundary test.
5. Clamp: `max(subtotal_cents - coupon.fixed_amount_cents, 0)`.
6. Confirm the `"percentage"` branch and its rounding are untouched — a
   candidate should re-run the full suite (not just the fixed-amount
   tests) to confirm nothing about the existing percentage arithmetic
   shifted.
7. Re-run the full suite; confirm all public tests pass and add or run
   the exceeds-subtotal scenario mentally or as a test.

A strong candidate reaches a complete, clamped fixed-amount
implementation within 10-15 minutes of starting Part B, having noticed
the boundary condition from the feature request's own wording rather than
needing it pointed out.
