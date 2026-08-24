# Bug + Feature Design (private — do not expose to candidate)

This project bundles a redemption-state bug and a feature-implementation
task that share the same code path (`CouponService`), so they're
documented together.

## Seed data (for reference while reading the tests)

Coupons (`app/repositories/coupon_repository.py`):

| code | discount_type | value | max_redemptions | status |
|---|---|---|---|---|
| WELCOME10 | percentage | 10% | 100 | active |
| SAVE5 | fixed_amount | 500 cents | 50 | active |
| BIGDISCOUNT | fixed_amount | 2000 cents | 10 | active |
| RETIRED | percentage | 15% | 10 | **cancelled** |
| LOYALTY3 | percentage | 20% | 3 | active |
| LOYALTY2 | percentage | 8% | 2 | active |
| HOLIDAY2 | percentage | 12% | 2 | active |

The small `max_redemptions` coupons (`LOYALTY3`, `LOYALTY2`, `HOLIDAY2`)
exist so tests can exhaust a coupon in a handful of calls without seeding
hundreds of redemptions. `RETIRED` is seeded already `cancelled`, for
the always-rejected-regardless-of-count baseline.

## Part A — The lost-exhaustion-state bug

### Expected behavior
Once a coupon's `redemption_count` reaches its `max_redemptions`, its
persisted `status` must become `"exhausted"`, and any subsequent
`redeem()` call must be rejected — visible on a fresh read of the coupon
(`GET /coupons/{code}` or a fresh `repository.get_by_code(code)` call),
not just in whatever object a prior call happened to return.

### Actual (buggy) behavior
`app/services/coupon_service.py::CouponService.redeem`:

```python
def redeem(self, code: str) -> Coupon:
    coupon = self._repository.get_by_code(code)
    if coupon is None:
        raise CouponNotFoundError(code)
    if coupon.status != "active":
        raise CouponNotRedeemableError(code, coupon.status)
    coupon.redemption_count += 1
    self._repository.save(coupon)
    if coupon.redemption_count >= coupon.max_redemptions:
        coupon.status = "exhausted"
    return coupon
```

`coupon.status` is mutated to `"exhausted"` **after** the call to
`self._repository.save(coupon)`. `CouponRepository.save()` (and
`get_by_code()`) deliberately make a **defensive copy** of whatever
`Coupon` they're handed — a legitimate, correct design choice, not a bug
in the repository — so that mutation to the local `coupon` variable never
reaches the copy actually stored in the repository. The next call to
`redeem()` fetches a *fresh* copy via `get_by_code()`, which still shows
`status == "active"`, so the guard clause
(`if coupon.status != "active": raise ...`) never fires. A coupon can
therefore be redeemed indefinitely past its stated limit.

Note the asymmetry that makes this subtle: `redemption_count` **is**
correctly persisted, because that mutation happens *before* the `save()`
call. Only the `status` mutation — which happens after — is silently
lost. A candidate who only checks `redemption_count` (which climbs
correctly) can easily miss that `status` never updates.

Also note: the object `redeem()` *returns* to its caller is the same
local `coupon` instance that was mutated after `save()` — so it correctly
shows `status="exhausted"` in the redeem call's own response. The bug is
only observable via a **separate, subsequent read** (a fresh
`GET /coupons/{code}` or `get_by_code()` call), never in the redeem
response itself. This is exactly what makes the bug easy to miss in
casual manual testing: hitting the redeem endpoint and eyeballing its
response looks completely correct.

### Root cause
The service mutates `coupon.status` **after** calling
`self._repository.save(coupon)`, but `save()` defensively copies its
input, so that final mutation is never persisted. Violated invariant:
"once a coupon's redemption count reaches its max, no further redemptions
may succeed" — silently broken because the state transition that enforces
it never lands in the stored record.

