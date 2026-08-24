# Bug Design (private — do not expose to candidate)

## Expected behavior

`POST /expense-reports/:id/approve` and `POST /expense-reports/:id/reject`
must only succeed for a caller who is actually authorized to act on *that
specific report*: the report's `assignedManagerId`, its
`delegatedApproverId` (once the delegation feature exists), or an admin.
Invariant: "a user may only approve/reject an expense report if they are
its `assignedManagerId`, its `delegatedApproverId`, or an admin — never
merely because they hold the `manager` role in general."

## Actual (buggy) behavior

`middleware/requireRole.ts` is correctly wired to the `approve`/`reject`
routes and correctly rejects any caller who is not a `manager` or `admin`
globally. But `ExpenseReportService.approveReport` and `.rejectReport`
(`src/services/expenseReportService.ts`) never compare the acting user
against `report.assignedManagerId` — both accept an `actingUserId`
parameter and never read it. Any user holding the `manager` role can
approve or reject any pending report, not just the ones assigned to them.

## Root cause

A missing resource-level authorization check layered on top of an
otherwise-correct coarse role gate. `requireRole('manager', 'admin')`
answers "does this caller hold an allowed role at all?" — it has no
knowledge of which specific expense report is being acted on, and was
never meant to. The service layer was supposed to be the place that checks
"is this caller allowed to act on *this* report," and it simply doesn't:
`approveReport`/`rejectReport` accept `actingUserId` as a parameter but the
function body never references it. This is a different bug shape than "the
role check itself is broken" — the role check is fine; what's missing is
the second, resource-level check that should run after it.

## Violated invariant

"A user may only approve/reject an expense report if they are its
`assignedManagerId`, its `delegatedApproverId` (once delegation exists), or
an admin — never merely because they hold the `manager` role in general."
(Stated in the candidate README as the reported bug; implied by the general
semantics of a per-record approval workflow.)

## Relevant execution path

`POST /expense-reports/:id/approve` (or `/reject`)
(`src/routes/expenseReports.ts`) → `attachUser`
(`src/middleware/attachUser.ts`, correct — populates `req.user` from the
`X-User-Id` header) → `requireRole('manager', 'admin')`
(`src/middleware/requireRole.ts`, correct — confirms the caller holds one
of the allowed roles, but has and needs no notion of *which* report) →
`approveExpenseReport`/`rejectExpenseReport` controller
(`src/controllers/expenseReportController.ts`, thin — passes
`req.user!.id` straight through to the service) →
`ExpenseReportService.approveReport`/`.rejectReport`
(`src/services/expenseReportService.ts`, **the bug**) →
`ExpenseReportRepository.getById`/`.save`
(`src/repositories/expenseReportRepository.ts`, a plain `Map`-backed
store — correct, no aliasing issue). The candidate must also read
`repositories/userRepository.ts` (correct, given) to understand where role
and identity information comes from.

## Evidence available to the candidate

- The failing public tests (`rejects approval from a manager who is not
  this report's assigned manager`, and its `reject` mirror) reproduce the
  exact reported scenario at both the service and HTTP layers.
- The README states the user complaint verbatim: a different manager than
  the employee's own approved the report.
- Reading `expenseReportService.ts::approveReport`/`.rejectReport`
  end-to-end reveals `actingUserId` is accepted but never used in either
  function body.
- `GET /expense-reports/:id` correctly reports the right `assignedManagerId`
  for a report, which a candidate can use to confirm the *data* is correct
  and the problem is purely that it's never checked.

## Reasonable hypotheses

1. (Plausible, wrong) `requireRole` itself is broken and letting through
   people who aren't managers at all. Ruled out by a direct test showing
   `requireRole('manager')`-gated routes correctly return 403 for a plain
   employee (see the public test `rejects approval from a plain employee`)
   — the role check itself works; it's what happens *after* the gate that's
   missing.
