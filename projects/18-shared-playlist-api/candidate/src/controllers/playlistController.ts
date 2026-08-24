import { Request, Response } from 'express';
import {
  PlaylistService,
  PlaylistNotFoundError,
  DuplicateSongError,
} from '../services/playlistService';
import { playlistRepository } from '../repositories/playlistRepository';

const playlistService = new PlaylistService(playlistRepository);

export function getPlaylist(req: Request, res: Response): void {
  const { id } = req.params;

  try {
    const playlist = playlistService.getPlaylist(id);
    res.status(200).json(playlist);
  } catch (err) {
    if (err instanceof PlaylistNotFoundError) {
      res.status(404).json({ error: err.message });
      return;
    }
    throw err;
  }
}

export function addSong(req: Request, res: Response): void {
  const { id } = req.params;

  try {
    const playlist = playlistService.addSongToPlaylist(id, req.body ?? {});
    res.status(201).json(playlist);
  } catch (err) {
    if (err instanceof PlaylistNotFoundError) {
      res.status(404).json({ error: err.message });
      return;
    }
    if (err instanceof DuplicateSongError) {
      res.status(409).json({ error: err.message });
      return;
    }
    throw err;
  }
}

export function listSongs(req: Request, res: Response): void {
  const { id } = req.params;
  const cursor = req.query.cursor !== undefined ? Number(req.query.cursor) : undefined;
  const limit = req.query.limit !== undefined ? Number(req.query.limit) : undefined;

  try {
    const result = playlistService.listSongs(id, cursor, limit);
    res.status(200).json(result);
  } catch (err) {
    if (err instanceof PlaylistNotFoundError) {
      res.status(404).json({ error: err.message });
      return;
    }
    throw err;
  }
}

export function removeSong(req: Request, res: Response): void {
  const { id, trackId } = req.params;

  try {
    const playlist = playlistService.removeSongFromPlaylist(id, trackId);
    res.status(200).json(playlist);
  } catch (err) {
    if (err instanceof PlaylistNotFoundError) {
      res.status(404).json({ error: err.message });
      return;
    }
    throw err;
  }
}
