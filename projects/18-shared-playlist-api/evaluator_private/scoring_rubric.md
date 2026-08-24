# Scoring Rubric — Project 18 (100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the route → controller → service → repository flow for `POST`/`GET`/`DELETE` on `/playlists/:id/songs`; read `playlistRepository.ts` to confirm `sequence` is already a stable, monotonically increasing per-playlist counter (not derived from array position) before designing pagination. |
| Debugging process | 10 | Reproduced the duplicate-track bug via the failing tests (or equivalent manual repro) before making changes; didn't shotgun-edit multiple files; verified the fix against both the "same playlist rejects" and "different playlists both succeed" cases. |
| Root-cause reasoning | 15 | Correctly identifies that `addSongToPlaylist`'s duplicate check compares object references (`===`) instead of `trackId` values, and can articulate why a freshly-parsed request body object can never be reference-equal to a stored `PlaylistSong`. |
| Bug-fix correctness | 15 | Public tests pass; hidden per-playlist-scoping test passes (fix compares `trackId`, not whole objects, and isn't scoped globally across all playlists); duplicate rejection returns a clear 409-style response and doesn't mutate the stored playlist. |
| Feature implementation quality | 20 | Pagination is keyed on `sequence`, not array index/offset; correctly filters `sequence > cursor`, honors `limit`, and sets `nextCursor` per the stated rule; passes the hidden delete-between-pages test (does **not** silently skip a song after a deletion lands between two page fetches) and the full-traversal test (paging via `nextCursor` until `null` collects every song exactly once). |
| Tests added | 10 | Added at least one regression test beyond the given failing ones for the bug fix and/or the pagination feature (e.g., an own delete-between-pages test, a sequence-integrity test, a three-playlist scoping test), or meaningfully strengthened existing coverage. |
| Scope discipline | 5 | Did not modify unrelated files/behavior (repository internals beyond what pagination requires, `GET /playlists/:id`, `DELETE` semantics, seed data) without justification; did not add unrequested features (e.g., sorting/filtering by artist, reordering). |
| Communication | 15 | Can clearly state expected vs. actual behavior for the duplicate bug, the root cause, why the fix is correct and properly scoped; can explain the pagination design and why `sequence`-based cursoring is more robust than offset-based slicing under concurrent mutation, including what they checked (or would check) around the DELETE endpoint's interaction with pagination. |

**Passing bar (strong intern/new-grad signal):** ≥75, hidden tests pass, and
candidate can explain both the root cause and the pagination design without
prompting.

**Red flags:**
- Duplicate-check fix passes the two originally-failing tests but fails the
  hidden three-playlist scoping test (deduped globally instead of
  per-playlist — see `bug_design.md`).
- Pagination passes all public tests but fails the hidden delete-between-
  pages test (implemented as array-index/offset slicing instead of
  `sequence`-based filtering — the intended trap; see `bug_design.md`).
- Candidate cannot explain *why* `===` never detects the duplicate, only
  that changing the comparator made the tests pass.
- Candidate cannot explain why an offset-based cursor is unsafe under
  concurrent mutation, even after their own delete-between-pages scenario is
  pointed out to them.
- Candidate rewrites large parts of the service/controller/routing "to be
  safe," changes the shape of `GET /playlists/:id`, `POST
  /playlists/:id/songs`'s response, or `DELETE`'s behavior without being
  asked to, or introduces a database/ORM-style abstraction unprompted.
- Candidate never reads `playlistRepository.ts` and assumes `sequence` isn't
  already tracked, reinventing a duplicate/parallel counter, or resets
  `sequence` from array length/position (which would make it collide after
  a deletion followed by an add).
