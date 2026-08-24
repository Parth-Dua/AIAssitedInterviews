# Notification Preferences — Stale Cache Bug + TTL Feature (Interview Exercise)

**Format:** Debugging + Feature Implementation
**Timebox:** 60–75 minutes
**Level:** SWE Intern / New Grad / Backend
**Difficulty:** 7/10

## Scenario

You've just joined the internal platform team. The notification
preferences service tracks, per user, which notification channels
(email/SMS/push) they've enabled. It's a small internal service — you
haven't seen this code before today.

To avoid hitting the "database" (an in-memory repository here, standing
in for a real one) on every request, a read-through cache sits in front
of it — a small hand-written in-memory cache, standing in for a
Redis-like cache. No real database or Redis server is involved in this
exercise.

Support has escalated a customer complaint, and the platform team has a
follow-up feature request.

### 1. A bug report

> "A user changed their SMS notifications from on to off in their
> settings, got a confirmation the change saved, but kept receiving SMS
> notifications for the next hour. When they checked the settings page
> again right after saving, it still showed the OLD value briefly before
> eventually 'fixing itself.'"

### 2. A feature request

> "Can we add a TTL (time-to-live) to the preferences cache? Even if
> something in the write path fails to invalidate the cache correctly,
> we'd like stale entries to expire on their own after a reasonable
> window, as defense in depth."

## Your task

1. Reproduce the reported bug, find its root cause, and fix it.
2. Implement TTL support for the cache: entries should expire after a
   configurable number of seconds, and the read-through path should use a
   sensible default TTL when it populates the cache.
3. Add or strengthen tests so neither the bug nor an incomplete TTL
   implementation can silently regress.
4. Make sure you haven't broken any other existing behavior.

This exercise has **two deliverables**, not one: the bug fix and the
feature. Budget your time for both.

## Repository layout

```
app/
  main.py                                       FastAPI app entrypoint
  api/routes/notification_prefs.py              GET/PUT /users/{user_id}/notification-preferences
  models/schemas.py                             Request/response Pydantic models
  services/notification_prefs_service.py        Read-through cache + write path
  repositories/notification_prefs_repository.py In-memory "database" of preferences
  cache/cache.py                                 Small in-memory cache (Redis-like), no real cache server
tests/
  test_notification_prefs_service.py            Unit tests for the service
  test_cache.py                                  Unit tests for the cache module
  test_notification_prefs_api.py                 API-level tests
```

## Setup

```bash
pip install -e ".[dev]"
```

## Running tests

```bash
pytest -q
```

Some tests currently fail — they encode the reported bug and the missing
TTL feature. The rest pass and describe behavior you must **not** break.

## Constraints

- Keep changes scoped to the bug fix and the requested feature (plus any
  tests you add). Don't refactor unrelated code.
- Preserve the existing request/response shapes for `GET` and `PUT`
  `/users/{user_id}/notification-preferences`.
- Don't require a real Redis server or database — the cache and
  repository stay in-memory, pure Python.
- Tests (yours included) must not rely on real wall-clock sleeping to
  exercise TTL behavior. The cache's clock should be controllable/fake so
  time-based behavior is deterministic and fast to test.

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

- Your bug fix.
- Your TTL implementation for the cache.
- Any tests you added or changed.
- Be ready to explain: what the stale-cache bug's root cause was, how you
  found it, why your fix is correct, how you designed the TTL feature
  (including how you tested time-based behavior without real sleeping),
  and what else you checked to make sure nothing else broke.
