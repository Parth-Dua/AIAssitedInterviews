# Scoring Rubric — Project 1 (100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the API→service→repository flow and where `discount_code` / threshold constant come from before editing. |
| Debugging process | 15 | Reproduced the bug via the failing test (or equivalent manual repro) before making changes; didn't shotgun-edit. |
| Root-cause reasoning | 20 | Correctly identifies that the shipping-threshold check uses the post-discount subtotal instead of the pre-discount one; can articulate *why* that's wrong relative to the stated policy. |
| Correctness of fix | 25 | Public test passes; all hidden tests pass; `total_cents` invariant holds; discount computation untouched/still correct. |
| Tests added/improved | 10 | Added at least one regression test beyond the given failing one, or meaningfully strengthened existing coverage (e.g., boundary case). |
| Scope discipline | 5 | Did not modify unrelated files/behavior (API shape, repository, constants) without justification. |
| Communication / explanation | 15 | Can clearly state expected vs. actual behavior, root cause, why the fix is correct, and what they checked to rule out breaking other behavior. |

**Passing bar (strong intern/new-grad signal):** ≥75, hidden tests pass, and
candidate can explain root cause without prompting.

**Red flags:**
- Fix passes the given test but fails
  `test_discount_amount_independent_of_shipping_outcome` or
  `test_multiple_line_items_with_discount_and_free_shipping` (the "cap the
  discount" incomplete fix — see `bug_design.md`).
- Candidate cannot explain *why* the bug happened, only that changing X made
  the test pass.
- Candidate rewrites large parts of the service "to be safe."
