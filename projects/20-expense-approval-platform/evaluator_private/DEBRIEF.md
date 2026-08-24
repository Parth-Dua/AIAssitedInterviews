# Interview Follow-Up Questions (private)

1. **What was the root cause?**
   Strong answer: `requireRole('manager', 'admin')` correctly confirms the
   caller holds an allowed *role*, but has no notion of which specific
   report is being acted on. `ExpenseReportService.approveReport` and
   `.rejectReport` were supposed to close that gap by checking the caller
   against the report's own `assignedManagerId`, but both accepted
   `actingUserId` as a parameter and never referenced it in the function
   body — so any manager could approve or reject any pending report.

2. **Why isn't a coarse role check like `requireRole('manager')` sufficient
   here?**
   Strong answer: a coarse role check answers "does this caller hold this
   role at all," which is the right question for some operations (e.g.
   "only employees can submit a report") but the wrong question for a
   per-record operation like approving *this specific* report. Two
   different managers both pass `requireRole('manager')` identically; only
   a check against the report's own `assignedManagerId` (or
   `delegatedApproverId`) can distinguish "this manager owns this report"
   from "this manager owns some other report." The two checks are
   complementary, not substitutes for each other.

3. **Why does your fix need to apply to both `approve` and `reject`, and to
   delegation?**
   Strong answer: the invariant is "only the assigned manager, delegate, or
   an admin may act on this report" — `approve` and `reject` are just two
   different actions gated by the identical rule, so a fix that only
   touches one leaves the other silently broken. Delegation adds a second
   valid identity (`delegatedApproverId`) to that same rule; if the
   authorization check inside `approveReport`/`rejectReport` isn't extended
   to recognize it, the delegation feature "works" in the sense that it
   sets a field and returns 200, but has literally no effect on who can
   approve or reject — the delegate is still rejected exactly like an
   unrelated manager would be.

4. **How did you verify your fix didn't just make the given tests pass?**
   Strong answer: checked that the assigned manager and admin happy paths
   still work; checked that a plain employee is still rejected (didn't
   accidentally loosen `requireRole`); wrote or reasoned through a test
   where a manager delegates and the delegate then actually attempts the
   approve/reject, not just that the delegate endpoint returns 200; checked
   the reject-path mirror of every approve-path test, since both functions
   have the identical shape and the identical gap.

5. **How would you extend this if a manager could delegate to MULTIPLE
   people, or if delegation needed an expiry?**
   Strong answer for multiple delegates: `delegatedApproverId: string |
   null` would need to become a list (or a separate join-table-style
   structure in a real database), and the authorization check would need
   to check membership in that list instead of equality; the core
   invariant — "only the assigned manager, an authorized delegate, or an
   admin" — doesn't change, only how "authorized delegate" is represented
   and looked up. Strong answer for expiry: the report (or a separate
   delegation record) would need a `delegationExpiresAt` timestamp, and the
   authorization check would need to also confirm the current time is
   before that expiry — worth discussing what should happen to an in-flight
   pending report once a delegation expires (does authority revert to the
   assigned manager automatically? does it need to be re-delegated?). A
   candidate who can articulate that the *check itself* stays structurally
   the same and only the data source changes is showing strong design
   instincts.

6. **What tests would you add, and why?**
   Strong answer: a delegate-then-approve test and its reject-path mirror
   (catches the "delegation has no effect" trap, one test per twin
   function); a non-assigned-manager delegation-rejection test (delegation
   itself needs the same "only the assigned manager or admin" gate);
   a delegate-to-non-manager rejection test; a delegate-on-non-pending
   -report rejection test; an admin-override test confirming an admin can
   still approve/reject regardless of any delegation state; a test that the
   original assigned manager retains their own authority after naming a
   delegate (delegation should be additive, not a transfer).
