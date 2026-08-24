# Scoring Rubric — Project 8 (100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the route → service → repository → domain flow; noticed `CouponRepository.save()`/`get_by_code()` return defensive copies (read the repository, didn't just stare at the service in isolation) before editing. |
| Debugging process | 10 | Reproduced the reported bug via the failing tests (or an equivalent manual repro: redeem a small-limit coupon to its cap, then check a *fresh* `GET`) before making changes; didn't shotgun-edit across files. |
| Root-cause reasoning | 15 | Correctly identifies that `coupon.status` is mutated *after* the `save()` call that persists a defensive copy, so the mutation never lands in the stored record; can articulate the general invariant violated ("a state transition must be applied before, not after, handing the object to a copy-on-write store"). |
| Bug-fix correctness | 15 | Public and hidden exhaustion-boundary tests pass, including the exact-boundary hidden test (max-th redemption exhausts, not one before or after) and the API-level rejected-with-no-further-increment hidden test; the workspace's `redemption_count` persistence (already correct) is left alone. |
| Feature implementation quality | 20 | `apply_discount` gains a `"fixed_amount"` branch that clamps to `0` rather than going negative; `"percentage"` branch and its rounding are byte-for-byte unchanged; the `UnsupportedDiscountTypeError` fallback for genuinely unknown types is preserved. |
| Tests added | 10 | Added at least one regression test beyond the given failing ones — ideally an exact-boundary exhaustion test and/or a fixed-amount-exceeds-subtotal test, since those are the two ways a narrow fix slips through. |
| Scope discipline | 5 | Did not modify `CouponRepository`'s defensive-copy behavior, the domain `Coupon` class, or unrelated endpoints without justification; changes stayed within `coupon_service.py` (plus tests). |
| Communication | 15 | Can clearly state: the redemption bug's root cause and why the fix is correct; why the fix belongs in the service's call ordering rather than in removing the repository's defensive copy; why the naive unclamped fixed-amount implementation is wrong and what test would catch it; what they checked to confirm both the fix and the feature work together. |

**Passing bar (strong intern/new-grad signal):** ≥75, all hidden tests
pass, and the candidate can explain both the lost-exhaustion-state root
cause and why the defensive copy in the repository is correct design (not
something to remove), without prompting.

**Red flags:**
- Fix passes the reported-bug test but only "works" because the candidate
  special-cased the specific public-test coupon (`LOYALTY3`/`LOYALTY2`)
  rather than fixing the general ordering mistake — verify with the
  hidden exact-boundary test, which uses the same coupons but checks
  intermediate states the public test doesn't.
- Candidate "fixes" the bug by having `CouponRepository.save()` store the
  exact object reference it was given (removing the defensive copy)
  instead of reordering the service's mutation before the save call —
  this happens to make the one reported bug disappear but destroys a
  legitimate, intentional protection and is a scope-discipline violation
  independent of whether tests pass.
- Candidate implements `fixed_amount` as a plain subtraction with no
  clamp — passes every public test (including the public fixed-amount
  test) but fails the hidden
  `test_fixed_amount_discount_exceeding_subtotal_clamps_to_zero`. A
  candidate who ran `pytest -q` against only the public suite and
  declared victory without considering the "discount bigger than the
  order" edge case mentioned in the feature request itself is a process
  red flag independent of the fix's own correctness.
- Candidate cannot explain *why* either the fix or the fixed-amount clamp
  is correct, only that changing X made a test pass.
- Candidate verifies the bug fix only by inspecting `redeem()`'s own
  return value, never by re-fetching the coupon independently — this is
  exactly the trap that would let the original bug slip through code
  review.
- Candidate rewrites large parts of the service or repository layer "to
  be safe."
