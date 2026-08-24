# Expected Reasoning Path

1. Run `npm test`; observe that `rejects approval from a manager who is not
   this report's assigned manager` fails in both
   `tests/expenseReportService.test.ts` and `tests/expenseReportsApi.test.ts`,
   along with the equivalent `reject` test and the not-yet-implemented
   `delegate` test, while everything else passes.
2. Read the failure output for the approval tests: the call/request succeeds
   (200, no thrown error) when it should have been rejected with 403.
3. Read the README's bug report and confirm it matches: an employee's report
   was approved by a manager who wasn't their own.
4. Trace the request path: `routes/expenseReports.ts` wires
   `POST /expense-reports/:id/approve` and `/reject` through `attachUser`
   then `requireRole('manager', 'admin')` before reaching the controller.
   Read `requireRole.ts` and confirm — ideally by running the "rejects
   approval from a plain employee" test, which already passes — that the
   role gate itself correctly blocks non-managers. This rules out "the role
   check is broken."
5. Read `attachUser.ts` to understand what `req.user` actually contains
   (id + role, from the `X-User-Id` header) — this clarifies what "the
   acting user" means for the rest of the trace.
6. Read `expenseReportController.ts::approveExpenseReport`/
   `rejectExpenseReport` — thin, passes `req.user!.id` straight into the
   service. Not the bug.
7. Open `services/expenseReportService.ts::approveReport`/`.rejectReport`.
   Notice each function accepts `actingUserId` as a parameter but the
   function body never reads it — the report's `assignedManagerId` is
   never compared against the caller at all.
8. Confirm this is the root cause: it exactly explains why *any* manager
   (not just the assigned one) can approve/reject, matching both the
   failing tests and the bug report. Optionally, also check
   `GET /expense-reports/:id` to confirm `assignedManagerId` is stored
   correctly — ruling out "the data itself is wrong" as an alternative
   explanation.
9. Fix `approveReport` and `rejectReport` to require
   `actingUserId === report.assignedManagerId` or an admin, before applying
   the status change; a typed error the controller maps to 403.
10. Design and implement `POST /expense-reports/:id/delegate`: only the
    report's own `assignedManagerId` (or an admin) may call it, only while
    `status === 'pending'`, and only naming another manager as the target;
    it sets `delegatedApproverId`.
11. Critically: go back to the fix from step 9 and extend the authorization
    check in *both* `approveReport` and `rejectReport` to also accept
    `actingUserId === report.delegatedApproverId`. A candidate who stops
    after step 10 has implemented a delegation feature that sets a field
    nothing else reads — the delegate is still rejected when they try to
    act on the report. Recognizing this without being told is the
    generalization signal this capstone is designed to test.
12. Re-run tests; write or extend tests covering: the delegate actually
    being able to approve/reject after a delegation; delegation itself
    being restricted to the report's own assigned manager; delegation being
    rejected once the report is no longer pending; and the admin override
    still working through all of the above.
13. Explain: the coarse `requireRole('manager', 'admin')` gate answers "is
    this caller a manager at all," never "is this caller *this report's*
    manager (or its delegate)." The service layer was supposed to close
    that second gap and didn't. The delegation feature adds a second valid
    identity (`delegatedApproverId`) that the same authorization check must
    also recognize — which is why the fix has to touch `approveReport` and
    `rejectReport` consistently, not just patch the one reported scenario.

A strong candidate reaches step 9 within 20-30 minutes given the failing
tests and README as a starting point, completes the delegation feature by
step 11 within the 60-90 minute timebox, and — ideally without being told —
notices on their own that the delegation check needs to land in the same
two functions the original fix touched, rather than discovering it only
when a hidden test (which they don't have access to) would have caught it.
