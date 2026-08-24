# Bug + Feature Design (private — do not expose to candidate)

This project bundles an authorization bug and a feature-implementation task
that share the same code path, so they're documented together.

## Seed data (for reference while reading the tests)

Users: Alice (id=1), Bob (id=2), Carol (id=3).

Memberships:
- marketing: Alice=owner, Bob=editor, Carol=editor
- engineering: Bob=owner, Alice=editor, Carol=editor

Documents:
- id=1, marketing, owner=Carol, "Q3 Campaign Brief"
- id=2, marketing, owner=Alice, "Marketing OKRs"
- id=3, marketing, owner=Bob, "Brand Guidelines"
- id=4, engineering, owner=Bob, "Deploy Runbook"
- id=5, engineering, owner=Carol, "Incident Postmortem Template"

Alice and Bob are each an `owner` in one workspace and only an `editor`
(non-owner) in the other — a deliberate mirror pair, so the cross-workspace
leak is reproducible in both directions. Carol is an `editor` in both
workspaces and never an `owner` anywhere, making her a clean baseline for
"a regular editor with no owner role at all."

## Part A — The cross-workspace authorization bug

### Expected behavior
A user's authority to manage (edit/delete) a document is determined solely
by: (a) personally owning the document, or (b) holding the `"owner"` role
*within that document's own workspace*. A role held in any other workspace
must confer no authority here.

### Actual (buggy) behavior
`app/services/permission_service.py::PermissionService.can_manage_document`
looks up the acting user's memberships with
`self._membership_repository.get_memberships_for_user(user_id)` — every
membership that user holds, across every workspace — and grants management
rights if *any* of them has role `"owner"`, regardless of which workspace
that membership is in:

```python
def can_manage_document(self, user_id: int, document: Document) -> bool:
    if document.owner_id == user_id:
        return True
    memberships = self._membership_repository.get_memberships_for_user(user_id)
    return any(m.role == "owner" for m in memberships)
```

A user who is `"owner"` in one workspace but merely an `"editor"` in another
therefore gets manage rights over documents in the *other* workspace too,
purely because they happen to be an owner somewhere.

### Root cause
Used-the-wrong-repository-method bug: `MembershipRepository` already exposes
`get_membership(user_id, workspace_id)` — a correctly workspace-scoped
lookup — right alongside the unscoped `get_memberships_for_user(user_id)`.
`can_manage_document` calls the unscoped one and then fails to filter the
result by `document.workspace_id`. The repository itself is correct and
unbugged; this is purely a "queried the wrong thing" mistake in the service
layer, discoverable by reading the repository's method list and comparing it
against what the service actually calls.

### Violated invariant
"A user's authority over a document is determined solely by their role
within THAT document's workspace (or personal ownership of the document
itself) — never by roles held in other workspaces." (Stated in the
candidate README's Constraints section and implied directly by the bug
report.)

### Relevant execution path
`DELETE /documents/{id}` (and, for the same reason, `PATCH` insofar as it
also calls into permission checks) — `app/api/routes/documents.py` — →
`DocumentService.delete_document` (`app/services/document_service.py`) →
`PermissionService.can_manage_document` (`app/services/permission_service.py`,
the bug) → `MembershipRepository` (`app/repositories/membership_repository.py`,
correct, has both the scoped and unscoped method already present). Note
that `PermissionService.can_edit_document` (which backs `PATCH`'s baseline
"any owner/editor member of the workspace may edit" behavior) is already
correctly scoped from the start — the bug is isolated to
`can_manage_document`, which backs `DELETE`.

### Evidence available to the candidate
- The public test `test_owner_role_in_other_workspace_cannot_delete_document_here`
  (API level) and its unit-level twin
  `test_owner_role_in_one_workspace_does_not_grant_manage_rights_in_another`
  reproduce the exact reported scenario with the seeded Alice/Bob mirror
  pair.
- The README states the invariant explicitly under Constraints.
- Reading `permission_service.py` end-to-end shows `can_read_document` and
  `can_edit_document` both call the scoped `get_membership(user_id,
  document.workspace_id)`, while `can_manage_document` alone calls the
  unscoped `get_memberships_for_user(user_id)` — an asymmetry visible just
  from reading the three methods side by side.
- Reading `membership_repository.py` shows `get_membership` already exists,
  is already correct, and is simply not the method `can_manage_document`
  happens to call.

