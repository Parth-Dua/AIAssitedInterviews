# Interview Follow-Up Questions (private)

1. **What was the root cause?**
   Strong answer: the update merge computed `request.model_dump()` without
   `exclude_unset=True`, so every field the caller omitted came through as
   `None` (its schema default) and silently overwrote the stored value —
   the code had no way to distinguish "not provided" from "provided as
   `None`."

2. **How did you narrow it down?**
   Strong answer: ran the failing test first, read the assertion (only
   `timezone` was correct; every other field reverted), then read
   `profile_service.py` looking specifically at how the request body gets
   merged into the stored profile, and `schemas.py` to see that every
   request field defaults to `None`.

3. **Why `exclude_unset=True` and not `exclude_none=True`? What's the
   difference, concretely?**
   Strong answer: `exclude_unset=True` drops only fields the caller never
   included in the request payload at all (checked against
   `model_fields_set`), while keeping any field the caller explicitly set —
   even to `null`. `exclude_none=True` drops every field whose *current
   value* is `None`, regardless of whether the caller sent it explicitly or
   omitted it — so it can't tell "omitted" from "explicitly cleared," and
   would silently ignore a caller's intentional `{"bio": null}` request to
   clear their bio. Should be able to say this without prompting, or after
   being shown the null-clearing test failure.

4. **Why does your fix solve it, and could it break anything else?**
   Strong answer: it restores "PATCH only touches fields the caller
   included" without changing response shape, without touching
   `GET /users/{user_id}`, and without breaking the case where a caller
   sends a full body (all fields present — behavior identical either way).
   Should mention they checked an empty-body PATCH is a no-op and that
   sequential single-field PATCHes accumulate correctly.

5. **What tests would you add, and why?**
   Strong answer: a single-field PATCH for a field other than the one in
   the given test (e.g. `email_notifications` only); an empty-body PATCH
   that changes nothing; sequential PATCHes that each set one field and
   confirm none of them clobber the others; and — the most important one —
   an explicit `{"bio": null}` PATCH that asserts the stored `bio` actually
   becomes `None`, since that's exactly the case a plausible-looking but
   wrong fix (`exclude_none=True`) fails.

6. **How would you extend this to support explicitly un-setting a field
   back to a true default vs. leaving it alone?** (design-forward)
   Strong answer (design-forward-thinking): the current design already
   supports this correctly for nullable fields (`bio`) via explicit `null`
   in the request — that's the whole point of `exclude_unset`. For a
   non-nullable field where "reset to default" is a distinct concept from
   "not a valid value" (e.g. resetting `timezone` back to the account's
   default timezone rather than leaving it null), a reasonable extension is
   a small sentinel value or a separate `reset_fields: list[str]` parameter
   in the request, rather than overloading `null` to mean two different
   things for a field that can't legitimately be null. Bonus points for
   noting this is exactly the kind of ambiguity that motivated tools like
   `Unset`/sentinel objects in some API designs, rather than relying purely
   on `None`.
