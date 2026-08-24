import { Playlist, PlaylistSong, TrackInput } from '../types';
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

    const alreadyExists = playlist.songs.some((s) => s === (track as unknown as PlaylistSong));
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

  listSongs(playlistId: string, cursor?: number, limit?: number): PlaylistSong[] {
    const playlist = this.repository.getById(playlistId);
    if (!playlist) {
      throw new PlaylistNotFoundError(playlistId);
    }

    return [...playlist.songs].sort((a, b) => a.sequence - b.sequence);
  }
}