### Reasonable hypotheses
1. (Correct) `can_manage_document` queries memberships without scoping to
   the document's own workspace.
2. (Plausible, wrong) Maybe the membership repository itself has
   stale/duplicate membership records (e.g. an old membership from before a
   role change wasn't removed). Ruled out by reading
   `MembershipRepository.add_membership`, which removes any existing
   membership for that `(user_id, workspace_id)` pair before appending the
   new one — there's no duplication, and printing/inspecting
   `get_memberships_for_user(user_id)` for the reported user shows exactly
   one membership per workspace, each with the expected role.
3. (Plausible, wrong) Maybe `can_edit_document` and `can_manage_document`
   are both broken and PATCH is silently succeeding too. Ruled out because
   the public test
   `test_owner_role_in_other_workspace_cannot_delete_document_here` and its
   sibling only assert on `DELETE`; a candidate who checks `PATCH` for the
   same user/document finds it behaves correctly (an editor may edit any
   document in their own workspace, which Alice legitimately is in
   Engineering) — the bug is isolated to the *manage* (delete-level) check,
   not the edit check.

### Intended regression tests
`test_owner_role_in_other_workspace_cannot_delete_document_here` (API,
public) and `test_owner_role_in_one_workspace_does_not_grant_manage_rights_in_another`
(unit, public) — already present. Plus the hidden
`test_owner_role_does_not_leak_into_other_workspace_reverse_direction`,
which exercises the same class of bug in the other direction (Bob is
engineering's owner but only marketing's editor) to catch a fix that
happens to special-case the specific public-test user/workspace pair
instead of fixing the general mechanism.

### Acceptable fixes
- Replace `get_memberships_for_user(user_id)` with
  `get_membership(user_id, document.workspace_id)` and check
  `membership is not None and membership.role == "owner"`.
- Equivalent: keep `get_memberships_for_user` but filter its result by
  `document.workspace_id` before checking role — functionally identical,
  just doesn't take advantage of the already-scoped repository method.
- Either fix must preserve: a document's personal owner can always manage
  it; a workspace `"owner"` member can manage any document *in that same
  workspace*; nothing else grants manage rights.

### Tempting but incomplete/wrong fix
Overcorrecting by ripping out the workspace-owner escape hatch entirely and
reducing `can_manage_document` to:

```python
def can_manage_document(self, user_id: int, document: Document) -> bool:
    return document.owner_id == user_id
```

This does stop the cross-workspace leak (the reported bug's scenario now
correctly returns `False`), but it also destroys the legitimate, intended
admin capability that a workspace `"owner"` can manage *any* document
within their *own* workspace, even ones a different member created. That
capability is exercised by two **public** tests
(`test_documents_api.py::test_workspace_owner_can_delete_document_they_dont_personally_own_in_own_workspace`
and its unit-level twin in `test_permission_service.py`) and by the
**hidden** `test_workspace_owner_can_delete_others_document_second_instance`
(same behavior, different workspace/user/document than the public
instance, to rule out a fix narrowly tailored to the exact public-test
data). It also happens to make a viewer who is coincidentally a document's
`owner_id` able to manage that document — caught by the hidden
`test_viewer_denied_even_if_they_are_the_documents_personal_owner`, since
`document.owner_id == user_id` alone no longer accounts for role at all.

**Validated:** applying this exact overcorrected `can_manage_document`
(with the viewer feature otherwise correctly implemented elsewhere) to a
temporary copy of the candidate repository, with the hidden tests copied
in, and running `pytest -q`, produced **4 failed, 14 passed** — the four
failures were exactly the two public workspace-owner tests and the two
hidden tests named above; every other public and hidden test passed. Note
this means the overcorrection is actually caught by the given *public*
test suite already, not only by the hidden tests — a candidate who runs
`pytest -q` after this "fix" and reads the output will see it regress. The
hidden tests exist as a second line of defense against a narrower fix that
special-cases only the exact public-test scenario (e.g. hardcoding
workspace/user IDs) rather than fixing the general mechanism.

## Part B — The viewer role feature

### Requested behavior
Workspace membership gains a third role, `"viewer"`. A viewer can `GET` a
document in their workspace but must receive `403` on `PATCH` and `DELETE`
of any document there, **regardless of any other condition** — including
the edge case where a viewer happens to be a document's `owner_id` (which
should never happen with valid data, but the authorization code must not
silently assume that invariant holds).

