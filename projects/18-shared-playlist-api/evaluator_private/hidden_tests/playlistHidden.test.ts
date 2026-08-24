/**
 * Hidden tests. Copy this file into candidate/tests/ (it is not present in
 * the candidate repo) and run `npm test` from candidate/ after applying a
 * candidate's fix, or after applying reference_solution/ to validate the
 * answer key.
 */
import request from 'supertest';
import { app } from '../src/app';
import { playlistRepository, createSeedPlaylists } from '../src/repositories/playlistRepository';

beforeEach(() => {
  playlistRepository.resetWith(createSeedPlaylists());
});

describe('GET /playlists/:id/songs — pagination survives a deletion between pages', () => {
  it('does not skip a song that was never returned to the client', async () => {
    // This is the test that catches the tempting-but-wrong pagination
    // implementation: treating `cursor` as a plain array-index offset
    // instead of filtering on the stable `sequence` field. Offset-slicing
    // works fine with no mutation in between page fetches, but breaks the
    // instant a song already seen (or before the current page) is removed,
    // because the array shifts left and the next offset-based slice skips
    // whatever moved into the gap.
    const seeded = createSeedPlaylists().find((p) => p.id === 'playlist-1')!;
    const orderedSeedIds = [...seeded.songs]
      .sort((a, b) => a.sequence - b.sequence)
      .map((s) => s.trackId);

    const page1 = await request(app).get('/playlists/playlist-1/songs?limit=5');
    expect(page1.status).toBe(200);
    expect(page1.body.items.length).toBe(5);
    const page1Ids: string[] = page1.body.items.map((s: { trackId: string }) => s.trackId);

    // Delete a song that was already returned on page 1.
    const deletedId = page1Ids[2];
    const del = await request(app).delete(`/playlists/playlist-1/songs/${deletedId}`);
    expect(del.status).toBe(200);

    const page2 = await request(app).get(
      `/playlists/playlist-1/songs?cursor=${page1.body.nextCursor}&limit=5`
    );
    expect(page2.status).toBe(200);
    const page2Ids: string[] = page2.body.items.map((s: { trackId: string }) => s.trackId);

    // The 5 songs that came right after page 1 in original sequence order
    // (excluding the one we just deleted) must all show up on page 2 — none
    // may be silently skipped because of the deletion.
    const expectedOnPage2 = orderedSeedIds.slice(5, 10).filter((id) => id !== deletedId);
    for (const id of expectedOnPage2) {
      expect(page2Ids).toContain(id);
    }

    // No song appears on both pages, and the deleted song never reappears.
    const overlap = page1Ids.filter((id) => page2Ids.includes(id));
    expect(overlap).toEqual([]);
    expect(page2Ids).not.toContain(deletedId);
  });
});

describe('GET /playlists/:id/songs — full cursor traversal', () => {
  it('collects exactly the seeded songs, with no duplicates or gaps', async () => {
    const seeded = createSeedPlaylists().find((p) => p.id === 'playlist-1')!;

    const collected: string[] = [];
    let cursor: number | undefined;
    let guard = 0;

    while (guard++ < 100) {
      const query = cursor !== undefined ? `?cursor=${cursor}&limit=4` : '?limit=4';
      const response = await request(app).get(`/playlists/playlist-1/songs${query}`);
      expect(response.status).toBe(200);

      collected.push(...response.body.items.map((s: { trackId: string }) => s.trackId));

      if (response.body.nextCursor === null) {
        break;
      }
      cursor = response.body.nextCursor;
    }

    expect(collected.length).toBe(seeded.songs.length);
    expect(new Set(collected).size).toBe(seeded.songs.length);
  });
});

describe('POST /playlists/:id/songs — sequence counter integrity', () => {
  it('does not consume a sequence number on a rejected duplicate add', async () => {
    const before = await request(app).get('/playlists/playlist-2/songs?limit=100');
    const maxSequenceBefore = Math.max(
      0,
      ...before.body.items.map((s: { sequence: number }) => s.sequence)
    );
    const existingTrackId = before.body.items[0].trackId;

    // Repeated duplicate attempts must all be rejected...
    for (let i = 0; i < 3; i++) {
      const dup = await request(app)
        .post('/playlists/playlist-2/songs')
        .send({ trackId: existingTrackId, title: 'x', artist: 'y' });
      expect(dup.status).toBe(409);
    }

    // ...and must not have advanced the sequence counter: the next
    // successfully added song should get exactly maxSequenceBefore + 1, not
    // maxSequenceBefore + 4 (which would happen if each rejected duplicate
    // attempt still "used up" a sequence number).
    const added = await request(app)
      .post('/playlists/playlist-2/songs')
      .send({ trackId: 'trk-hidden-seq-check', title: 'New Song', artist: 'New Artist' });
    expect(added.status).toBe(201);

    const newSong = added.body.songs.find(
      (s: { trackId: string }) => s.trackId === 'trk-hidden-seq-check'
    );
    expect(newSong.sequence).toBe(maxSequenceBefore + 1);
  });
});

describe('POST /playlists/:id/songs — duplicate check is scoped per playlist, not global', () => {
  it('allows the same trackId across three different playlists, added out of seed order', async () => {
    // Extra rigor beyond the public "two different playlists" test: adds to
    // playlists in a different order than they were seeded, and to three
    // playlists instead of two, to catch a fix that accidentally
    // deduplicates against a single global set of track ids instead of
    // per-playlist.
    const shared = { trackId: 'trk-hidden-shared', title: 'Shared', artist: 'Shared Artist' };

    const r3 = await request(app).post('/playlists/playlist-3/songs').send(shared);
    const r1 = await request(app).post('/playlists/playlist-1/songs').send(shared);
    const r2 = await request(app).post('/playlists/playlist-2/songs').send(shared);

    expect(r3.status).toBe(201);
    expect(r1.status).toBe(201);
    expect(r2.status).toBe(201);

    // Each playlist should still independently reject a second add of the
    // same track — the fix must not have removed per-playlist dedup while
    // fixing the global-scoping concern.
    const dupOnPlaylist1 = await request(app).post('/playlists/playlist-1/songs').send(shared);
    expect(dupOnPlaylist1.status).toBe(409);
  });
});