### Relevant execution path
`POST /coupons/{code}/redeem` (`app/api/routes/coupons.py`) →
`CouponService.redeem` (`app/services/coupon_service.py`, the bug) →
`CouponRepository.save` / `get_by_code`
(`app/repositories/coupon_repository.py`, correct — the defensive-copy
behavior must be *read and understood*, not fixed) → `Coupon`
(`app/domain/coupon.py`). This is genuinely multi-file reasoning: the bug
line itself is in the service, but understanding *why* it's a bug
requires reading the repository's `save`/`get_by_code` implementation and
recognizing that a `Coupon` object handed to `save()` is not the same
object subsequently returned by `get_by_code()`.

### Evidence available to the candidate
- The public tests `test_redeeming_beyond_max_redemptions_is_rejected`
  and `test_exhausted_coupon_status_visible_on_fresh_get` (API level) and
  their unit-level twins in `test_coupon_service.py` reproduce the exact
  reported scenario using the small `LOYALTY3`/`LOYALTY2` coupons.
- `redeem()`'s own docstring and structure show `redemption_count` is
  incremented and saved, then `status` is checked and set — reading the
  order of operations against `CouponRepository.save`'s docstring (which
  plainly explains it returns/stores a defensive copy) reveals the gap.
- A candidate who prints or asserts on the *return value* of `redeem()`
  alone will see `status="exhausted"` and wrongly conclude the code is
  correct — only a subsequent, independent `get_by_code`/`GET` call
  reveals the discrepancy. This is intentional: it's exactly the
  distinction a careful candidate must notice.

### Reasonable hypotheses
1. **(Correct)** The exhausted-status mutation happens after the
   defensive-copy `save()` call and is silently lost — the persisted
   coupon's `status` never updates even once `redemption_count` reaches
   `max_redemptions`.
2. **(Plausible, wrong)** `redemption_count` itself isn't being
   incremented or persisted correctly. Ruled out by observing, via a
   fresh `GET /coupons/{code}` after each redemption, that
   `redemption_count` climbs correctly and exactly matches the number of
   successful redemption calls — only `status` fails to update. A
   candidate who checks `redemption_count` in isolation and stops there
   (without also checking `status` on a fresh read) will miss the actual
   bug.

### Intended regression tests
`test_redeeming_beyond_max_redemptions_is_rejected` and
`test_exhausted_coupon_status_visible_on_fresh_get` (API, public) and
their unit-level twins in `test_coupon_service.py` — already present.
Plus the hidden `test_exhaustion_boundary_is_exact_not_off_by_one`, which
checks the exact redemption at which the boundary crosses (the
`max_redemptions`-th call exhausts — not one before, not one after) from
a fresh repository fetch, and the hidden
`test_redeem_exhausted_coupon_returns_409_and_does_not_increment_again`,
which is the same check via the live HTTP API using a coupon untouched by
any other test.

### Acceptable fixes
- Reorder: set `coupon.status = "exhausted"` **before** the (single)
  `self._repository.save(coupon)` call. This is the reference fix.
- Equivalent: leave the first `save()` call where it is (after
  incrementing `redemption_count`) and add a **second** `save()` call
  after the `status` mutation. Redundant (two saves where one would do)
  but functionally correct — both `redemption_count` and the final
  `status` end up persisted.
- Not acceptable: any fix that removes or bypasses the defensive copy in
  `CouponRepository` itself (e.g., having `save()` store the exact object
  reference it was given) — that "fixes" this one call site by
  discarding a legitimate, intentional protection against a different,
  broader class of bugs (external code holding a reference and mutating
  repository-owned state later without going through `save()`). The fix
  belongs in the service's call ordering, not in the repository's
  contract.

## Part B — The fixed-amount discount type feature

### Requested behavior
`CouponService.apply_discount(coupon, subtotal_cents)` must dispatch on
`coupon.discount_type`. `"percentage"` behavior is unchanged (exact same
arithmetic/rounding as before). `"fixed_amount"` must subtract
`coupon.fixed_amount_cents` from the subtotal and **never return a
negative total** — clamp to `0` when the fixed discount is larger than
the subtotal.

