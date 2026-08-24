# Bug Design (private — do not expose to candidate)

## Expected behavior
A loan is overdue as of a reference date `as_of` iff:
1. it has not been returned (`returned_at IS NULL`), and
2. its **effective due date** is strictly before `as_of`, where the
   effective due date is `renewed_due_at` when the loan has been renewed
   (`renewed_due_at IS NOT NULL`), otherwise `due_at`.

In SQL terms: `coalesce(renewed_due_at, due_at) < as_of`.

## Actual (buggy) behavior
`app/repositories/loan_repository.py::LoanRepository.get_overdue_loans`
filters `Loan.returned_at.is_(None)` correctly, but for the due-date
comparison it uses `Loan.due_at < as_of` — it never references
`renewed_due_at` at all. Any loan that was renewed to a later due date still
appears in the overdue list as long as its *original* due date has passed,
even though the renewal (recorded in `renewed_due_at`) pushed the real due
date into the future.

## Root cause
The query was written before renewals existed, or the renewal column was
added later (`renewed_due_at` on `Loan`) without updating the one query that
decides overdue status. `renewed_due_at` is a real, populated column — it's
just not read anywhere in the overdue query. This is a classic
"schema/column added, one query not updated to use it" bug: not a typo or an
off-by-one, but a query that's stale relative to the model it queries.

## Violated invariant
"Overdue status must always be evaluated against the loan's *current*
(post-renewal) due date, not its original due date." This is implied by the
existence of `renewed_due_at` on the model and by the bug report; it is not
spelled out as a single sentence anywhere in the candidate-facing README
(deliberately — the candidate must infer it from the model and the bug
report, the way a real engineer would from a schema and a support ticket).

