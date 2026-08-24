import { PlaylistRepository, createSeedPlaylists } from '../src/repositories/playlistRepository';
import {
  PlaylistService,
  PlaylistNotFoundError,
  DuplicateSongError,
} from '../src/services/playlistService';

function makeService(): PlaylistService {
  return new PlaylistService(new PlaylistRepository(createSeedPlaylists()));
}

describe('PlaylistService.addSongToPlaylist', () => {
  it('adds a new track to a playlist', () => {
    const service = makeService();

    const playlist = service.addSongToPlaylist('playlist-2', {
      trackId: 'trk-new-1',
      title: 'New Song',
      artist: 'New Artist',
    });

    const added = playlist.songs.find((s) => s.trackId === 'trk-new-1');
    expect(added).toBeDefined();
    expect(added?.title).toBe('New Song');
  });

  it('rejects adding the same trackId to the same playlist a second time', () => {
    // Reproduces the support report: the same track should not be
    // addable to a playlist it's already in.
    const service = makeService();
    const before = service.addSongToPlaylist('playlist-2', {
      trackId: 'trk-dup-1',
      title: 'Dup Song',
      artist: 'Dup Artist',
    });
    const countBefore = before.songs.length;

    expect(() =>
      service.addSongToPlaylist('playlist-2', {
        trackId: 'trk-dup-1',
        title: 'Dup Song',
        artist: 'Dup Artist',
      })
    ).toThrow(DuplicateSongError);

    const playlist = service.getPlaylist('playlist-2');
    expect(playlist.songs.length).toBe(countBefore);
  });

  it('allows the same trackId to be added to two different playlists', () => {
    // The duplicate check is scoped per playlist, not global.
    const service = makeService();

    service.addSongToPlaylist('playlist-2', {
      trackId: 'trk-shared-1',
      title: 'Shared Song',
      artist: 'Shared Artist',
    });
    const playlist3 = service.addSongToPlaylist('playlist-3', {
      trackId: 'trk-shared-1',
      title: 'Shared Song',
      artist: 'Shared Artist',
    });

    expect(playlist3.songs.some((s) => s.trackId === 'trk-shared-1')).toBe(true);
  });

  it('throws PlaylistNotFoundError for an unknown playlist', () => {
    const service = makeService();

    expect(() =>
      service.addSongToPlaylist('does-not-exist', {
        trackId: 'trk-x',
        title: 'x',
        artist: 'x',
      })
    ).toThrow(PlaylistNotFoundError);
  });
});

describe('PlaylistService.removeSongFromPlaylist', () => {
  it('removes a track from the playlist', () => {
    const service = makeService();
    const playlist = service.getPlaylist('playlist-2');
    const target = playlist.songs[0];

    const updated = service.removeSongFromPlaylist('playlist-2', target.trackId);

    expect(updated.songs.some((s) => s.trackId === target.trackId)).toBe(false);
  });
});

describe('PlaylistService.listSongs', () => {
  it('returns a paginated envelope ({items, nextCursor}) ordered by sequence', () => {
    const service = makeService();

    const page = service.listSongs('playlist-1') as unknown as {
      items: { sequence: number }[];
      nextCursor: number | null;
    };

    expect(page).not.toBeInstanceOf(Array);
    expect(Array.isArray(page.items)).toBe(true);
    expect('nextCursor' in page).toBe(true);

    for (let i = 1; i < page.items.length; i++) {
      expect(page.items[i].sequence).toBeGreaterThan(page.items[i - 1].sequence);
    }
  });

  it('respects `limit` and returns a non-null nextCursor when more songs remain', () => {
    const service = makeService();

    const page = service.listSongs('playlist-1', undefined, 5) as unknown as {
      items: unknown[];
      nextCursor: number | null;
    };

    expect(page.items.length).toBe(5);
    expect(page.nextCursor).not.toBeNull();
  });
});
