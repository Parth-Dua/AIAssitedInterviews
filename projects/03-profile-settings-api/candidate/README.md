# Profile Settings API — Partial Update Bug (Interview Exercise)

**Format:** AI-Assisted Debugging Assessment
**Timebox:** 45–60 minutes
**Level:** SWE Intern / New Grad / Backend
**Difficulty:** 6/10

## Scenario

You've just joined the internal tools team. This small service stores each
user's account settings — display name, bio, timezone, and email
notification preference — and exposes a `PATCH` endpoint the settings page
uses to save changes as the user edits fields one at a time. It's a small
internal service — you haven't seen this code before today.

Support has escalated a customer complaint:

> "Someone on support noticed that updating just their timezone also
> silently cleared their bio and reset their email notification preference
> — even though they only sent `timezone` in the request."

## Your task

1. Reproduce the reported bug.
2. Find the root cause.
3. Fix it so that a `PATCH` request only ever changes the fields the caller
   actually included in the request body.
4. Add or strengthen tests so this can't silently regress.
5. Make sure you haven't broken any other existing behavior.

You do **not** need to add any new features — this is a bug fix only.

## Repository layout

```
app/
  main.py                            FastAPI app entrypoint
  api/routes/users.py                GET/PATCH /users/{user_id}
  models/schemas.py                  UserProfile / ProfileUpdateRequest models
  services/profile_service.py        Profile update business logic
  repositories/profile_repository.py In-memory profile store
tests/
  test_profile_service.py            Unit tests for the profile service
  test_profile_api.py                API-level tests
```

## Setup

```bash
pip install -e ".[dev]"
```

## Running tests

```bash
pytest -q
```

One test currently fails — it encodes the reported bug. The rest pass and
describe behavior you must **not** break.

## Constraints

- Keep changes scoped to fixing this bug (plus any tests you add). Don't
  refactor unrelated code.
- Preserve the existing public API (`GET /users/{user_id}` and
  `PATCH /users/{user_id}` request/response shape).
- Don't add a database or persistence layer — the in-memory repository is
  intentional for this exercise.

## AI tool policy

You may use an AI coding assistant. If you'd like it to behave the way a
real interview/OA proctor would configure it, load
`.ai/assessment-skill/SKILL.md` into your assistant as a system/project
instruction. It's written to work with any capable coding assistant, not
a specific product.

Using an assistant well is part of what's being evaluated — treat it like
a knowledgeable but junior pair programmer, not an oracle. You're expected
to reproduce the bug, form your own hypotheses, and verify anything it
suggests before you rely on it.

## Deliverables

- Your code fix.
- Any tests you added or changed.
- Be ready to explain: what the root cause was, how you found it, why your
  fix is correct, and what else you checked to make sure nothing else
  broke.
