# Scoring Rubric — Project 3 (100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the route→service→repository flow and, specifically, read `schemas.py` to notice every `ProfileUpdateRequest` field defaults to `None` before editing. |
| Debugging process | 15 | Reproduced the bug via the failing test (or equivalent manual repro) before making changes; didn't shotgun-edit. |
| Root-cause reasoning | 20 | Correctly identifies that the merge conflates "field omitted" with "field is `None`," and articulates *why* plain `model_dump()` can't tell them apart. |
| Correctness of fix | 25 | Public tests pass; all hidden tests pass — **including** the explicit-null-clears-field case; omitted fields stay untouched; response reflects the full merged profile. |
| Tests added/improved | 10 | Added at least one regression test beyond the given failing one (e.g., another single-field PATCH, empty-body PATCH, or a null-clearing case), or meaningfully strengthened existing coverage. |
| Scope discipline | 5 | Did not modify unrelated files/behavior (API shape, repository, constants) without justification. |
| Communication / explanation | 15 | Can clearly state expected vs. actual behavior, root cause, why `exclude_unset` (not `exclude_none`) is correct, and what they checked to rule out breaking other behavior. |

**Passing bar (strong intern/new-grad signal):** ≥75, hidden tests pass
(including the null-clearing hidden test), and candidate can explain root
cause without prompting.

**Red flags:**
- Fix passes the given public test but fails
  `test_patch_explicit_null_clears_nullable_field` because the candidate
  used `exclude_none=True` instead of `exclude_unset=True` (the intended
  tempting-but-incomplete fix — see `bug_design.md`). This is the single
  most diagnostic signal in this project: it separates candidates who
  pattern-matched "drop the Nones" from candidates who understood *why*
  the fix works.
- Candidate cannot explain the difference between "field omitted" and
  "field explicitly null," only that changing X made the given test pass.
- Candidate rewrites large parts of the service "to be safe," e.g.
  reworking the repository or adding persistence/validation well beyond
  what the bug requires.
- Candidate makes `ProfileUpdateRequest` fields required or removes the
  partial-update semantics entirely to "simplify" — breaks the stated
  public API contract.
