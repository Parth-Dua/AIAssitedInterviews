# Bug Design (private — do not expose to candidate)

## Expected behavior
`PATCH /users/{user_id}` is a *partial* update. Only fields explicitly
present in the request body may change the stored profile. A field the
caller omits from the request body must be left exactly as it was. A field
the caller explicitly sends as `null` (for a nullable field, e.g. `bio`) is
a legitimate instruction to clear that field.

## Actual (buggy) behavior
`app/services/profile_service.py::ProfileService.update_profile` computes
`update_data = request.model_dump()` — **without** `exclude_unset=True` —
and merges every key in `update_data` onto the stored profile via
`profile.model_copy(update=update_data)`. Because every field on
`ProfileUpdateRequest` defaults to `None`, any field the caller did not
include in the request body comes through `model_dump()` as `None` and
silently overwrites the corresponding stored value. `PATCH /users/1
{"timezone": "America/New_York"}` wipes `display_name`, `bio`, and
`email_notifications` back to `None` even though the caller only mentioned
`timezone`.

## Root cause
Conflating "field is `None`/unset" with "field was not provided." The
merge logic has no way to distinguish a request that omitted a field from
one that explicitly set it to `None` — both produce the same
`model_dump()` output. Pydantic v2 provides exactly this distinction via
`model_dump(exclude_unset=True)` (or, at the field level,
`"field" in request.model_fields_set`), which the code does not use.

## Violated invariant
"A PATCH request must only change the fields explicitly included in the
request body; omitted fields must be left untouched." (Stated in the
candidate README as the fix criterion; directly evidenced by the failing
public test.)

## Relevant execution path
`PATCH /users/{user_id}` (`app/api/routes/users.py`) →
`ProfileService.update_profile` (`app/services/profile_service.py`, where
the bug lives) → `ProfileRepository.get` / `.save`
(`app/repositories/profile_repository.py`, plain in-memory dict). The
candidate must also read `app/models/schemas.py` to notice that every
field on `ProfileUpdateRequest` is `Optional[...] = None` — that's what
makes "omitted" and "explicitly None" indistinguishable *unless* the
merge code asks Pydantic which fields were actually set.

## Evidence available to the candidate
- The failing public test `test_patch_only_timezone_preserves_other_fields`
  reproduces the exact reported scenario.
- The README states the bug report and the fix criterion explicitly.
- Reading `profile_service.py` end-to-end shows `request.model_dump()`
  feeding directly into `profile.model_copy(update=...)` with no filtering
  of unset fields.
- Reading `schemas.py` shows every `ProfileUpdateRequest` field defaults to
  `None`, which is the reason the naive merge can't tell "omitted" from
  "explicitly None."

## Reasonable hypotheses
1. (Correct) The merge uses `model_dump()` without `exclude_unset=True`
   (or equivalent), so omitted fields come through as `None` and overwrite
   real stored values.
2. (Plausible, wrong) The repository's `save()` is replacing the whole
   profile object incorrectly — ruled out by reading
   `profile_repository.py`: `save()` is a simple `dict[user_id] = profile`
   assignment; it stores whatever `UserProfile` it's handed, so the bug
   must be in what gets constructed *before* `save()` is called.
3. (Plausible, wrong) The route is not passing `request` through correctly,
   e.g. constructing a new `ProfileUpdateRequest` with defaults somewhere —
   ruled out by reading `api/routes/users.py`: the parsed `request` object
   is passed straight to `update_profile` unchanged.

## Intended regression test
`test_patch_only_timezone_preserves_other_fields` (already present as a
public test) plus hidden tests covering another single-field PATCH, an
empty-body PATCH, sequential accumulating PATCHes, and — most importantly
— an explicit-`null`-clears-the-field case (see `hidden_tests/`).

## Acceptable fixes
- Change `update_data = request.model_dump()` to
  `update_data = request.model_dump(exclude_unset=True)`.
- Equivalent: build the update dict manually from
  `request.model_fields_set` (e.g.
  `{f: getattr(request, f) for f in request.model_fields_set}`).
- Equivalent: iterate `request.model_dump(exclude_unset=True).items()` and
  `setattr` onto a mutable copy, or use `model_validate` with a merged
  dict built the same way. Any implementation that ends up applying only
  the fields present in `request.model_fields_set` (verbatim, including
  explicit `None`s) is acceptable.
- The response must still be the full, merged `UserProfile`.

## Tempting but incomplete/wrong fix
Switching to `request.model_dump(exclude_none=True)` instead of
`exclude_unset=True`. This *looks* like a fix and passes the originally
failing public test — omitted fields no longer overwrite stored values,
because `exclude_none` drops every field currently `None` from the dump,
which includes the omitted ones. But it also drops fields the caller
**explicitly** set to `null` to intentionally clear them (e.g. `PATCH
{"bio": null}` to clear a bio), because `exclude_none=True` cannot tell
"omitted" from "explicitly null" — it only looks at the final value, not
whether the caller set it. Under this fix, an explicit `null` for `bio`
silently no-ops instead of clearing the field.

This is caught by the hidden test
`test_patch_explicit_null_clears_nullable_field`, which sends
`{"bio": null}` and asserts the stored `bio` actually becomes `None`.
`exclude_none=True` fails this test (bio stays at its old value);
`exclude_unset=True` passes it (bio is explicitly in
`model_fields_set`, so it's included in the dump as `None` and applied).
Verified by actually running both variants against the full hidden test
suite (see validation notes in `EVALUATOR.md`).

## Why this is interview-appropriate
This is the textbook Pydantic `exclude_unset` vs. `exclude_none` vs. plain
`model_dump()` gotcha, applied to the extremely common "implement a PATCH
endpoint" task. It requires no specialist domain knowledge — it's fully
discoverable from the code, the failing test, and the README — but it is a
genuine, well-known correctness trap that trips up developers who haven't
internalized the difference between "not sent" and "sent as null."
Slightly harder than a pure business-logic variable-swap bug because the
correct fix and the tempting-but-wrong fix both look reasonable and both
pass the given failing test; only reading the schema carefully (and/or
writing the null-clearing case yourself) surfaces the difference.
