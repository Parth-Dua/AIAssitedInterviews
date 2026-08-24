# Bug Design (private — do not expose to candidate)

## Expected behavior

`PUT /notes/:id` performs a full edit of a note (title, content, tags),
submitted by a client whose edit form loaded a snapshot of the note at some
point in time, including the version that snapshot was loaded at. Invariant:
"a note update must only succeed if the client's view of the note (its
`version`) is still current; if the note has changed since the client loaded
it, the write must be rejected, not silently applied over the newer state."

## Actual (buggy) behavior

`NoteService.updateNote` (`src/services/noteService.ts`) builds the updated
note directly from the client's payload — `title`, `content`, and `tags` are
all taken verbatim from `payload`, and `version` is simply
`existing.version + 1`. `payload.version` (the version the client's edit
form was loaded with) is accepted by the endpoint and even required by
input validation, but it is never compared against `existing.version`
anywhere. A `PUT` succeeds (200, the note is saved with the client's fields)
regardless of whether the note has changed since the client's edit form
loaded it. Any intervening write — most concretely, a tag added via
`POST /notes/:id/tags` while the edit form was still open — is silently
discarded the moment that stale edit form is saved.

## Root cause

A missing optimistic-concurrency check on the one endpoint whose contract
actually depends on one: `POST /notes/:id/tags` is a small, additive,
version-bumping write that never needed to know about staleness (it always
operates on whatever the current state is). `PUT /notes/:id`, by contrast,
replaces the note's authorable fields wholesale from a client-held snapshot
— that's exactly the shape of operation where "is the snapshot still
current?" matters, and it's the one place that check doesn't exist. The
merge logic itself is not "broken" in the sense of doing arithmetic wrong;
it faithfully applies whatever the client sent. The bug is an omission, not
a miscalculation — deliberately, so it reads as plausible, unremarkable
code rather than an obviously broken line.

## Violated invariant

"A user may only have a full-edit save succeed if the note has not changed
since their edit form loaded it; any write that happened in the meantime
must cause the stale save to be rejected, never silently overwritten."

## Relevant execution path

`PUT /notes/:id` (`src/routes/notes.ts`) → `updateNote` controller
(`src/controllers/noteController.ts`, thin input-shape validation, passes
the payload straight through to the service) → `NoteService.updateNote`
(`src/services/noteService.ts`, **the bug** — no version comparison) →
`NoteRepository.getById`/`.save` (`src/repositories/noteRepository.ts`, a
plain `Map`-backed store — correct, no aliasing or caching issue). The
candidate should also read `NoteService.addTag` (correct, given) to confirm
that endpoint's own write is sound and durable, which is what makes the
"the tag write itself might be broken" hypothesis rule-out-able by direct
observation (see below).

## Evidence available to the candidate through the app

- Opening a note's edit view, quick-adding a tag to that same note from the
  list without saving the edit form, then saving the edit form: the
  quick-added tag disappears from the note afterward, with no error shown
  anywhere in the UI (the frontend's save handler doesn't check the
  response status at all in the starting code, so a rejected save — once
  the candidate's own fix produces one — would need frontend attention
  too).
- A `GET /notes/:id` taken immediately after the quick-add-tag call (before
  any stale save happens) shows the tag present and the note's version
  incremented — this is the evidence that rules out hypothesis 1 below.
- Re-fetching a note at any point always reflects the true current
  in-memory state — there is no caching layer anywhere in this app, which
  rules out hypothesis 2 below.
- The `PUT` endpoint's own request/response shape (it accepts and requires
  a `version` field, and the note's `GET`/list responses always include the
  note's current `version`) is a strong hint, once noticed, that `version`
  is meant to mean something to this endpoint specifically.

## Reasonable hypotheses

1. (Wrong) "Maybe `POST /notes/:id/tags` doesn't actually persist the tag
   correctly — the write itself is unreliable." Ruled out: a `GET
   /notes/:id` immediately after the quick-add-tag call shows the tag
   present and the version incremented. The write itself is correct and
   durable; the tag is only lost later, by a *different* operation.
2. (Wrong) "Maybe there's a caching layer somewhere serving stale reads."
   Ruled out: there is no cache anywhere in this app —
   `NoteRepository.getById` always reads live in-memory state directly;
   re-reading `GET /notes/:id` at any point always reflects the true
   current state. The staleness is entirely in the *client's* own captured
   snapshot (from when its edit form was opened), not in anything the
   server serves on read.
3. (Correct) `PUT /notes/:id`, via `NoteService.updateNote`, blindly
   overwrites the note using the client's snapshot for *all* fields —
   title, content, and tags alike — without ever checking whether that
   snapshot (identified by `payload.version`) is still the note's current
   version.

## Intended regression tests

Public tests (`candidate/tests/`) cover ordinary CRUD — creating, listing,
fetching, quick-adding a tag, and a full edit that succeeds when given the
current version — and pass unmodified on the buggy starting code (verified;
see validation log at the end of this file). They do not encode the bug.
Hidden tests (`evaluator_private/hidden_tests/notesHidden.test.ts`) cover:
the tag-loss-via-stale-edit-save reproduction (the core discovered bug); the
lost-content-update-between-two-sessions scenario (second symptom, same
root cause — and specifically the case that distinguishes a complete fix
from the tags-merge-only tempting fix, since it never touches tags at all);
a sanity check that a `PUT` with the current version still succeeds
normally after a fix (the fix must not make every edit fail); a
nonexistent-note `PUT` still returning 404 rather than a version-conflict
status; and a quick-add-tag call that races ahead of a rejected stale `PUT`
still leaving both tags intact end-to-end afterward.

## Acceptable fixes

- `NoteService.updateNote` (service layer) must compare `payload.version`
  to `existing.version`; if they differ, throw a `VersionConflictError` (or
  similarly named error) *without* applying any part of the write — no
  field is updated, no version is bumped, nothing is saved.
- The controller (`noteController.ts`) must map that error to a `409`
  response with a clear error body (not `200`, not `400` — `409 Conflict`
  is the semantically correct status for "the resource changed under you").
- A small, mechanical frontend change is acceptable and expected: the edit
  form already sends the loaded `version` in its `PUT` body (that part of
  the contract predates the fix), but the starting `public/app.js`'s save
  handler never inspects the response status — it treats every response as
  a success. Once the backend starts returning `409`s, the frontend should
  check for that and show a message like "this note changed since you
  opened it — reload to see the latest version" instead of silently
  claiming success. See `reference_solution/app.js` for the minimal patch.
  This frontend change is bookkeeping, not the substantive fix — the actual
  engineering decision (detecting and rejecting stale writes) is entirely
  backend-side.
- Equivalent phrasings: an explicit `if (payload.version !== existing.version)`
  check inline in the service (the reference solution's approach), or the
  same check expressed as a small private helper — acceptable as long as
  *no* field of the note is mutated when the versions don't match.

## Tempting but incomplete/wrong fix

A candidate who reproduces *only* the tag-loss symptom (the more visually
obvious one, since it's directly reachable through the quick-add-tag UI
control) is likely to "fix" it by making `updateNote` merge `tags`
additively — union of `payload.tags` and `existing.tags` — instead of
overwriting, while leaving `title` and `content` blindly overwritten exactly
as before, and adding no version check at all. This resolves the tag-loss
symptom specifically (a quick-added tag is never removed by a tags-merge,
so it always survives a subsequent stale save) but does **not** address the
general invariant: a stale *content* save still silently clobbers a newer
content change with zero protection, and nobody involved gets any error —
the second saver's request still returns `200`, unaware it just discarded
someone else's change.

`hidden_tests/notesHidden.test.ts`'s "lost update between two sequential
sessions" test catches exactly this: two sessions `GET` the same note at the
same version, each independently `PUT`s a different `content` change using
that captured version, and the second `PUT` must be rejected with `409`,
leaving the first session's content change intact. This test never touches
`tags` at all, so a tags-merge-only patch cannot pass it by accident — it
still returns `200` and silently overwrites, which is exactly the failure
mode being tested for. Verified in the validation log below: the
tags-merge-only patch passes all 21 public tests and 2 of 5 hidden tests
(the current-version sanity check and the 404-not-409 check, both of which
don't depend on the version check existing at all) but fails the other 3 —
the stale-tag-loss test, the lost-content-update test, and the racing
quick-add test — all for the same reason: `200` where `409` was expected,
because no version comparison exists anywhere in that patch.

## Why this is interview-appropriate, and why calibrated above standard OA
difficulty on purpose

Most repo-debugging OAs hand the candidate a failing test or an exact bug
report and ask them to trace it to a root cause and fix it — valuable, but
it skips the step every real on-call or bug-report investigation actually
starts with: noticing, through use, that something is wrong at all, then
turning a vague "this feels off" into a deterministic, minimal reproduction
before any code-reading begins. This project (the first of a two-project
"black-box full-app debugging" tier) is deliberately harder than the
Node-track debugging projects that precede it (16-19, all ~6/10) because it
tests that upstream skill explicitly: the candidate must drive a real
running application (via its UI or by replaying the same HTTP calls the UI
makes), notice a discrepancy between what they did and what they see, and
only then start the familiar trace-to-root-cause work. The reproduction
sequence itself is fully deterministic and single-session/single-user (no
real concurrency, no multi-tab timing games, no luck involved) — open an
edit view, quick-add a tag to the same note from the list, save the edit
view — which keeps the difficulty in the discovery-and-reasoning dimension
rather than in flaky or hard-to-trigger timing. The two-symptom structure
(tag loss being the obvious, UI-discoverable one; the lost content update
being the deeper, same-root-cause one that a thorough candidate finds by
generalizing rather than stopping at the first fix that makes the obvious
symptom go away) mirrors a very common real differentiator in bug-bash and
on-call scenarios: an incomplete fix that resolves the reported symptom
while leaving the actual invariant violated.

## Validation log

- `npm install && npm test` against the unmodified `candidate/` starting
  code: **21/21 public tests pass** (2 suites).
- Manual `curl` reproduction of both symptoms against a real running
  `npm run dev` server: confirmed. Symptom 1 (quick-added tag lost after a
  stale full-edit save) and symptom 2 (second of two same-version sessions'
  content changes silently overwrites the first, with no error to either
  caller) both reproduced exactly as designed.
- Reference fix (`reference_solution/noteService.ts` +
  `reference_solution/noteController.ts`) copied over the buggy files in an
  isolated scratch copy, hidden tests copied in: **26/26 tests pass** (21
  public + 5 hidden). Re-ran the manual `curl` reproduction against this
  fixed server: the stale save now returns `409` and the quick-added tag
  survives.
- Tags-merge-only tempting fix applied in the same scratch copy (in place
  of the reference fix, no version check at all): **21/26 pass, 5 fail.**
  Of the 21 public tests, 19 pass and 2 fail — both are the "updates fields
  and increments version when given the current version" test (one at the
  service-unit layer, one at the HTTP layer); both fail under this patch
  because tag *merging* changes their expected exact-tags-equality
  assertion when editing a note that already carries pre-existing tags —
  an incidental side effect of the patch's own behavior on a public test,
  not something the hidden-test design relies on for its signal. Of the 5
  hidden tests, exactly 2 pass (current-version sanity, 404-not-409 check)
  and 3 fail — the stale-tag-loss test, the lost-content-update test, and
  the racing-quick-add test — all failing with `200` where `409` was
  expected, precisely as designed: the lost-content-update test in
  particular is the one that specifically distinguishes this incomplete
  fix from a correct one, since it never touches `tags` at all.
- `candidate/` restored to its original, untouched buggy state throughout
  (all editing happened in an isolated scratch copy); re-verified `npm
  test` → 21/21 pass and the `curl` reproduction still shows the bug after
  restoration.