2. (Plausible, wrong) `userRepository` has stale or incorrect
   manager-assignment data. Ruled out because `GET /expense-reports/:id`
   correctly shows the right `assignedManagerId` for the report in
   question — the data is correct, it's simply never checked at approval
   time.
3. (Correct) The service never compares the acting user's id against the
   report's `assignedManagerId` (or `delegatedApproverId`, once delegation
   exists).

## Intended regression tests

The two already-failing public tests (one at the service layer, one at the
HTTP layer, plus their `reject` mirrors) plus the hidden tests in
`hidden_tests/expenseReportsHidden.test.ts` covering: delegated approval
actually taking effect on both `approve` and `reject`; delegation being
restricted to the report's own assigned manager (or an admin); delegation
being rejected once a report is no longer pending; delegating to a
non-manager being rejected; the original assigned manager retaining their
own authority after naming a delegate; and the admin override surviving
through all of the above.

## Acceptable fixes

- Add a check in `approveReport`/`rejectReport` (and `delegateApproval`,
  where relevant) that the acting user is the report's
  `assignedManagerId`, its `delegatedApproverId` (for approve/reject only),
  or an admin, throwing a typed error the controller maps to 403 otherwise.
- Equivalent phrasings: a shared private helper consulted by both
  `approveReport` and `rejectReport` (the reference solution's approach), a
  small "can this user act on this report" method on the service, or
  inlined duplicate checks in both functions — acceptable as long as
  `approveReport`, `rejectReport`, *and* the check's interaction with
  `delegatedApproverId` are all consistent with each other.
- The fix must **not** stop at only checking `assignedManagerId` and
  forgetting `delegatedApproverId` once delegation exists — see "Tempting
  but incomplete/wrong fix" below.
- The fix must **not** remove or weaken `requireRole`'s coarse gate — the
  resource-level check is additive, not a replacement for the role check.

## Tempting but incomplete/wrong fix

A candidate correctly adds the `assignedManagerId` check to
`approveReport`/`rejectReport` — fixing the literally reported bug, so an
unrelated manager is now correctly rejected with 403 — but does not extend
that check to also accept `delegatedApproverId`. In this version,
`POST /expense-reports/:id/delegate` "works" in the sense that it validates
its inputs and sets `report.delegatedApproverId`, returning a 200 — but
the field has zero actual effect on who can approve or reject: the delegate
still gets rejected with 403 when they try to act on the report, exactly as
an unrelated manager would.

Because the public tests only exercise the originally reported scenario
(an unrelated manager attempting to approve, with no delegation involved)
plus a bare check that the delegate endpoint exists and sets the field,
they **cannot distinguish** this incomplete fix from the correct one — both
pass every public test. Only a hidden test that actually delegates and then
has the delegate attempt to approve or reject catches it. See
`hidden_tests/expenseReportsHidden.test.ts`'s `delegated approval — approve
path` and `delegated approval — reject path` tests, one per twin function,
so a fix applied to only one of `approveReport`/`rejectReport` is also
caught.

## Why this is interview-appropriate for an Amazon-style capstone OA

A coarse role-based middleware gate that is correct for what it checks, but
insufficient on its own for an operation that needs *resource-level*
(per-record) authorization, is one of the most common real backend
vulnerability classes — "is this a manager" is not the same question as "is
this a manager for *this* record," and code that gets the first right while
silently skipping the second ships to production constantly. This is a
structurally different lesson from a bug in an unscoped repository query
(the shape used elsewhere in this curriculum's authorization-themed
project): here the gate and the data are both correct in isolation, and the
missing piece is a check that should exist at a different layer entirely.
The delegation feature is deliberately shaped to tempt the same class of
incomplete fix a second time, in code the candidate writes themselves,
which is exactly the generalization signal this capstone is designed to
test — see `scoring_rubric.md`'s dedicated generalization category and
`ai_skill_audit.md`'s discussion of why an unconstrained agent doesn't
reliably get this right on a single pass either.
