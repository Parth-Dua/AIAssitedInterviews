# Interview Follow-Up Questions (private)

1. **What was the root cause?**
   Strong answer: the overdue-loans query compared each loan's original
   `due_at` against `as_of` and never referenced `renewed_due_at` at all, so
   a renewal that pushed the due date into the future had no effect on
   overdue status.

2. **How did you narrow it down?**
   Strong answer: ran the failing test first, read the assertion (a
   renewed loan with a future renewed due date still showed as overdue),
   then traced the request through the route and service (both trivial
   pass-throughs) into the repository, where the actual query lives.

3. **Why does your fix solve it, and could it break anything else?**
   Strong answer: it changes the comparison to use the effective due date
   (`renewed_due_at` if set, else `due_at`) instead of `due_at` alone,
   restoring the invariant without touching the returned-loan filter or the
   route/service layers. Should mention they checked that a never-renewed
   loan behaves exactly as before (falls back to `due_at`), and that the
   `<` boundary stayed strict rather than becoming `<=`.

4. **What tests would you add, and why?**
   Strong answer: a renewed loan whose renewal date has *also* passed
   (still overdue); a loan whose renewal *shortened* the due date
   (`renewed_due_at` earlier than `due_at`) to make sure the fix doesn't
   only handle "renewal pushes date later"; the exact boundary date; a
   returned loan with a past effective due date, to confirm returned status
   still wins.

5. **Suppose your fix had instead fetched all non-returned loans and
   filtered in Python with `loan.renewed_due_at or loan.due_at < as_of`,
   but kept the original `Loan.due_at < as_of` filter in the SQL query
   ahead of it. What would go wrong?**
   Strong answer: that pre-filters candidates by original due date before
   the renewal is ever considered, so a loan whose original due date is
   still in the future but whose renewal *shortened* it into the past would
   never be fetched as a candidate in the first place — it would be
   silently missing from the overdue list even though it's genuinely
   overdue. The fix has to change what the SQL query selects, not just
   post-process what it happens to return.

6. **If a librarian later wanted "loans overdue by more than N days" (for
   escalation to a fines process), how would you extend this design without
   duplicating the overdue logic?**
   Strong answer (design-forward-thinking): keep a single source of truth
   for "effective due date" — e.g. a repository helper or a SQL expression
   built once and reused — and layer the "more than N days" condition on
   top of it (`effective_due_at < as_of - N days`) rather than writing a
   second, separate overdue query that could drift out of sync with the
   first the same way this one did.
