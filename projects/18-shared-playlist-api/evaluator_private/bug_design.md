# Bug Design (private — do not expose to candidate)

## Expected behavior
`POST /playlists/:id/songs` prevents adding a track that is already in that
playlist. Invariant: "a playlist's `songs` array contains at most one entry
per distinct `trackId`." Adding a track already present in the playlist
should be rejected (409) and must not change the stored playlist.

## Actual (buggy) behavior
`PlaylistService.addSongToPlaylist` (`src/services/playlistService.ts`)
checks for a duplicate with:

```ts
const alreadyExists = playlist.songs.some((s) => s === (track as unknown as PlaylistSong));
```

`track` is a plain object built fresh from `req.body` on every request; it
is never the same object reference as any `PlaylistSong` already stored in
`playlist.songs` (those were constructed and pushed on a previous request).
`===` on two distinct object references is always `false`, regardless of
their field values, so `alreadyExists` is always `false` and the duplicate
branch never executes. A track can be added to the same playlist an
unbounded number of times.

## Root cause
Reference (identity) equality used where value equality on the identifying
field (`trackId`) was intended. The comparator never reads `track.trackId`
or `s.trackId` at all — it compares whole-object references. This is a
single-line defect in an otherwise-correct function; the rest of
`addSongToPlaylist` (lookup, `sequence` assignment, save) is fine, which is
deliberate — it should let a candidate quickly rule out "the whole add-song
flow is broken" and focus on why the specific duplicate check never fires.

## Violated invariant
"A playlist's `songs` array contains at most one entry per distinct
`trackId`." (Stated in the candidate README as the reported user complaint;
implied by the phrase "prevent adding a track that's already in the
playlist.")

## Relevant execution path
`POST /playlists/:id/songs` (`src/routes/playlists.ts`) → `addSong`
controller (`src/controllers/playlistController.ts`, thin — passes
`req.body` straight through to the service and maps `PlaylistNotFoundError`
to 404, `DuplicateSongError` to 409) → `PlaylistService.addSongToPlaylist`
(`src/services/playlistService.ts`, **the bug**) →
`PlaylistRepository.getById` / `.save` / `.nextSequence`
(`src/repositories/playlistRepository.ts`, correct, given). The candidate
should read the repository to see the `songs` array shape and that
`sequence` is already tracked per playlist (see the Feature section below)
before assuming the duplicate bug or the missing pagination might be a
repository-layer problem.

## Evidence available to the candidate
- The README states the bug report verbatim: the app is "supposed to
  prevent adding a track that's already in the playlist, but it doesn't
  seem to be stopping duplicates."
- The failing public tests (`rejects adding the same trackId to the same
  playlist a second time`, at both the service and HTTP layers) reproduce
  the exact reported behavior: a duplicate add succeeds (201/no throw)
  instead of being rejected.
- Reading `addSongToPlaylist` end-to-end shows a duplicate check that never
  reads `trackId` on either side of the comparison.

## Reasonable hypotheses
1. (Correct) The duplicate check in `addSongToPlaylist` compares object
   references (`===`) instead of `trackId` values, so it can never be true.
2. (Plausible, wrong) The repository's `save`/`getById` is returning a copy
   instead of the live object, so mutations to `playlist.songs` aren't
   persisted and some other, unrelated re-fetch is what shows duplicates —
   ruled out by reading `playlistRepository.ts`: `save` stores the exact
   object passed in via `Map.set`, `getById` returns the exact stored
   reference via `Map.get`, no cloning anywhere.
3. (Plausible, wrong) The route is registering `POST /playlists/:id/songs`
   twice, so the handler runs twice per request and a track gets added
   twice per call — ruled out by reading `routes/playlists.ts`, which
   registers each method+path combination exactly once.
4. (Plausible, wrong) `req.body` parsing is somehow constructing a new
   `trackId` each time even for "the same" request, so no two adds ever
   really share a `trackId` — ruled out by testing directly: sending the
   identical JSON body twice yields identical `trackId` values in both
   requests (trivially verifiable via a log or a repeated curl/supertest
   call), so the bug isn't in what's being compared, it's in how it's being
   compared.

