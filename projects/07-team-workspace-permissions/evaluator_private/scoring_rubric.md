# Scoring Rubric — Project 7 (100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the route → service → repository flow; noticed `permission_service.py` has `can_read_document`, `can_edit_document`, and `can_manage_document` as distinct checks, and that `membership_repository.py` exposes both a scoped (`get_membership`) and unscoped (`get_memberships_for_user`) lookup, before editing. |
| Debugging process | 10 | Reproduced the cross-workspace bug via the failing test (or equivalent manual repro: add a membership, hit `DELETE` as the mirrored user) before making changes; didn't shotgun-edit across files. |
| Root-cause reasoning | 15 | Correctly identifies that `can_manage_document` queries a user's memberships without scoping to the document's own workspace, and can articulate the general invariant violated ("authority over a resource must be scoped to that resource's tenant/workspace"). |
| Bug-fix correctness | 15 | Public and hidden cross-workspace tests pass in both directions (owner-in-A/editor-in-B and owner-in-B/editor-in-A); `can_edit_document` (PATCH) left alone/correct; fix uses (or is equivalent to) the already-correct `get_membership` scoped lookup rather than filtering the unscoped one inconsistently. |
| Feature/viewer-role implementation quality | 20 | `MembershipCreateRequest.role` extended to include `"viewer"`; invalid roles still rejected with `422`; both `can_edit_document` and `can_manage_document` explicitly deny viewers — checked *before* any personal-ownership shortcut, not merely relying on the role enum never producing a viewer-owned document; `GET` still works for viewers. |
| Tests added | 10 | Added at least one regression test beyond the given failing ones — ideally a second instance of the cross-workspace scenario in the opposite direction, and/or a viewer-denied-despite-ownership test, since those are the two ways a narrow fix slips through. |
| Scope discipline | 5 | Did not modify the response schema, unrelated endpoints, `can_read_document`, or the repository's data layout without justification; changes stayed within `permission_service.py` and `schemas.py` (plus tests). |
| Communication | 15 | Can clearly state: the cross-workspace bug's root cause and why the fix is correct; why the workspace-owner escape hatch had to be *scoped*, not removed, when fixing it; why the viewer check has to come before the ownership check, not after; what they checked to confirm both the fix and the feature work together. |

**Passing bar (strong intern/new-grad signal):** ≥75, all hidden tests
pass, and the candidate can explain both the cross-workspace root cause and
why removing the workspace-owner escape hatch entirely would be wrong,
without prompting.

**Red flags:**
- Fix passes the reported-bug test but fails
  `test_workspace_owner_can_delete_document_they_dont_personally_own_in_own_workspace`
  or the hidden `test_workspace_owner_can_delete_others_document_second_instance`
  (the "reduce `can_manage_document` to `owner_id == user_id`"
  overcorrection — see `bug_design.md`). Note this overcorrection actually
  fails *public* tests too, not only hidden ones — a candidate who ran
  `pytest -q` after this "fix" and didn't notice the new failures is a
  process red flag independent of the fix's own correctness.
- Candidate adds the `"viewer"` role to the `Literal` but never adds an
  explicit role check in `can_edit_document`/`can_manage_document` — passes
  the ordinary viewer test but fails
  `test_viewer_denied_even_if_they_are_the_documents_personal_owner`.
- Candidate "fixes" the bug by hardcoding the specific reported
  user/workspace pair (e.g. special-casing Alice or "marketing") instead of
  fixing the general scoping mechanism — verify with the hidden
  reverse-direction test.
- Candidate cannot explain *why* either the fix or the viewer-role design
  is correct, only that changing X made a test pass.
- Candidate rewrites large parts of the service or repository layer "to be
  safe."