`POST /workspaces/{workspace_id}/members` must also validate `role`: only
`{"owner", "editor", "viewer"}` are acceptable; anything else must be
rejected with `422`.

### Starting (incomplete) state
`MembershipCreateRequest.role` is typed `Literal["owner", "editor"]` — role
validation already exists and already rejects garbage values like
`"superadmin"` with `422` (that part of the feature is already done and
shouldn't need touching), it just doesn't yet know about `"viewer"`.
`PermissionService.can_edit_document` and `can_manage_document` have no
concept of a viewer role at all yet — they only ever see memberships with
role `"owner"` or `"editor"`, since nothing can create a `"viewer"`
membership until the `Literal` is extended.

### Correct design
- Extend `MembershipCreateRequest.role` to
  `Literal["owner", "editor", "viewer"]`.
- In both `can_edit_document` and `can_manage_document`, check the caller's
  membership role for `"viewer"` **first**, before the personal-ownership
  check, and return `False` immediately if so. Checking personal ownership
  first (the natural-looking order, since it's already the first check in
  the starting `can_manage_document`) creates exactly the trap the hidden
  test `test_viewer_denied_even_if_they_are_the_documents_personal_owner`
  is designed to catch: if `document.owner_id == user_id` returns `True`
  before the role is consulted, a viewer who is (incorrectly, but
  possibly, via a data bug elsewhere) a document's owner would still be
  granted edit/delete rights.
- `can_read_document` doesn't need a change — a `"viewer"` membership
  already satisfies "any member of the workspace" for read access.

### Tempting but incomplete/wrong implementation
Adding `"viewer"` to the role `Literal` and stopping there, on the
assumption that since a viewer's role is neither `"owner"` nor `"editor"`,
the existing `membership.role in ("owner", "editor")` / `membership.role ==
"owner"` checks will naturally exclude them. This is **true** for the
ordinary case (a viewer who does not personally own the document) but
**false** the moment a viewer is checked against a document they happen to
personally own, because both starting methods check
`document.owner_id == user_id` *before* consulting the role at all — so
without an explicit, role-first viewer check, that early-return bypasses
the (already role-exclusive) later logic entirely. Caught by
`test_viewer_denied_even_if_they_are_the_documents_personal_owner`.

### Acceptable implementations
- The reference `PermissionService` above (explicit `role == "viewer"`
  check first in both `can_edit_document` and `can_manage_document`).
- Equivalent: a shared private helper (e.g. `_role_for(user_id, document)`)
  called at the top of both methods, as long as the viewer short-circuit
  happens before any ownership check.
- Not acceptable: relying solely on the `Literal` validation at the API
  boundary without any explicit role check in the authorization methods
  themselves — the service layer must not assume a viewer can never be a
  document's owner just because that shouldn't happen with valid data.

### Validation performed
The reference `PermissionService` and `schemas.py` (`reference_solution/`)
were applied to a temporary copy of the candidate repository, hidden tests
were copied into `tests/`, and `pytest -q` was run: **18 passed** (13
public + 5 hidden). Separately, the tempting-but-incomplete overcorrection
described in Part A (with the viewer feature otherwise correctly
implemented) was applied the same way: **4 failed, 14 passed** — see Part
A for exactly which tests failed. The original, untouched candidate
starting state was re-verified afterward: **3 failed, 10 passed**
(`test_documents_api.py::test_owner_role_in_other_workspace_cannot_delete_document_here`,
`test_permission_service.py::test_owner_role_in_one_workspace_does_not_grant_manage_rights_in_another`,
and `test_membership_api.py::test_add_viewer_member`), confirming the
intended pass/fail split.

## Why this is interview-appropriate
Multi-tenant / multi-workspace authorization scoping bugs — checking "does
this user have role X" without scoping the check to the specific resource's
tenant — are one of the most common and highest-signal real-world backend
bug classes (the same shape shows up as "any org admin can act on any other
org's data" in real SaaS incidents). Pairing it with "now add a read-only
role" is exactly the kind of natural follow-up a real team would ask for
once the root cause is understood, and it forces the candidate to
generalize their fix correctly rather than just patching the one reported
path. No specialist knowledge required — the repository layer is a five-
method, pure-Python, in-memory class, and the fix is fully discoverable
from reading `permission_service.py` next to `membership_repository.py`.