## Intended regression tests
The two already-failing public tests (one at the service layer, one at the
HTTP layer) reproducing the duplicate-add bug, the public "two different
playlists" test establishing per-playlist (not global) scope, plus the
hidden tests in `hidden_tests/playlistHidden.test.ts`: the delete-between-
pages pagination test, the full-traversal test, the sequence-counter-
integrity test, and the stricter three-playlist duplicate-scoping test.

## Acceptable fixes
- Change the comparator to `playlist.songs.some((s) => s.trackId === track.trackId)`
  (the reference solution's approach).
- Equivalent phrasings: building a `Set<string>` of existing `trackId`s and
  checking membership; using `.find()`/`.findIndex()` on `trackId` instead
  of `.some()`; moving the check into the repository as a
  `hasTrack(playlistId, trackId)` helper, as long as it still compares
  `trackId` values and is still scoped to the one playlist being modified.
- The fix must **not** dedupe globally across all playlists (e.g. a single
  `Set<string>` of all track ids ever added, shared across playlists) — the
  public "same trackId on two different playlists" test and the hidden
  three-playlist scoping test both catch this.

## Tempting-but-incomplete/wrong pagination implementation (the feature side)
`GET /playlists/:id/songs?cursor=&limit=` must be implemented from scratch
(the starting code ignores `cursor`/`limit` entirely and returns every song
as a bare array). The tempting-but-wrong implementation treats `cursor` as a
plain **array-index offset** into the current `songs` array:

```ts
const offset = cursor ?? 0;
const items = sorted.slice(offset, offset + limit);
const nextCursor = items.length === limit ? offset + limit : null;
```

This passes every public test (correct item count for a given `limit`, a
non-null `nextCursor` when more songs exist) because none of the public
tests mutate the playlist between page fetches. It fails under a realistic
interleaving that the hidden tests specifically exercise: fetch page 1
(`limit=5`, offset 0) → `DELETE` one of the songs already returned on page
1 (via the given, correct `DELETE` endpoint) → fetch "page 2" using the
`nextCursor` the client received (`5`, still interpreted as an offset).
Because the array shrank by one and every later element shifted left by one
index, `slice(5, 10)` now returns the *sixth* song that currently exists in
the shrunken array — which was the *seventh* song in the original ordering
— silently skipping the song that should have been sixth. The client never
sees that song on either page, even though it still exists in the playlist
and was never returned to them.

Sequence-based cursoring (`filter((s) => s.sequence > cursor)`) is naturally
immune to this: `sequence` values are stable, assigned once per song and
never reused or renumbered, so a cursor value always identifies the same
logical position in the sequence regardless of what happens to the
in-memory array around it. This is exactly the lesson the exercise is
built to test — a very common real interview/OA topic (offset vs. keyset/
cursor pagination under concurrent mutation).

`hidden_tests/playlistHidden.test.ts`'s "does not skip a song that was
never returned to the client" test catches this precisely: validated
against the actual offset-slicing implementation (dedup bug fixed
correctly, only the pagination approach wrong), it produced exactly the
predicted failure — `trk-106` (the song immediately after the deleted one
in original sequence order) never appeared in either page's results. The
other three hidden tests, and all 16 public tests, still passed under the
offset-slicing implementation, confirming this is a genuinely narrow,
well-targeted regression test rather than a broad correctness net.

## Why this is interview-appropriate for an Amazon-style OA
A realistic "read an unfamiliar Express/TypeScript repo across
route → controller → service → repository, fix a reported correctness bug,
and implement a requested feature the same way you'd implement it in
production" shape — reference-equality-vs-value-equality bugs and
offset-vs-cursor pagination are both extremely common real interview/OA
topics for backend/full-stack roles, and pairing them in one exercise tests
whether a candidate can both diagnose an existing defect *and* design new
functionality without introducing an equally realistic new defect of its
own. The tempting-but-incomplete pagination design additionally rewards
candidates who think about what a "read" endpoint's cursor actually needs
to remain valid under concurrent writes, rather than treating pagination as
pure array slicing.