## Relevant execution path
`GET /loans/overdue?as_of=...` (`app/api/routes/loans.py`) →
`LoanService.list_overdue` (`app/services/loan_service.py`, thin
pass-through) → `LoanRepository.get_overdue_loans` (the bug) →
`Loan` ORM model (`app/models/orm.py`, defines `renewed_due_at` and
`due_at`). The candidate must read all four files to notice that
`renewed_due_at` exists on the model and is documented ("supersedes
due_at") but is never referenced in the query that decides overdue status.

## Evidence available to the candidate
- The failing public test
  `test_renewed_loan_with_future_renewed_due_date_is_not_overdue`
  reproduces the exact reported scenario with concrete dates.
- The `Loan` model's docstring on `renewed_due_at` states it "supersedes
  due_at" when present.
- The service docstring states the overdue rule in prose ("effective due
  date ... is the renewed due date if the loan was renewed, otherwise the
  original due date"), which does not match what the repository actually
  does — a documentation/implementation mismatch a careful reader will
  notice.
- Reading `get_overdue_loans` end-to-end shows exactly one date comparison,
  and it only mentions `due_at`.

## Reasonable hypotheses
1. (Correct) The repository query never applies `renewed_due_at`; it should
   compare against `coalesce(renewed_due_at, due_at)` instead of `due_at`.
2. (Plausible, wrong) The renewal endpoint/write path isn't actually saving
   `renewed_due_at` to the database. Ruled out by inspecting the seeded test
   data / adding a loan with `renewed_due_at` set and confirming (e.g. via
   the ORM or a quick query) that the column is populated correctly — the
   read path is what's broken, not the write path (there is in fact no
   write/renew endpoint in this exercise; loans are seeded directly with
   `renewed_due_at` already set, which should tip a careful candidate off
   that the write side isn't in scope).
3. (Plausible, wrong) `LoanService.list_overdue` is swallowing or not
   forwarding `as_of` correctly. Ruled out by reading the service — it's a
   one-line pass-through with no logic of its own.

## Intended regression tests
Public: `test_renewed_loan_with_future_renewed_due_date_is_not_overdue`
(already present, reproduces the exact reported scenario).

Hidden (`hidden_tests/test_loans_hidden.py`):
- `test_overdue_boundary_is_strictly_before_as_of` /
  `test_overdue_boundary_one_day_past_as_of` — the `<` boundary must stay
  strict, not become `<=`, when the fix is applied.
- `test_renewed_loan_still_overdue_if_renewed_due_date_also_past` — a
  renewed loan is not unconditionally "safe"; if the renewal date itself has
  passed, it must still be overdue.
- `test_shortened_loan_renewed_due_date_earlier_than_original_due_at` — the
  test specifically designed to catch the tempting-but-incomplete fix below.
- `test_returned_loan_excluded_even_if_effective_due_date_in_past` —
  returned status always wins, regardless of how far past due the loan
  looks.
- `test_multiple_loans_mixed_states_returns_only_the_overdue_ones` — a
  mixed-state integration check across five loans in one query.

## Acceptable fixes
- Rewrite the SQL comparison to use
  `sqlalchemy.func.coalesce(Loan.renewed_due_at, Loan.due_at) < as_of`
  (the reference solution).
- Equivalent: `sqlalchemy.case()` expressing the same coalesce logic.
- Equivalent: two `select(...).where(...)` branches unioned (one for
  `renewed_due_at IS NOT NULL AND renewed_due_at < as_of`, one for
  `renewed_due_at IS NULL AND due_at < as_of`) — more verbose but
  semantically identical and acceptable.
- Not acceptable: any fix that computes the effective due date once and
  reuses it across rows (e.g. binds `renewed_due_at or due_at` to a Python
  variable outside the per-row context), or any fix that still gates
  candidate selection on `due_at < as_of` in SQL before applying a
  renewed-date check afterward (see below) — both silently drop the
  "shortened loan" case.

## Tempting but incomplete/wrong fix
Keep the existing (buggy) SQL filter `Loan.due_at < as_of` to select
candidate rows, then post-filter in Python using the renewed date:

```python
stmt = select(Loan).where(
    Loan.returned_at.is_(None),
    Loan.due_at < as_of,
)
candidates = list(session.execute(stmt).scalars().all())
return [
    loan for loan in candidates
    if (loan.renewed_due_at or loan.due_at) < as_of
]
```

This is genuinely tempting: it directly addresses the reported symptom (a
renewed loan with a future renewed due date no longer shows up, because the
Python filter excludes it), it passes the given public test, and it "looks
like" it fixed the bug by finally reading `renewed_due_at`. Verified by
actually implementing this exact fix and running it against the hidden
tests (see validation below).

It is incomplete because the SQL filter `Loan.due_at < as_of` still runs
*first*, before the renewal is considered, so it silently drops any loan
whose **original** `due_at` is not yet past — even if that loan was later
shortened (`renewed_due_at` set to a date earlier than `due_at`, and earlier
than `as_of`). Such a loan is genuinely overdue (its effective due date has
passed) but is never even fetched as a candidate, so it's missing from the
result entirely.

**Caught by:**
`hidden_tests/test_loans_hidden.py::test_shortened_loan_renewed_due_date_earlier_than_original_due_at`
— a loan with `due_at=2026-08-01` (future), `renewed_due_at=2026-07-10`
(past), checked against `as_of=2026-07-20`. The correct fix returns it as
overdue (1 loan); the tempting fix returns an empty list, because
`due_at < as_of` (`2026-08-01 < 2026-07-20`) is False and the row is
excluded before the Python-side renewal check ever runs.

### Validation performed
This tempting-but-incomplete fix was implemented verbatim in a temporary
copy of the candidate repository, with `hidden_tests/test_loans_hidden.py`
copied into `tests/`, and `pytest -q` was run against it. Result: 12 passed,
1 failed — the single failure was exactly
`test_shortened_loan_renewed_due_date_earlier_than_original_due_at`, and the
originally-failing public test
(`test_renewed_loan_with_future_renewed_due_date_is_not_overdue`) passed,
confirming the fix is tempting (it resolves the reported symptom) but
incomplete (it fails a real case the hidden tests are designed to catch).

## Why this is interview-appropriate
Classic "read a small model + repository + service + route, find a query
that ignores a column the model clearly defines, from a plausible bug
report" — a very common real-world SWE intern/new-grad debugging shape,
especially in codebases where a feature (renewals) was added incrementally
and one read path lagged behind the schema change. No specialist SQLAlchemy
or ORM knowledge is required beyond what's demonstrated in the reference
solution; the fix is fully discoverable from the code, the failing test,
and the model's own docstring.
