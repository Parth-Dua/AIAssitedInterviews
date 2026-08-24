import { Playlist, PlaylistSong, SongPage, TrackInput } from '../types';
import { PlaylistRepository } from '../repositories/playlistRepository';

export class PlaylistNotFoundError extends Error {
  constructor(playlistId: string) {
    super(`Playlist not found: ${playlistId}`);
    this.name = 'PlaylistNotFoundError';
  }
}

export class DuplicateSongError extends Error {
  constructor(trackId: string) {
    super(`Track already in playlist: ${trackId}`);
    this.name = 'DuplicateSongError';
  }
}

const DEFAULT_PAGE_LIMIT = 50;

/**
 * Business logic for reading and mutating playlists. Sits between the
 * controllers (HTTP concerns) and the repository (storage concerns).
 */
export class PlaylistService {
  constructor(private readonly repository: PlaylistRepository) {}

  getPlaylist(playlistId: string): Playlist {
    const playlist = this.repository.getById(playlistId);
    if (!playlist) {
      throw new PlaylistNotFoundError(playlistId);
    }
    return playlist;
  }

  addSongToPlaylist(playlistId: string, track: TrackInput): Playlist {
    const playlist = this.repository.getById(playlistId);
    if (!playlist) {
      throw new PlaylistNotFoundError(playlistId);
    }

    // BUG FIX: compare on the identifying field (trackId), not object
    // reference. `track` is a freshly-parsed request body object and can
    // never be `===` to a stored PlaylistSong, so the old check never
    // fired.
    const alreadyExists = playlist.songs.some((s) => s.trackId === track.trackId);
    if (alreadyExists) {
      throw new DuplicateSongError(track.trackId);
    }

    const song: PlaylistSong = {
      ...track,
      addedAt: Date.now(),
      sequence: this.repository.nextSequence(playlist.id),
    };
    playlist.songs.push(song);
    return this.repository.save(playlist);
  }

  removeSongFromPlaylist(playlistId: string, trackId: string): Playlist {
    const playlist = this.repository.getById(playlistId);
    if (!playlist) {
      throw new PlaylistNotFoundError(playlistId);
    }

    playlist.songs = playlist.songs.filter((s) => s.trackId !== trackId);
    return this.repository.save(playlist);
  }

  /**
   * FEATURE: cursor-based pagination keyed on `sequence` (a stable,
   * monotonically increasing per-song identifier), not array index/offset.
   * Returns songs with `sequence > cursor` (or from the start if `cursor`
   * is omitted), up to `limit` items, ordered by `sequence` ascending.
   *
   * Using `sequence` instead of an offset means a deletion between two
   * page fetches can never cause the next page to silently skip a song:
   * the cursor identifies a specific song's position in the sequence, not
   * a position in the current (possibly-shrunk) array.
   */
  listSongs(playlistId: string, cursor?: number, limit: number = DEFAULT_PAGE_LIMIT): SongPage {
    const playlist = this.repository.getById(playlistId);
    if (!playlist) {
      throw new PlaylistNotFoundError(playlistId);
    }

    const sorted = [...playlist.songs].sort((a, b) => a.sequence - b.sequence);
    const filtered = cursor !== undefined ? sorted.filter((s) => s.sequence > cursor) : sorted;
    const items = filtered.slice(0, limit);
    const nextCursor = items.length === limit ? items[items.length - 1].sequence : null;

    return { items, nextCursor };
  }
}
