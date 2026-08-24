import request from 'supertest';
import { app } from '../src/app';
import { playlistRepository, createSeedPlaylists } from '../src/repositories/playlistRepository';

beforeEach(() => {
  playlistRepository.resetWith(createSeedPlaylists());
});

describe('GET /health', () => {
  it('returns 200', async () => {
    const response = await request(app).get('/health');
    expect(response.status).toBe(200);
  });
});

describe('GET /playlists/:id', () => {
  it('returns playlist metadata', async () => {
    const response = await request(app).get('/playlists/playlist-2');

    expect(response.status).toBe(200);
    expect(response.body.id).toBe('playlist-2');
    expect(response.body.name).toBe('Chill Study Beats');
    expect(Array.isArray(response.body.songs)).toBe(true);
  });

  it('returns 404 for a playlist that does not exist', async () => {
    const response = await request(app).get('/playlists/does-not-exist');
    expect(response.status).toBe(404);
  });
});

describe('POST /playlists/:id/songs', () => {
  it('adds a track and it appears in the playlist', async () => {
    const response = await request(app)
      .post('/playlists/playlist-2/songs')
      .send({ trackId: 'trk-api-1', title: 'API Song', artist: 'API Artist' });

    expect(response.status).toBe(201);
    expect(
      response.body.songs.some((s: { trackId: string }) => s.trackId === 'trk-api-1')
    ).toBe(true);
  });

  it('rejects adding the same trackId to the same playlist a second time', async () => {
    // Support report: "the same song sometimes appears more than once in a
    // playlist ... it doesn't seem to be stopping duplicates."
    await request(app)
      .post('/playlists/playlist-2/songs')
      .send({ trackId: 'trk-api-dup', title: 'Dup', artist: 'Dup Artist' });

    const before = await request(app).get('/playlists/playlist-2');
    const countBefore = before.body.songs.length;

    const response = await request(app)
      .post('/playlists/playlist-2/songs')
      .send({ trackId: 'trk-api-dup', title: 'Dup', artist: 'Dup Artist' });

    expect(response.status).toBe(409);

    const after = await request(app).get('/playlists/playlist-2');
    expect(after.body.songs.length).toBe(countBefore);
  });

  it('allows the same trackId to be added to two different playlists', async () => {
    const r1 = await request(app)
      .post('/playlists/playlist-2/songs')
      .send({ trackId: 'trk-api-shared', title: 'Shared', artist: 'Shared Artist' });
    const r2 = await request(app)
      .post('/playlists/playlist-3/songs')
      .send({ trackId: 'trk-api-shared', title: 'Shared', artist: 'Shared Artist' });

    expect(r1.status).toBe(201);
    expect(r2.status).toBe(201);
  });
});

describe('GET /playlists/:id/songs', () => {
  it('returns a paginated envelope ({items, nextCursor}) instead of a bare array', async () => {
    const response = await request(app).get('/playlists/playlist-1/songs');

    expect(response.status).toBe(200);
    expect(Array.isArray(response.body)).toBe(false);
    expect(Array.isArray(response.body.items)).toBe(true);
    expect('nextCursor' in response.body).toBe(true);
  });

  it('returns exactly `limit` items and a non-null nextCursor when more songs exist', async () => {
    const response = await request(app).get('/playlists/playlist-1/songs?limit=5');

    expect(response.status).toBe(200);
    expect(response.body.items.length).toBe(5);
    expect(response.body.nextCursor).not.toBeNull();
  });
});

describe('DELETE /playlists/:id/songs/:trackId', () => {
  it('removes a track and confirms it is gone', async () => {
    const list = await request(app).get('/playlists/playlist-2');
    const target = list.body.songs[0];

    const response = await request(app).delete(
      `/playlists/playlist-2/songs/${target.trackId}`
    );
    expect(response.status).toBe(200);
    expect(
      response.body.songs.some((s: { trackId: string }) => s.trackId === target.trackId)
    ).toBe(false);

    const after = await request(app).get('/playlists/playlist-2');
    expect(
      after.body.songs.some((s: { trackId: string }) => s.trackId === target.trackId)
    ).toBe(false);
  });
});
