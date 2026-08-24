# Expected Reasoning Path

1. Run `npm test`; observe that `moves a task from "todo" to "in_progress"
   when status is updated` fails in both `tests/taskService.test.ts` and
   `tests/tasksApi.test.ts`, while everything else passes.
2. Read the failure output: the request/call succeeds (200 / no thrown
   error), but the returned `status` is still `'todo'` instead of
   `'in_progress'`.
3. Read the README's user complaint and confirm it matches: title/priority
   updates work, status updates silently no-op.
4. Trace the request path: `routes/tasks.ts` → `PATCH /tasks/:id` is wired
   only to `updateTask` in `controllers/taskController.ts`, with no
   validation middleware in between (unlike `POST`, which goes through
   `validateTaskCreate`). Read `validateTaskCreate.ts` briefly to confirm
   it only checks `title` and is not applied to the `PATCH` route — rules
   out "the middleware is stripping the field" as a hypothesis.
5. Read `taskController.ts::updateTask` — thin, passes `req.body` straight
   into `TaskService.updateTask`. Not the bug.
6. Open `services/taskService.ts::updateTask`. Notice the merge builds
   `title`, `priority`, and `assigneeId` with an update-if-present /
   fall-back-to-existing pattern, but `status` is hardcoded to
   `existing.status` — it never reads `updates.status` at all.
7. Confirm this is the root cause: it exactly explains why title/priority
   updates work but status updates don't, matching both the failing test
   and the user report.
8. Fix the `status` line to follow the same pattern as the other three
   fields: `status: updates.status ?? existing.status`.
9. Re-run tests. The two originally-failing tests should now pass. A
   careful candidate then asks: "what if `status` is set to something
   invalid now that it's actually respected?" — checks whether anything
   validates the value, finds nothing does for `PATCH` (unlike `POST`'s
   `validateTaskCreate`), and adds validation (in the service or a new
   middleware) that rejects an out-of-enum `status` with a 400/422 and
   leaves the stored task unchanged.
10. Explain: the merge logic for `status` simply didn't follow the pattern
    the other three fields already used, and fixing that alone re-opens a
    second gap (no enum validation on update) that a thorough fix should
    also close.

A strong candidate reaches step 8 within 15-20 minutes given the failing
tests and README as a starting point, and reaches step 9's realization
(closing the validation gap) within the full 45-60 minute timebox, ideally
without being told to — noticing it themselves is a strong signal.
