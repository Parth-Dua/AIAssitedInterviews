export interface PlaylistSong {
  trackId: string;
  title: string;
  artist: string;
  /** Epoch ms at the time the song was added. Not used for ordering — see `sequence`. */
  addedAt: number;
  /**
   * Monotonically increasing integer assigned to a song when it's added to a
   * given playlist. Used as the stable cursor for pagination instead of
   * wall-clock time or array position, so paging is deterministic and
   * unaffected by later removals.
   */
  sequence: number;
}

export interface Playlist {
  id: string;
  name: string;
  ownerId: string;
  songs: PlaylistSong[];
}

/** Shape accepted by POST /playlists/:id/songs. */
export interface TrackInput {
  trackId: string;
  title: string;
  artist: string;
}

/** Response envelope for GET /playlists/:id/songs. */
export interface SongPage {
  items: PlaylistSong[];
  nextCursor: number | null;
}
