import { Request, Response } from 'express';
import { NoteService, NoteNotFoundError } from '../services/noteService';
import { noteRepository } from '../repositories/noteRepository';
import { NoteSummary } from '../types';

const noteService = new NoteService(noteRepository);

export function listNotes(req: Request, res: Response): void {
  const notes: NoteSummary[] = noteService.listNotes().map(({ id, title, tags, version }) => ({
    id,
    title,
    tags,
    version,
  }));
  res.status(200).json(notes);
}

export function getNote(req: Request, res: Response): void {
  const { id } = req.params;

  try {
    const note = noteService.getNote(id);
    res.status(200).json(note);
  } catch (err) {
    if (err instanceof NoteNotFoundError) {
      res.status(404).json({ error: err.message });
      return;
    }
    throw err;
  }
}

export function createNote(req: Request, res: Response): void {
  const { title, content, tags } = req.body ?? {};

  if (typeof title !== 'string' || title.trim().length === 0) {
    res.status(400).json({ error: 'title is required' });
    return;
  }

  const note = noteService.createNote({ title, content, tags });
  res.status(201).json(note);
}

export function addTag(req: Request, res: Response): void {
  const { id } = req.params;
  const { tag } = req.body ?? {};

  if (typeof tag !== 'string' || tag.trim().length === 0) {
    res.status(400).json({ error: 'tag is required' });
    return;
  }

  try {
    const note = noteService.addTag(id, tag);
    res.status(200).json(note);
  } catch (err) {
    if (err instanceof NoteNotFoundError) {
      res.status(404).json({ error: err.message });
      return;
    }
    throw err;
  }
}

export function updateNote(req: Request, res: Response): void {
  const { id } = req.params;
  const { title, content, tags, version } = req.body ?? {};

  if (
    typeof title !== 'string' ||
    typeof content !== 'string' ||
    !Array.isArray(tags) ||
    typeof version !== 'number'
  ) {
    res.status(400).json({ error: 'title, content, tags, and version are required' });
    return;
  }

  try {
    const note = noteService.updateNote(id, { title, content, tags, version });
    res.status(200).json(note);
  } catch (err) {
    if (err instanceof NoteNotFoundError) {
      res.status(404).json({ error: err.message });
      return;
    }
    throw err;
  }
}
