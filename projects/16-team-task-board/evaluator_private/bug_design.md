# Bug Design (private — do not expose to candidate)

## Expected behavior
`PATCH /tasks/:id` performs a partial update: every field present in the
request body (`title`, `status`, `priority`, `assigneeId`) is applied to the
stored task; any field omitted from the body is left unchanged. Invariant:
"a PATCH request updates exactly the fields included in the request body;
every one of title/status/priority/assigneeId must be independently
updatable."

## Actual (buggy) behavior
`TaskService.updateTask` (`src/services/taskService.ts`) builds the merged
task object field-by-field. `title`, `priority`, and `assigneeId` correctly
fall back to the existing value with `??` / an explicit `!== undefined`
check when omitted from `updates`. `status`, however, is hardcoded to
`existing.status` unconditionally — `updates.status` is never read. A
`PATCH` that includes a `status` change succeeds (200, the merged task is
returned and saved) but the returned/stored `status` is always whatever it
already was.

## Root cause
Field omission in the merge: the `status` line in the object literal reads
`status: existing.status` instead of `status: updates.status ??
existing.status`. Every other field in the same object literal follows the
"use the update if present, else fall back" pattern; `status` alone breaks
that pattern. The bug is isolated to a single field on a single line — the
merge mechanism itself is correct (proven by title/priority/assigneeId all
updating fine), which is deliberate: it should let a candidate quickly rule
out "the merge/PATCH plumbing is broken in general" and focus on why this
one field is different.

## Violated invariant
"A PATCH request updates exactly the fields included in the request body;
every one of title/status/priority/assigneeId must be independently
updatable." (Stated in the candidate README as the reported user complaint;
implied by the general semantics of a partial-update endpoint.)

## Relevant execution path
`PATCH /tasks/:id` (`src/routes/tasks.ts`) → `updateTask` controller
(`src/controllers/taskController.ts`, thin — passes `req.body` straight
through to the service and maps `TaskNotFoundError` to 404) →
`TaskService.updateTask` (`src/services/taskService.ts`, **the bug**) →
`TaskRepository.getById` / `.save` (`src/repositories/taskRepository.ts`,
a plain `Map`-backed store — correct, no aliasing issue). The candidate
must also read `src/middleware/validateTaskCreate.ts` to confirm it is only
wired to the `POST` route (see `routes/tasks.ts`) and therefore cannot be
the thing stripping `status` from the `PATCH` request body.

## Evidence available to the candidate
- The failing public test `moves a task from "todo" to "in_progress" when
  status is updated` (in both `tests/taskService.test.ts` and
  `tests/tasksApi.test.ts`) reproduces the exact reported scenario.
- The README states the user complaint verbatim: title/priority updates
  work, status updates silently no-op.
- Reading `taskService.ts::updateTask` end-to-end reveals four fields
  merged with the same intended pattern, one of which — `status` — doesn't
  follow it.

## Reasonable hypotheses
1. (Correct) `updateTask`'s merge hardcodes `status` to the existing value
   instead of respecting `updates.status`.
2. (Plausible, wrong) The validation middleware is stripping `status` out
   of the request body before it reaches the controller — ruled out by
   reading `middleware/validateTaskCreate.ts`, which only checks for a
   `title` on `POST` and is never applied to the `PATCH` route at all (see
   `routes/tasks.ts`); nothing removes fields from `req.body`.
3. (Plausible, wrong) The repository is returning a stale/cached copy of
   the task on the next `GET` instead of the just-saved one — ruled out
   because `PATCH` itself returns the (already wrong) status in its own
   200 response body, before any subsequent `GET` is even involved; the
   repository's `save`/`getById` is a straightforward `Map` set/get with no
   caching or cloning layer to go stale.
4. (Plausible, wrong) `TaskUpdateInput`/Express body parsing is silently
   dropping the `status` key — ruled out because `title` and `priority`
   arrive through the exact same `req.body ?? {}` path and update fine in
   the same request shape.

## Intended regression tests
The two already-failing public tests (one at the service layer, one at the
HTTP layer) plus the hidden tests in `hidden_tests/taskHidden.test.ts`
covering the invalid-status-value gap, the (permitted) non-linear
transition, the empty-body no-op, and accumulation across sequential
`PATCH` calls.

## Acceptable fixes
- Change the `status` line in the merge to
  `status: updates.status ?? existing.status` (mirrors the pattern already
  used for `title`/`priority`).
- Equivalent phrasings: an explicit `updates.status !== undefined ?
  updates.status : existing.status` check, or restructuring the merge as
  `{ ...existing, ...updates }` followed by re-validating/re-typing the
  result (acceptable as long as it doesn't silently accept invalid enum
  values — see below).
- A *complete* fix must also close the validation gap: `PATCH /tasks/:id`
  with an out-of-enum `status` value must be rejected (400/422) and must
  not mutate the stored task. This can live in the service (validate
  `updates.status` against the three valid statuses before merging, throw
  a typed error, have the controller map it to 400) or in a new middleware
  mirroring `validateTaskCreate`'s pattern wired to the `PATCH` route —
  either is acceptable; see `reference_solution/` for one valid version
  (service-layer validation).
- The fix must **not** add status-transition rules (e.g. forbidding
  `todo → done` directly) — the system does not enforce a linear workflow,
  and `hidden_tests/taskHidden.test.ts` explicitly checks that a direct
  `todo → done` transition is still allowed after the fix.

## Tempting but incomplete/wrong fix
Removing the hardcode — changing `status: existing.status` to
`status: updates.status ?? existing.status` — and stopping there. This
makes the reported bug's test pass (status updates now take effect) but
does nothing to validate the *value* of `updates.status`. Since there is no
`validateTaskUpdate`-equivalent middleware wired to the `PATCH` route in the
starting code (only `validateTaskCreate`, applied solely to `POST`), a
`PATCH /tasks/:id` with `{"status": "bogus-value"}` now succeeds with a 200
and corrupts the task's stored status to a value outside the
`'todo' | 'in_progress' | 'done'` enum. `hidden_tests/taskHidden.test.ts`'s
"rejects an invalid status value and leaves the stored status unchanged"
test catches exactly this: it fails against the naive fix (gets a 200
instead of a 400/422, and/or finds the corrupted value persisted) and
passes against a fix that also validates the enum on update. See
`evaluator_private/reference_solution/` for the one-line naive fix isolated
from the complete one, and the project's validation log for the exact
observed failure (15/16 hidden+public tests pass under the naive fix; only
the invalid-status test fails).

## Why this is interview-appropriate for an Amazon-style OA
A realistic "read an unfamiliar Express/TypeScript repo across
route → middleware → controller → service → repository, a user reported a
partial-update bug, find and fix it" shape — the multi-file reasoning chain
(and the need to rule out the middleware as a red herring) is exactly what
Amazon-style repo-based debugging OAs test: can the candidate trace a
request through several thin layers to find where a stated business
invariant is actually violated, rather than pattern-matching on the first
file they open. The tempting-but-incomplete fix additionally rewards
candidates who think about *what else could go wrong* once they've made the
literal bug report reproduce correctly, rather than stopping at the first
green test run — a common differentiator in OA rubrics for this format.
