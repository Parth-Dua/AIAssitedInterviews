# Shared Playlist API — Duplicate Track Bug + Pagination (Interview Exercise)

**Format:** AI-Assisted Debugging + Feature Implementation Assessment
**Timebox:** 60–75 minutes
**Level:** SWE Intern / New Grad / Backend
**Difficulty:** 7/10 — calibrated to Amazon-style SWE repo-based debugging/
feature-implementation online assessments (repo-based, unfamiliar code, one
reported bug plus one requested feature, public + hidden tests). This
project does not assume you've attempted any other project in this
curriculum.

## Scenario

You've just joined the team behind an internal shared-playlist tool: users
create playlists and add tracks to them, and a playlist can be built up
collaboratively over time. It's a small internal service — you haven't seen
this code before today.

Support has escalated a user complaint:

> "Users report that the same song sometimes appears more than once in a
> playlist — the app is supposed to prevent adding a track that's already in
> the playlist, but it doesn't seem to be stopping duplicates."

Separately, product has a feature request for the same area of the code:

> "Some of our users' playlists have grown to hundreds of tracks. Right now
> `GET /playlists/:id/songs` returns every song in a single response — we
> need real pagination (`cursor` + `limit`) before this becomes a
> performance problem."

## Your task

1. Reproduce the reported duplicate-track bug.
2. Find the root cause and fix it, so a track that's already in a playlist
   cannot be added to that same playlist again.
3. Implement cursor-based pagination for `GET /playlists/:id/songs`: it
   should accept `cursor` and `limit` query parameters and return
   `{ items, nextCursor }` — not the full, unpaginated list it returns
   today.
4. Add or strengthen tests for both the fix and the new feature so neither
   can silently regress.
5. Make sure you haven't broken any other existing behavior.

## Repository layout

```
src/
  app.ts                                Express app setup (middleware, routes)
  server.ts                             Entrypoint — imports app, calls .listen()
  types.ts                              Playlist / PlaylistSong / request shapes
  routes/playlists.ts                   Router for /playlists
  controllers/playlistController.ts     Request/response handling
  services/playlistService.ts           Playlist business logic (add/remove/list songs)
  repositories/playlistRepository.ts    In-memory playlist store (seeded with sample data)
tests/
  playlistService.test.ts               Unit tests against the service directly
  playlistsApi.test.ts                  HTTP-level tests against the Express app (supertest)
```

## Setup

```bash
npm install
```

## Running tests

```bash
npm test
```

Several tests currently fail: some reproduce the duplicate-track bug, others
describe the pagination behavior that doesn't exist yet. The rest pass and
describe behavior you must **not** break.

## Constraints

- Preserve the existing shapes of `GET /playlists/:id`, `POST
  /playlists/:id/songs`, and `DELETE /playlists/:id/songs/:trackId` — you're
  not asked to change these endpoints.
- Keep your changes scoped to the reported bug and the requested pagination
  feature (plus tests). Don't refactor unrelated code or add functionality
  beyond what's described above.

## AI tool policy

You may use an AI coding assistant. If you'd like it to behave the way a
real interview/OA proctor would configure it, load
`.ai/assessment-skill/SKILL.md` into your assistant as a system/project
instruction. It's written to work with any capable coding assistant, not
a specific product.

Using an assistant well is part of what's being evaluated — treat it like
a knowledgeable but junior pair programmer, not an oracle. You're expected
to reproduce the bug, form your own hypotheses, design the pagination
approach yourself, and verify anything the assistant suggests before you
rely on it.

## Deliverables

- Your code fix for the duplicate-track bug.
- Your implementation of cursor-based pagination.
- Any tests you added or changed.
- Be ready to explain: what the root cause of the bug was, how you found it,
  why your fix is correct, how your pagination design works and why you
  chose it, and what else you checked to make sure nothing else broke.
