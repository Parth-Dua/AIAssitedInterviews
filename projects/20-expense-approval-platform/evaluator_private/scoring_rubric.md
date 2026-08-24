# Scoring Rubric — Project 20 (Capstone, 100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the route → `attachUser` → `requireRole` → controller → service → repository flow for approve/reject/delegate; read `requireRole.ts` and `attachUser.ts` to confirm the coarse role gate itself is correct before concluding the resource-level check was missing elsewhere. |
| Debugging process | 15 | Reproduced the bug via the failing tests (or equivalent manual repro) before making changes; used the passing "plain employee gets 403" test as evidence the role gate works, rather than assuming it might be broken; didn't shotgun-edit multiple unrelated files. |
| Root-cause reasoning | 20 | Correctly identifies that `ExpenseReportService.approveReport`/`.rejectReport` accept `actingUserId` but never compare it against `report.assignedManagerId`; can articulate why a coarse role check ("is this a manager") is a different question from a resource-level check ("is this *this report's* manager"), and why both are needed. |
| Bug-fix correctness | 15 | The reported-bug public tests pass (service-level and HTTP-level, for both approve and reject); an unrelated manager is rejected with a clear 4xx and the report's status is left unchanged; the assigned manager and admin happy paths are untouched. |
| Feature implementation quality | 15 | `POST /expense-reports/:id/delegate` exists, is wired correctly, only the report's own assigned manager (or an admin) can call it, only while the report is pending, validates the delegate is actually a manager, and sets `delegatedApproverId`. |
| **Generalization / consistency across approve, reject, and delegate** | 10 | **Capstone-specific category.** Did the candidate's authorization check for `approveReport` and `rejectReport` also accept `delegatedApproverId`, not just `assignedManagerId`? A candidate can get full marks on the literal bug fix and the literal feature request while shipping a delegation feature that has no actual effect on who can approve — this category is where that gets caught, scored independently of bug-fix correctness and feature quality above. |
| Tests added | 10 | Added at least one regression test beyond the given failing ones (e.g., a delegate-then-approve test, a non-assigned-manager delegation-rejection test), or meaningfully strengthened existing coverage. |
| Communication | 5 | Can clearly state expected vs. actual behavior, the precise missing-check root cause, why the fix generalizes to delegation, and what they checked to rule out other explanations. |

**Passing bar (strong new-grad+/mid-level backend signal):** ≥75, all
hidden tests pass, and the candidate can explain both the missing-check root
cause and why `approveReport`/`rejectReport` need to recognize
`delegatedApproverId` without being prompted.

**Red flags:**
- Authorization check added only for `assignedManagerId`, with
  `delegatedApproverId` never consulted (passes the reported-bug public
  tests and the bare "delegate endpoint exists" public test, but fails the
  hidden `delegated approval — approve path` and `delegated approval —
  reject path` tests — see `bug_design.md`). This is the single most
  important red flag for this project: it means the candidate fixed the
  literally-reported bug but did not generalize the underlying rule to a
  sibling feature they implemented themselves, in the same session, in the
  same file.
- Fix applied to only one of `approveReport`/`rejectReport` (e.g. approve
  checks `assignedManagerId`/`delegatedApproverId` correctly but reject
  still doesn't) — passes half the hidden suite, fails the other half.
- Candidate cannot explain *why* the original code was wrong — only that
  changing a line made a test pass.
- Candidate weakens or removes `requireRole`, or moves the resource-level
  check into `requireRole` itself in a way that couples it to a specific
  route's URL structure rather than the report being acted on.
- Candidate rewrites large parts of the service/controller/routing "to be
  safe," or introduces a database/ORM-style abstraction unprompted.
- Candidate never reads `requireRole.ts`/`attachUser.ts` and instead
  guesses at what `req.user` contains, or assumes the coarse role gate
  itself is the broken component without testing that hypothesis.
