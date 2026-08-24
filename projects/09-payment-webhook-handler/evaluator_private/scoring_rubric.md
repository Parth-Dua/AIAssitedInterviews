# Scoring Rubric — Project 9 (100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the route→service→repository/client flow; identified that `EventLogRepository` has both `has_seen` and `record` before editing, and what each one does. |
| Debugging process | 15 | Reproduced the bug via the failing test (or equivalent manual repro) before making changes; checked the passing split-payment test to understand what must *not* break; didn't shotgun-edit. |
| Root-cause reasoning | 20 | Correctly identifies that `has_seen(event_id)` exists, is correct, and is simply never called by the service — this is a missing dedup gate, not a broken one; can articulate why deduping must key off `event_id` and not order state. |
| Correctness of fix | 25 | Public test passes; all hidden tests pass; the split-payment case (two distinct `event_id`s) still applies correctly; `record()` still logs every delivery attempt including duplicates; fulfillment call count matches distinct successfully-applied events exactly. |
| Tests added/improved | 10 | Added at least one regression test beyond the given failing one (e.g. three-plus redeliveries, or an explicit assertion that a second distinct event still applies), or meaningfully strengthened existing coverage. |
| Scope discipline | 5 | Did not modify unrelated files/behavior (API shape, repository internals, fulfillment client) without justification; did not build an unrequested concurrency/locking mechanism. |
| Communication / explanation | 15 | Can clearly state expected vs. actual behavior, root cause, why the fix is correct, why it doesn't break the split-payment case, and (as a discussion point) what a concurrent version would additionally need. |

**Passing bar (strong mid-level+ backend signal):** ≥75, hidden tests pass,
and candidate can explain root cause and the split-payment distinction
without prompting.

**Red flags:**
- Fix passes the given public test but fails
  `test_second_distinct_event_for_same_order_is_not_blocked_by_first` or
  `test_duplicate_delivery_is_still_recorded_in_audit_log` (the
  "order-status-gate" incomplete fix — see `bug_design.md`). Also flag if
  it fails the *public*
  `test_two_distinct_events_apply_as_separate_partial_payments` — that
  means the candidate didn't even re-run the full suite after their fix.
- Candidate cannot explain why deduping on `order.status` differs from
  deduping on `event_id`, only that changing X made the given test pass.
- Candidate builds a concurrency/locking mechanism unprompted, spending
  significant time on something out of scope for this exercise (it's fine,
  and expected, for them to *mention* it as a discussion point per the
  README's Deliverables — the red flag is implementing it).
- Candidate rewrites large parts of the service "to be safe."
