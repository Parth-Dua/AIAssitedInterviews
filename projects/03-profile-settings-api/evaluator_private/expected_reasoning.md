# Expected Reasoning Path

1. Run `pytest -q`; observe `test_patch_only_timezone_preserves_other_fields`
   fails while everything else passes.
2. Read the assertion: after `PATCH {"timezone": "America/New_York"}`,
   `timezone` is correct but `display_name`, `bio`, and `email_notifications`
   have all reverted to `None`/falsy values instead of their seeded values.
3. Open `app/api/routes/users.py`; confirm the parsed `ProfileUpdateRequest`
   is passed straight into `ProfileService.update_profile` with nothing
   filtered out at the route layer.
4. Open `app/models/schemas.py`; notice `ProfileUpdateRequest` declares
   every field `Optional[...] = None`. This is necessary for a PATCH
   schema, but it means "the caller didn't send this field" and "the caller
   sent this field as null" both end up looking identical *after*
   `model_dump()` unless something asks Pydantic which fields were actually
   set on the instance.
5. Open `app/services/profile_service.py`; find
   `update_data = request.model_dump()` feeding directly into
   `profile.model_copy(update=update_data)`. Recognize that plain
   `model_dump()` includes every field at its current value — `None` for
   anything omitted — so the merge is unconditionally overwriting every
   field the caller didn't mention.
6. Consider the fix: use `request.model_dump(exclude_unset=True)` (or
   `request.model_fields_set`) so only fields the caller actually included
   are merged in.
7. Before finalizing, notice `bio` is `Optional[str]` on the *stored*
   `UserProfile` too — i.e., a caller might legitimately want to send
   `{"bio": null}` to clear it. Check that the fix still applies an
   explicit `null` (as opposed to silently dropping it, which is what
   `exclude_none=True` would do). A careful candidate either reasons this
   through from the Pydantic docs/knowledge of `exclude_unset` vs.
   `exclude_none`, or discovers it by writing a test for explicit-null
   clearing and noticing `exclude_none` breaks it.
8. Re-run tests; all public tests pass. Manually reason through a couple
   more cases (empty-body PATCH does nothing; two sequential single-field
   PATCHes both stick) or add tests for them.
9. Explain: the merge logic didn't distinguish "not provided" from "0/None
   value," and `exclude_unset=True` (not `exclude_none=True`) is the
   correct fix because it preserves the ability to explicitly clear a
   nullable field.

A strong candidate reaches step 6 within 15-20 minutes given the failing
test as a starting point, and reaches step 7 (the exclude_unset vs.
exclude_none distinction) either on their own or after writing/considering
a null-clearing test case.
