# Interview Follow-Up Questions (private)

1. **Why does `===` never detect the duplicate here?**
   Strong answer: `track` is a plain object parsed fresh from `req.body` on
   every request, so it's a distinct object in memory every time, even when
   its fields (`trackId`, `title`, `artist`) are identical to a song already
   stored in `playlist.songs`. `===` on two objects compares reference
   identity, not field-by-field value equality — since `track` was never
   the object that got pushed into `playlist.songs` on a prior request, the
   comparison is always `false`. The fix compares the identifying field
   (`trackId`) directly instead of the whole object.

2. **How did you narrow it down?**
   Strong answer: ran the failing tests first (the unit test against
   `PlaylistService` and the supertest HTTP test), read the assertions
   (adding the same `trackId` twice both times returns success instead of
   the second being rejected), then traced the request path from the route
   through the controller into the service, and read `addSongToPlaylist`
   line by line, paying attention to what the duplicate check actually
   compares.

3. **Why is `sequence`-based cursoring more robust than offset-based
   slicing under concurrent mutation?**
   Strong answer: an offset is a position in a mutable array — it only
   means "the Nth item" relative to the array's *current* contents at query
   time. If an item earlier in the array is removed between two page
   fetches, everything after it shifts left by one position, so the same
   offset now points at a different logical item, silently skipping
   whatever moved into the gap. A `sequence` value, by contrast, is a
   stable identity assigned once when a song is added and never reused or
   renumbered — filtering on `sequence > cursor` always means "everything
   added after this specific song," regardless of what's been removed
   since. This is a specific instance of the general offset-vs-keyset
   pagination tradeoff.

4. **How did you verify your pagination implementation was actually
   correct, not just passing the given tests?**
   Strong answer: they either designed a delete-between-pages scenario
   themselves (fetch a page, delete something already returned, fetch the
   next page, confirm nothing is skipped) or can articulate why they'd want
   to before shipping — full credit for reasoning about it even if they
   didn't write the exact hidden test. A candidate who only ran the given
   tests and stopped once they were green, without considering what
   `DELETE` does to their cursor scheme, is a weaker signal here.

5. **What tests would you add, and why?**
   Strong answer: a delete-between-pages test (catches offset-based
   pagination); a full-traversal test that pages via `nextCursor` until
   `null` and checks the total collected matches the seeded count with no
   duplicates or gaps (catches off-by-one errors in the cursor/limit
   boundary); a three-(or more)-playlist duplicate-scoping test (catches an
   overly broad fix that dedupes globally instead of per-playlist); a
   sequence-integrity test confirming a rejected duplicate doesn't consume
   a `sequence` number (catches subtle interactions between the dedup fix
   and the pagination feature if they're not implemented independently).

6. **How would you extend this if playlists needed to support reordering
   songs?**
   Strong answer: reordering (moving a song to a different position without
   removing/re-adding it) is not naturally expressible with the current
   monotonically-increasing `sequence` scheme, since `sequence` currently
   also serves as "insertion order." A reasonable approach is separating
   *pagination identity* from *display order*: keep `sequence` purely as a
   stable, never-reused id for cursoring, and add a separate mutable `rank`
   / `position` field (e.g. a float or a fractional-indexing scheme) that
   the client can reorder without needing to renumber every other song or
   invalidate outstanding cursors. A weaker answer might not distinguish
   these two concerns and propose renumbering `sequence` on reorder, which
   would silently break any client mid-pagination (the same class of bug as
   the pagination feature in this exercise).