### Starting (incomplete) state
`Coupon` already carries both `percent_value` and `fixed_amount_cents`
fields, and the repository already seeds real `"fixed_amount"` coupons
(`SAVE5`, `BIGDISCOUNT`) — the data model is ready. `apply_discount` only
implements the `"percentage"` branch and raises
`UnsupportedDiscountTypeError` for anything else, including
`"fixed_amount"`. This is a deliberately plausible "data model shipped
ahead of the business logic" starting state, not an obviously missing
stub.

### Correct design
Add a `"fixed_amount"` branch to `apply_discount`:

```python
if coupon.discount_type == "fixed_amount":
    return max(subtotal_cents - coupon.fixed_amount_cents, 0)
```

Leave the `"percentage"` branch and the final `raise
UnsupportedDiscountTypeError(...)` fallback untouched.

### Tempting but incomplete/wrong implementation
Implementing the same branch **without** the clamp:

```python
if coupon.discount_type == "fixed_amount":
    return subtotal_cents - coupon.fixed_amount_cents
```

This is correct for every case where the fixed discount is smaller than
the subtotal — which is most of the "obvious" manual test cases a
candidate is likely to try (e.g., "$5 off a $20 order = $15") — and so it
passes every *public* test, including the public fixed-amount test
(`SAVE5`, 500 cents off a 2000-cent subtotal → 1500, never negative).
It only breaks once the discount **exceeds** the subtotal, which the
public suite never exercises. Caught by the hidden
`test_fixed_amount_discount_exceeding_subtotal_clamps_to_zero`
(`BIGDISCOUNT`, 2000 cents off a 500-cent subtotal — the naive version
returns `-1500`).

### Acceptable implementations
- The reference branch above (`max(subtotal_cents -
  coupon.fixed_amount_cents, 0)`).
- Equivalent: an explicit `if subtotal_cents <= coupon.fixed_amount_cents:
  return 0` guard followed by the plain subtraction — same semantics,
  more verbose.
- Not acceptable: the unclamped naive version described above, or any
  version that changes `"percentage"` behavior/rounding to accommodate
  the new branch.

### Validation performed
`reference_solution/coupon_service.py` was applied to a temporary copy of
the candidate repository, hidden tests were copied into `tests/`, and
`pytest -q` was run: **18 passed** (14 public + 4 hidden). Separately, the
naive unclamped `fixed_amount` implementation described above (with the
redemption-state bug otherwise correctly fixed exactly as in the
reference) was applied the same way: **1 failed, 17 passed** — the single
failure was exactly
`test_fixed_amount_discount_exceeding_subtotal_clamps_to_zero`; every
other public and hidden test passed, confirming the naive version is
genuinely tempting (it clears the full public suite) and that the hidden
test is what catches it. The original, untouched candidate starting state
was re-verified afterward: **6 failed, 8 passed**
(`test_coupon_service.py::test_redeeming_beyond_max_redemptions_is_rejected`,
`test_coupon_service.py::test_exhausted_coupon_status_is_persisted`,
`test_coupon_service.py::test_apply_fixed_amount_discount`,
`test_coupons_api.py::test_redeeming_beyond_max_redemptions_is_rejected`,
`test_coupons_api.py::test_exhausted_coupon_status_visible_on_fresh_get`,
`test_coupons_api.py::test_apply_fixed_amount_discount_endpoint`),
confirming the intended pass/fail split.

## Why this is interview-appropriate

A state transition that's supposed to persist getting silently dropped
because it's applied to a mutable object *after* that object was already
handed off to a defensive-copy-on-write store is a genuinely common and
subtle real backend bug class — it shows up any time a service holds a
domain object across a save call and keeps mutating it afterward,
assuming the mutation is "still live." It's especially realistic here
because the repository's defensive-copy behavior is itself entirely
correct and well-intentioned (protecting stored state from external
mutation) — the bug is purely about *respecting* that contract's
implication (mutate-then-save, never save-then-mutate-and-expect-it-to-
stick), not about any flaw in the repository. Pairing it with "now add a
second discount type, with a sensible edge case" is exactly the kind of
natural follow-up a real team would ask for once the redemption bug is
fixed, and the naive-vs-clamped trap is a realistic, extremely common
off-by-a-boundary-condition mistake in any code that subtracts a discount
from a total.
