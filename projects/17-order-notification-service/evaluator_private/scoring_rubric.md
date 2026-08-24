# Scoring Rubric — Project 17 (100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the route → validation middleware → controller → service → notifier → app-level error-handler-registration flow; read `app.ts` and `errorHandler.ts` to confirm middleware ordering isn't the problem, and read/ran `warehouseNotifier` in isolation to confirm it isn't hanging internally, before concluding the bug was in the controller. |
| Debugging process | 15 | Reproduced the bug via the failing test (or an equivalent manual repro — e.g., `curl`/supertest with a bounded timeout) before making changes; didn't shotgun-edit multiple files. |
| Root-cause reasoning | 20 | Correctly identifies that `createOrder` is an async Express 4 route handler that `await`s a promise which can reject, with no `try/catch` and no wrapping, so the rejection never reaches `next(err)`/`errorHandler.ts` and no response is ever sent; can articulate *why* Express 4 doesn't handle this automatically (no built-in promise-rejection-to-`next()` forwarding for async handlers, unlike Express 5). |
| Correctness of fix | 25 | Public tests pass; hidden tests pass — including the error-contract test (catches the "catch the error but respond directly, bypassing `errorHandler.ts`" incomplete fix), the second-offline-warehouse-id generalization test, and the sequential-request test (a failed order doesn't leave the app unable to handle the next one); reachable-warehouse orders and the 400-for-missing-fields path still work. |
| Tests added/improved | 10 | Added at least one regression test beyond the given failing one (e.g., asserting the specific error status/body for an unreachable warehouse, or a second offline-warehouse-id case), or meaningfully strengthened existing coverage. |
| Scope discipline | 5 | Did not modify unrelated files/behavior (repository internals, `warehouseNotifier`'s offline-set logic, validation rules, the `requestLogger`) without justification. |
| Communication / explanation | 15 | Can clearly state expected vs. actual behavior, root cause, why the fix is correct, and what else they checked (including whether the error response now matches the app's established contract, not just "some response now comes back"). |

**Passing bar (strong intern/new-grad signal):** ≥75, hidden tests pass, and
candidate can explain root cause without prompting.

**Red flags:**
- Fix passes the originally-failing public test but fails `responds with
  the app's real error contract, not an ad-hoc bypass response` (the
  "catch the error but `res.status(500).send(...)` directly instead of
  `next(err)`" incomplete fix — see `bug_design.md`).
- Candidate cannot explain *why* the request was hanging, only that
  wrapping something in try/catch made the test pass.
- Candidate adds a wrapper/try-catch to *every* route or restructures the
  whole app "to be safe" without being able to explain what problem each
  change solves, or introduces retries/timeouts/circuit-breaker logic that
  wasn't asked for and isn't implied by the bug report.
- Candidate never reads `warehouseNotifier.ts` or its direct unit tests,
  and instead assumes (without checking) that the notifier itself is what
  hangs.
- Candidate never reads `app.ts`/`errorHandler.ts` and instead assumes
  (without checking) that middleware ordering is the problem.
- Candidate's fix makes `createOrder` synchronous-looking by removing the
  `await` entirely (e.g., "fire and forget" the notification) rather than
  properly catching/forwarding its rejection — this silences the symptom
  differently but abandons notifying the warehouse reliably at all, which
  isn't what was asked.
