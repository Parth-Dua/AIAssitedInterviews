# Expected Reasoning Path

## Part 1 — the duplicate-track bug

1. Run `npm test`; observe that `rejects adding the same trackId to the same
   playlist a second time` fails in both `tests/playlistService.test.ts` and
   `tests/playlistsApi.test.ts`, while the "two different playlists" variant
   of the same scenario passes.
2. Read the failure output: adding the same `trackId` twice to the same
   playlist succeeds both times (201 / no thrown error) instead of the
   second attempt being rejected.
3. Read the README's user complaint and confirm it matches: "the app is
   supposed to prevent adding a track that's already in the playlist, but
   it doesn't seem to be stopping duplicates."
4. Trace the request path: `routes/playlists.ts` → `POST
   /playlists/:id/songs` is wired to `addSong` in
   `controllers/playlistController.ts`, thin, passes `req.body` straight to
   `PlaylistService.addSongToPlaylist`. Not the bug.
5. Open `services/playlistService.ts::addSongToPlaylist`. Find the
   duplicate check:
   `playlist.songs.some((s) => s === (track as unknown as PlaylistSong))`.
   Notice it compares object *references*, not any field of either object —
   `trackId` is never read on either side.
6. Confirm this can never be true: `track` is a brand-new object built from
   `req.body` on every request; it can never be the same reference as an
   object already sitting in `playlist.songs` from a prior request. A quick
   experiment (log `track === playlist.songs[i]` for a genuinely-duplicate
   request, or just reason about JS object identity) confirms this.
7. Fix the comparator to compare `trackId` values:
   `playlist.songs.some((s) => s.trackId === track.trackId)`.
8. Re-run tests. The two originally-failing duplicate tests should now
   pass, and the "two different playlists" test should still pass (proving
   the fix is scoped per-playlist, not global — a candidate who wrote
   `Array.prototype.some` correctly but scoped it against every playlist's
   songs, or maintained a single global `Set<trackId>`, would fail this).
9. A careful candidate re-reads `playlistRepository.ts` to confirm `save`/
   `getById` don't clone objects (so the mutation-then-save pattern used
   elsewhere in the service is safe) and that nothing else relies on
   reference equality between request bodies and stored songs.

## Part 2 — cursor-based pagination

10. Read the feature request in the README:
    `GET /playlists/:id/songs?cursor=&limit=` should return `{ items,
    nextCursor }`, not a bare array of everything.
11. Run the pagination-related tests; observe both the "returns a paginated
    envelope" and "respects `limit`" tests failing at both layers — the
    current `listSongs` sorts by `sequence` and returns everything,
    ignoring `cursor`/`limit` entirely.
12. Read `types.ts` to see that `PlaylistSong.sequence` already exists and
    is described as "used for stable pagination... to keep tests
    deterministic" — and read `playlistRepository.ts::nextSequence` to see
    it's a monotonically increasing per-playlist counter, not derived from
    array length or position. This rules out "I need to add a sequence
    field myself" as a false lead.
13. Design the pagination: sort by `sequence` ascending, filter to
    `sequence > cursor` (or from the start if `cursor` is omitted), take
    `limit` items, and set `nextCursor` to the last returned item's
    `sequence` if a full page was returned, else `null`.
14. A candidate who instead reaches for `Array.prototype.slice(offset,
    offset + limit)`, treating `cursor` as a plain numeric offset, will
    pass every public test — nothing in the public suite mutates a playlist
    between two page fetches. This is the intended trap: the hidden
    delete-between-pages test specifically exercises DELETE landing between
    two GETs and will fail against an offset-based implementation. A strong
    candidate reasons about this *before* being told, from the observation
    that `DELETE /playlists/:id/songs/:trackId` exists and is a given,
    correct endpoint: "if a client deletes something mid-pagination, does
    my cursor still make sense?"
15. Re-run tests; all public tests pass with either pagination approach,
    but only the `sequence`-filtering approach is actually correct.

## Communication
A strong candidate can explain: (a) why `===` never matches for the
duplicate check and why the fix restores it without breaking the
per-playlist scoping, and (b) why a `sequence`-based cursor is more robust
than an array-offset cursor under concurrent mutation — specifically, that
an offset is a position in a mutable collection while a `sequence` value is
a stable identity that doesn't shift when other elements are removed.

A strong candidate reaches the duplicate-bug fix (step 7) within roughly
15-20 minutes, and reaches a `sequence`-based pagination design (step 13)
within the 60-75 minute timebox — ideally reasoning their way to it
directly rather than writing offset-slicing first and only fixing it after
a hidden-test failure they can't see. Noticing the DELETE-between-pages
risk unprompted, from reading the existing DELETE endpoint, is a strong
signal.
