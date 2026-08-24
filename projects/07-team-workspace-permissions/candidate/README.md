# Team Workspace Permissions — Authorization Bug + Viewer Role (Interview Exercise)

**Format:** Debugging + Feature Implementation
**Timebox:** 60–75 minutes
**Level:** SWE Intern / New Grad / Backend
**Difficulty:** 7/10

## Scenario

You've just joined the internal tools team building a lightweight team
workspace product (think a small internal Notion/Confluence). Teams get
their own workspace; each workspace has its own members and documents. A
user's authority is entirely determined by their role in a given
workspace — a user can be an `owner` in one workspace and merely an
`editor` in another, and those are independent facts. It's a small internal
service — you haven't seen this code before today.

A security-conscious teammate has escalated a permissions bug, and product
has a follow-up feature request.

### 1. A bug report

> "A user reported that a coworker who is a workspace owner in the
> 'Marketing' workspace was somehow able to delete a document in the
> completely separate 'Engineering' workspace, even though that coworker
> is only a regular editor (not an owner) in Engineering. This shouldn't
> be possible — workspace roles are supposed to be workspace-specific."

### 2. A feature request

> "Can we add a read-only 'viewer' role? We have people who need to see
> documents in a workspace — for context, for review — without being able
> to change anything. Right now everyone we add to a workspace can edit."

## Your task

1. Reproduce the reported bug, find its root cause, and fix it.
2. Add a `"viewer"` workspace role: viewer members can read documents in
   their workspace but must never be able to edit or delete them.
3. Make sure adding a member to a workspace validates the role it's given
   — an unrecognized role should be rejected, not silently accepted.
4. Add or strengthen tests so neither the bug nor an incomplete viewer
   implementation can silently regress.
5. Make sure you haven't broken any other existing behavior — in
   particular, workspace owners must still be able to manage any document
   within their *own* workspace, even ones they didn't personally create.

This exercise has **two deliverables**, not one: the authorization bug fix
and the viewer-role feature. Budget your time for both.

## Repository layout

```
app/
  main.py                              FastAPI app entrypoint
  api/deps.py                          Shared repository/service instances
  api/routes/documents.py              GET/PATCH/DELETE /documents/{id}
  api/routes/workspaces.py             POST /workspaces/{workspace_id}/members
  models/schemas.py                    Request/response Pydantic models
  services/permission_service.py       Authorization checks for documents
  services/document_service.py         Document read/write orchestration
  services/membership_service.py       Adding workspace members
  repositories/user_repository.py      In-memory users
  repositories/membership_repository.py   In-memory workspace memberships
  repositories/document_repository.py     In-memory documents
tests/
  test_permission_service.py           Unit tests for authorization logic
  test_documents_api.py                API-level tests for document routes
  test_membership_api.py               API-level tests for adding members
```

Requests identify the acting user via an `X-User-Id` header (there's no
login system in this exercise — the header stands in for an authenticated
caller).

## Setup

```bash
pip install -e ".[dev]"
```

## Running tests

```bash
pytest -q
```

Some tests currently fail — they encode the reported bug and the missing
viewer-role feature. The rest pass and describe behavior you must **not**
break.

## Constraints

- Keep changes scoped to the bug fix and the requested feature (plus any
  tests you add). Don't refactor unrelated code.
- Preserve the existing request/response shapes for the document and
  membership endpoints.
- A user's authority over a document must be determined solely by their
  role within *that document's own workspace* (or personal ownership of
  the document itself) — never by a role they hold in some other
  workspace. Workspace roles must stay workspace-scoped.
- Don't add a real database — the repositories stay in-memory, pure
  Python.

## AI tool policy

You may use an AI coding assistant. If you'd like it to behave the way a
real interview/OA proctor would configure it, load
`.ai/assessment-skill/SKILL.md` into your assistant as a system/project
instruction. It's written to work with any capable coding assistant, not
a specific product.

Using an assistant well is part of what's being evaluated — treat it like
a knowledgeable but junior pair programmer, not an oracle. You're expected
to reproduce the bug, form your own hypotheses, design the feature, and
verify anything the assistant suggests before you rely on it.

## Deliverables

- Your authorization bug fix.
- Your viewer-role implementation, including the role-validation gap.
- Any tests you added or changed.
- Be ready to explain: what the authorization bug's root cause was, how
  you found it, why your fix is correct, how you designed the viewer
  role, and what else you checked to make sure nothing else broke.
