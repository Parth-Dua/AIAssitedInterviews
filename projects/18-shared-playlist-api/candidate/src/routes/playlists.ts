import { Router } from 'express';
import { getPlaylist, addSong, listSongs, removeSong } from '../controllers/playlistController';

const router = Router();

router.get('/playlists/:id', getPlaylist);
router.post('/playlists/:id/songs', addSong);
router.get('/playlists/:id/songs', listSongs);
router.delete('/playlists/:id/songs/:trackId', removeSong);

export default router;
