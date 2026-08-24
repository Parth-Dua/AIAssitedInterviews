# Expected Reasoning Path

1. Run `pytest -q`; observe
   `test_renewed_loan_with_future_renewed_due_date_is_not_overdue` fails
   while everything else passes.
2. Read the assertion: a loan due 2026-06-15 (past), renewed to
   2026-08-01 (future), checked `as_of` 2026-07-20 — expected not overdue,
   actual overdue.
3. Open `app/api/routes/loans.py`; confirm `as_of` comes straight from the
   query parameter and is passed through unmodified.
4. Open `app/services/loan_service.py`; confirm `list_overdue` is a
   one-line pass-through to the repository — no logic to inspect here.
5. Open `app/repositories/loan_repository.py::get_overdue_loans`; find the
   `select(Loan).where(...)` call. Notice the WHERE clause has exactly two
   conditions: `Loan.returned_at.is_(None)` and `Loan.due_at < as_of`.
   Notice `renewed_due_at` is never mentioned.
6. Open `app/models/orm.py`; read the `Loan` model, in particular the
   `renewed_due_at` field and its docstring ("supersedes due_at" when
   present). Connect this to what the repository is missing.
7. Recognize the fix: the due-date comparison should use the effective due
   date — `renewed_due_at` if set, else `due_at` — not `due_at` alone. In
   SQL, this is `func.coalesce(Loan.renewed_due_at, Loan.due_at) < as_of`.
8. Apply the fix; re-run `pytest -q`; the previously-failing test now
   passes and nothing else regresses.
9. Reason through additional cases by hand or by writing new tests: a
   renewed loan whose new due date has *also* passed (still overdue); a
   loan whose renewal *shortened* the due date (renewed_due_at earlier than
   due_at); the exact boundary date; returned loans with a past effective
   due date. Confirm these all behave correctly against the fix.
10. Explain: the query was written (or last touched) before the renewal
    column was wired into the overdue check, so the read path drifted from
    what the model actually supports.

A strong candidate reaches step 7 within 15-25 minutes given the failing
test and the four small files to read. The extra step here versus a
single-file bug (Project 1) is recognizing that the fix belongs in the
repository's query, not the service or route — which requires reading all
three layers plus the model before editing.
