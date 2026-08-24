# Scoring Rubric — Project 16 (100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the route → middleware → controller → service → repository flow for both `POST` and `PATCH`; read `validateTaskCreate.ts` to confirm it isn't wired to `PATCH` and isn't stripping fields, before assuming the bug was elsewhere. |
| Debugging process | 15 | Reproduced the bug via the failing tests (or equivalent manual repro with `curl`/supertest) before making changes; didn't shotgun-edit multiple files. |
| Root-cause reasoning | 20 | Correctly identifies that `TaskService.updateTask` hardcodes `status: existing.status` instead of respecting `updates.status`; can articulate why this breaks the "PATCH updates exactly the fields provided" invariant and why it's plausible production code (leftover pattern break, not an obviously-flagged bug). |
| Correctness of fix | 25 | Public tests pass; hidden tests pass — including the invalid-status-value rejection (catches the naive "just remove the hardcode" fix) and the non-linear-transition test (catches an over-eager fix that adds unwanted transition rules); `title`/`priority`/`assigneeId` updates still work; empty-body PATCH still a no-op. |
| Tests added/improved | 10 | Added at least one regression test beyond the given failing ones (e.g., an invalid-status test, a sequential-update test), or meaningfully strengthened existing coverage. |
| Scope discipline | 5 | Did not modify unrelated files/behavior (repository internals, `GET`/`POST` routes, seed data) without justification. |
| Communication / explanation | 15 | Can clearly state expected vs. actual behavior, root cause, why the fix is correct, and what else they checked (including whether they considered — and rejected — adding transition-order enforcement). |

**Passing bar (strong intern/new-grad signal):** ≥75, hidden tests pass, and
candidate can explain root cause without prompting.

**Red flags:**
- Fix passes the two originally-failing tests but fails
  `rejects an invalid status value and leaves the stored status unchanged`
  (the "remove the hardcode, forget validation" incomplete fix — see
  `bug_design.md`).
- Fix adds a status state-machine / transition guard (e.g. rejecting
  `todo → done` directly) that wasn't asked for and isn't part of the
  stated invariant — fails
  `allows jumping directly from "todo" to "done", skipping "in_progress"`.
- Candidate cannot explain *why* the bug happened, only that changing a
  line made the test pass.
- Candidate rewrites large parts of the service/controller/routing "to be
  safe," or introduces a database/ORM-style abstraction unprompted.
- Candidate never opens `validateTaskCreate.ts` and instead guesses at
  middleware behavior, or assumes the bug is in the repository (`Map`)
  layer without reading it.
