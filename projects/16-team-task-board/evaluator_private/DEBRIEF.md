# Interview Follow-Up Questions (private)

1. **What was the root cause?**
   Strong answer: `TaskService.updateTask` merges the update into the
   existing task field-by-field; `title`, `priority`, and `assigneeId` all
   fall back to the existing value when omitted, but `status` was
   hardcoded to `existing.status` regardless of what was requested — it
   never read `updates.status` at all.

2. **How did you narrow it down?**
   Strong answer: ran the failing tests first (both the unit test against
   `TaskService` and the supertest HTTP test), read the assertions
   (request succeeds, returned status is unchanged), then traced the
   request path from the route through the (absent, for PATCH) validation
   middleware, the controller, into the service, and read `updateTask`
   line by line looking for where each field is decided.

3. **Why does your fix solve it, and could it break anything else?**
   Strong answer: it restores the same "use the update if present, else
   keep the existing value" pattern already used for the other three
   fields, so `status` behaves consistently with them. It doesn't touch
   `title`/`priority`/`assigneeId` handling, the repository, or the
   `POST`/`GET` routes, so those are unaffected. They should mention they
   checked that an empty-body `PATCH` still no-ops, and that repeated
   `PATCH` calls still accumulate correctly.

4. **You mentioned the fix alone isn't quite complete — what else did you
   check or add?**
   Strong answer: once `status` is actually respected, nothing validates
   that the *value* is one of `'todo' | 'in_progress' | 'done'` — unlike
   `POST`, which has `validateTaskCreate` checking `title`. A `PATCH` with
   an arbitrary string would now silently corrupt the stored status. They
   added validation (service-layer check or a new middleware) that rejects
   an invalid value with 400/422 and leaves the task unchanged, and a test
   for it. A candidate who didn't think of this on their own but arrives
   at it when asked directly still shows reasonable signal; a candidate
   who found it unprompted is a stronger signal.

5. **Why didn't you add a rule preventing 'todo' from going directly to
   'done', skipping 'in_progress'?**
   Strong answer: nothing in the bug report, README, or code implies a
   linear workflow — the task's `status` type is a plain three-value union
   with no ordering, and the repository/service never encode transition
   rules elsewhere. Adding one would be inventing a requirement, not fixing
   the reported bug, and risks breaking legitimate use cases (e.g.,
   reopening a `'done'` task directly to `'todo'`, or fast-tracking a task
   straight to `'done'`). A candidate who *did* add such a rule should be
   asked to justify it — if they can't point to something in the repo or
   README that implies it, that's a scope-discipline flag.

6. **What tests would you add, and why?**
   Strong answer: an invalid-status-value test (catches the incomplete
   fix); a direct `'todo' → 'done'` transition test (guards against an
   over-eager fix adding transition rules); an empty-body `PATCH` test
   (guards against accidentally requiring at least one field, or
   accidentally clearing fields not present); a sequential multi-PATCH
   test (guards against the merge reading from a stale copy instead of the
   just-saved state).
