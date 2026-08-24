export interface PlaylistSong {
  trackId: string;
  title: string;
  artist: string;
  /** Epoch ms at the time the song was added. Not used for ordering — see `sequence`. */
  addedAt: number;
  /** Monotonically increasing integer assigned when a song is added to a given playlist. */
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
