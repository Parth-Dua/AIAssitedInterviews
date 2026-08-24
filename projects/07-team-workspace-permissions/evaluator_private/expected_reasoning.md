# Expected Reasoning Path

## Part A — the bug

1. Run `pytest -q`; observe
   `test_owner_role_in_other_workspace_cannot_delete_document_here` and
   `test_owner_role_in_one_workspace_does_not_grant_manage_rights_in_another`
   fail while most other tests pass (plus one unrelated viewer-role
   failure, see Part B).
2. Read the failing assertions: Alice (owner in marketing, editor in
   engineering) is able to `DELETE` a document in engineering she doesn't
   own, when she should get `403`.
3. Trace the call path: `DELETE /documents/{id}` →
   `DocumentService.delete_document` →
   `PermissionService.can_manage_document`.
4. Read `can_manage_document` and notice it calls
   `get_memberships_for_user(user_id)` — every membership that user has,
   with no workspace filter — then checks `any(role == "owner")` across
   all of them.
5. Open `membership_repository.py` and notice `get_membership(user_id,
   workspace_id)` already exists, is already scoped correctly, and is
   already used by `can_read_document` and `can_edit_document` right next
   to `can_manage_document` — the asymmetry is visible just from reading
   the three methods together.
6. Fix `can_manage_document` to use the scoped `get_membership` lookup
   instead, checking the role of the membership *in the document's own
   workspace* only.
7. Re-run the reported-bug test and its unit-level twin; both pass.
   Manually reason through (or add a test for) the mirror case — Bob is
   owner in engineering, editor in marketing — to confirm the fix isn't
   accidentally directional.
8. Re-run the *existing* public test that exercises the intended
   admin capability (`test_workspace_owner_can_delete_document_they_dont_personally_own_in_own_workspace`)
   to make sure the fix didn't accidentally remove the workspace-owner
   escape hatch entirely — a strong candidate checks this proactively,
   since it's the natural thing to break while "fixing" this.

A strong candidate reaches step 6 within 15-25 minutes given the failing
tests as a starting point, having read `permission_service.py` and
`membership_repository.py` side by side.

## Part B — the viewer role

1. Read the feature request and the currently-failing
   `test_add_viewer_member` test: adding a member with `role="viewer"`
   currently returns `422`.
2. Find `MembershipCreateRequest` in `schemas.py`; notice `role:
   Literal["owner", "editor"]` — extend it to include `"viewer"`.
3. Re-run tests; `test_add_viewer_member` now passes, but nothing yet
   stops a viewer from editing or deleting, since `can_edit_document` and
   `can_manage_document` were written assuming only `"owner"`/`"editor"`
   memberships exist.
4. Add an explicit viewer-denial check to both methods. The subtle part:
   both methods currently check `document.owner_id == user_id` *first* and
   return `True` immediately if so — a candidate who appends a viewer
   check *after* that line, rather than before it, has written code that
   passes the ordinary "viewer tries to edit a document they don't own"
   test but would still let a viewer manage a document if
   `document.owner_id` ever equalled their `user_id`. A careful candidate
   either reorders the check (viewer check first) or explicitly reasons
   through why order matters here and states it.
5. Confirm `GET` is untouched — `can_read_document` doesn't special-case
   role at all, so a viewer's read access "just works" once their
   membership exists.
6. Re-run the full suite; confirm all public tests pass and add or run the
   viewer-ownership-edge-case scenario mentally or as a test.

A strong candidate reaches a complete viewer implementation within
15-20 minutes of starting Part B, having noticed the check-ordering trap
without being told about it explicitly.
