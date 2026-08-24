import { Playlist, PlaylistSong } from '../types';

/**
 * In-memory store of playlists, keyed by playlist id. In production this
 * would be backed by a real database table; for this exercise a Map is
 * enough.
 *
 * Also tracks a per-playlist sequence counter, kept separately from the
 * `songs` array itself so that it survives removals: deleting a song must
 * never cause a future song to be assigned a `sequence` value that was
 * already used (which would break cursor-based pagination).
 */
export class PlaylistRepository {
  private readonly playlistsById: Map<string, Playlist> = new Map();
  private readonly sequenceCounters: Map<string, number> = new Map();

  constructor(seed: Playlist[] = []) {
    for (const playlist of seed) {
      this.playlistsById.set(playlist.id, playlist);
      this.sequenceCounters.set(playlist.id, highestSequence(playlist.songs));
    }
  }

  getById(id: string): Playlist | undefined {
    return this.playlistsById.get(id);
  }

  save(playlist: Playlist): Playlist {
    this.playlistsById.set(playlist.id, playlist);
    return playlist;
  }

  /**
   * Returns the next `sequence` value for a song added to the given
   * playlist, advancing the counter as a side effect. Callers must only
   * invoke this once they've decided the song will actually be added —
   * calling it for a request that ends up rejected (e.g. a duplicate) would
   * "waste" a sequence number.
   */
  nextSequence(playlistId: string): number {
    const current = this.sequenceCounters.get(playlistId) ?? 0;
    const next = current + 1;
    this.sequenceCounters.set(playlistId, next);
    return next;
  }

  /** Test/dev helper: not used by request handlers. */
  clear(): void {
    this.playlistsById.clear();
    this.sequenceCounters.clear();
  }

  /** Test/dev helper: replace all stored playlists with the given set. */
  resetWith(playlists: Playlist[]): void {
    this.clear();
    for (const playlist of playlists) {
      this.playlistsById.set(playlist.id, playlist);
      this.sequenceCounters.set(playlist.id, highestSequence(playlist.songs));
    }
  }
}

function highestSequence(songs: PlaylistSong[]): number {
  return songs.reduce((max, song) => Math.max(max, song.sequence), 0);
}

function seedSong(
  trackId: string,
  title: string,
  artist: string,
  sequence: number
): PlaylistSong {
  // Fixed, deterministic timestamps for seed data — real adds use Date.now().
  const BASE_TIME = 1_700_000_000_000;
  return { trackId, title, artist, addedAt: BASE_TIME + sequence * 1000, sequence };
}

export function createSeedPlaylists(): Playlist[] {
  const roadTripSongs: PlaylistSong[] = [
    seedSong('trk-101', 'Highway Lights', 'The Wandering Few', 1),
    seedSong('trk-102', 'Coastal Drive', 'Marina Sound', 2),
    seedSong('trk-103', 'Sunset Overpass', 'Ravine', 3),
    seedSong('trk-104', 'Open Road', 'Cassette Youth', 4),
    seedSong('trk-105', 'Desert Static', 'Lowbeam', 5),
    seedSong('trk-106', 'Mile Marker', 'The Wandering Few', 6),
    seedSong('trk-107', 'Windshield View', 'Coastal Static', 7),
    seedSong('trk-108', 'Gas Station Radio', 'Marina Sound', 8),
    seedSong('trk-109', 'Rearview', 'Ravine', 9),
    seedSong('trk-110', 'North on 9', 'Lowbeam', 10),
    seedSong('trk-111', 'Motel Neon', 'Cassette Youth', 11),
    seedSong('trk-112', 'Dashboard Glow', 'The Wandering Few', 12),
    seedSong('trk-113', 'Truck Stop Diner', 'Coastal Static', 13),
    seedSong('trk-114', 'Long Way Home', 'Marina Sound', 14),
    seedSong('trk-115', 'Backroads', 'Ravine', 15),
    seedSong('trk-116', 'Interstate Hum', 'Lowbeam', 16),
    seedSong('trk-117', 'Border Crossing', 'Cassette Youth', 17),
    seedSong('trk-118', 'Last Exit', 'The Wandering Few', 18),
  ];

  const studySongs: PlaylistSong[] = [
    seedSong('trk-201', 'Library Hours', 'Soft Focus', 1),
    seedSong('trk-202', 'Rainy Desk', 'Paper Lantern', 2),
    seedSong('trk-203', 'Low Lamp', 'Quiet Signal', 3),
  ];

  const workoutSongs: PlaylistSong[] = [
    seedSong('trk-301', 'Redline', 'Voltage Kids', 1),
    seedSong('trk-302', 'Sprint Set', 'Hard Reset', 2),
  ];

  return [
    { id: 'playlist-1', name: 'Road Trip Mix', ownerId: 'user-1', songs: roadTripSongs },
    { id: 'playlist-2', name: 'Chill Study Beats', ownerId: 'user-2', songs: studySongs },
    { id: 'playlist-3', name: 'Workout Hype', ownerId: 'user-1', songs: workoutSongs },
  ];
}

/** Default repository instance used by the app, seeded with sample data. */
export const playlistRepository = new PlaylistRepository(createSeedPlaylists());
