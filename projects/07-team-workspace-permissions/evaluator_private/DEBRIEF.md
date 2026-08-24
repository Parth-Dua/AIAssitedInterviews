# Interview Follow-Up Questions (private)

1. **What was the root cause of the reported bug?**
   Strong answer: `can_manage_document` looked up a user's memberships
   across *all* workspaces and granted management rights if any of them
   had role `"owner"`, instead of checking only the membership in the
   specific document's workspace. The repository already had the correctly
   scoped lookup available; the service just called the wrong one.

2. **Why is checking a role without scoping it to the resource's
   tenant/workspace a dangerous pattern in general, beyond this specific
   case?**
   Strong answer: any time authority is derived from "does this user have
   role X anywhere," instead of "does this user have role X *for this
   specific resource's owner/tenant*," a user with elevated privilege in
   one tenant silently gains that privilege everywhere — a classic
   multi-tenant privilege-escalation shape. It's dangerous specifically
   because it's easy to write and easy to have it pass casual testing (a
   test that only checks a user acting within their own workspace won't
   catch it at all), and it tends to get worse over time as more roles and
   more workspaces are added.

3. **Your first fix attempt could have been to make `can_manage_document`
   just check `document.owner_id == user_id`. Why is that wrong, and how
   did you catch it (or would you catch it) if you'd gone down that path?**
   Strong answer: it breaks the legitimate capability that a workspace
   `"owner"` can manage any document in their own workspace, not just
   documents they personally created — that's the whole point of having an
   owner role. Catching it means actually running the full test suite
   (including tests unrelated to the specific bug report) after making a
   change, not just the one failing test you started from.

4. **How did you design the viewer role, and why did check ordering
   matter?**
   Strong answer: extended the role validation to accept `"viewer"`, then
   added an explicit "if the caller's role is viewer, deny" check to both
   the edit and manage authorization methods — placed *before* the
   personal-ownership check, not after, because both methods short-circuit
   to `True` as soon as `document.owner_id == user_id` is true. If the
   viewer check came after that line, a viewer who happened to be a
   document's owner (which shouldn't happen with valid data, but isn't
   structurally prevented) would still get write access.

5. **What tests would you add to guard against this class of bug
   recurring elsewhere in the codebase?**
   Strong answer: a general pattern — for every function that grants
   authority based on a role, a test with a user who holds the relevant
   role in a *different* resource's tenant/workspace than the one being
   acted on, asserting they're denied. Also worth naming: property-style
   or parametrized tests that sweep over "acting user × target document"
   combinations rather than one-off scenarios, since scoping bugs are
   often invisible until you specifically construct a mismatched pair.

6. **How would you extend this permission model if a workspace needed
   custom roles beyond owner/editor/viewer?**
   Strong answer (design-forward-thinking): stop hardcoding role names as
   string literals compared with `==`/`in` throughout the service, and
   instead model a role as a set of capabilities (e.g. `can_read`,
   `can_edit`, `can_delete_own`, `can_delete_any`) that a role maps to,
   looked up once per check. That way adding a new custom role is a data
   change (define its capability set) rather than a code change scattered
   across every authorization method — and it removes the exact kind of
   ad hoc string-matching bug this exercise was built around.
