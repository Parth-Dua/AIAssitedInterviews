# Scoring Rubric — Project 2 (100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the route → service → repository → model flow, and specifically that `renewed_due_at` is a real model field that the query wasn't using, before editing. |
| Debugging process | 15 | Reproduced the bug via the failing test (or equivalent manual repro) before making changes; didn't shotgun-edit across files. |
| Root-cause reasoning | 20 | Correctly identifies that `get_overdue_loans` compares against `due_at` alone instead of the coalesced effective due date (`renewed_due_at` if set, else `due_at`); can articulate why the query — not the service or route — is where the bug lives. |
| Correctness of fix | 25 | Public test passes; all hidden tests pass, including the "shortened loan" boundary case; the `<` strictness at the `as_of` boundary is preserved; returned-loan exclusion is preserved. |
| Tests added/improved | 10 | Added at least one regression test beyond the given failing one (e.g., a renewed-but-still-overdue case, or a boundary case), or meaningfully strengthened existing coverage. |
| Scope discipline | 5 | Did not modify the model, service, route, or API response shape without justification; changes stayed in the repository query (or an equivalently narrow fix). |
| Communication / explanation | 15 | Can clearly state expected vs. actual behavior, root cause, why the fix is correct, and what they checked (boundary, shortened-loan, returned-loan cases) to rule out breaking other behavior. |

**Passing bar (strong intern/new-grad signal):** ≥75, hidden tests pass, and
candidate can explain root cause without prompting.

**Red flags:**
- Fix passes the given public test but fails
  `test_shortened_loan_renewed_due_date_earlier_than_original_due_at` (the
  "keep filtering on `due_at` in SQL, patch with a Python post-filter"
  incomplete fix — see `bug_design.md`).
- Fix computes the effective due date once (e.g., at query-build time,
  outside the per-row context) instead of per row — will not compile/behave
  correctly against SQLAlchemy's column expressions, or silently produces
  wrong results if attempted in Python without fetching all rows first.
- Candidate cannot explain *why* the bug happened, only that changing X made
  the test pass.
- Candidate introduces `datetime.now()` / `date.today()` anywhere in the
  service or repository instead of relying on the passed-in `as_of`.
- Candidate rewrites large parts of the repository, service, or model "to be
  safe."
