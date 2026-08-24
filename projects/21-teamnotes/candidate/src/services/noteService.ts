import { Note, NoteCreateInput, NoteUpdatePayload } from '../types';
import { NoteRepository } from '../repositories/noteRepository';

export class NoteNotFoundError extends Error {
  constructor(noteId: string) {
    super(`Note not found: ${noteId}`);
    this.name = 'NoteNotFoundError';
  }
}

let nextGeneratedId = 1000;
function generateNoteId(): string {
  return `note-${nextGeneratedId++}`;
}

/**
 * Business logic for reading and mutating notes. Sits between the
 * controllers (HTTP concerns) and the repository (storage concerns).
 */
export class NoteService {
  constructor(private readonly repository: NoteRepository) {}

  listNotes(): Note[] {
    return this.repository.getAll();
  }

  getNote(id: string): Note {
    const note = this.repository.getById(id);
    if (!note) {
      throw new NoteNotFoundError(id);
    }
    return note;
  }

  createNote(input: NoteCreateInput): Note {
    const note: Note = {
      id: generateNoteId(),
      title: input.title,
      content: input.content ?? '',
      tags: input.tags ?? [],
      version: 1,
    };
    return this.repository.save(note);
  }

  /** Appends a single tag to a note if it isn't already present. */
  addTag(id: string, tag: string): Note {
    const existing = this.repository.getById(id);
    if (!existing) {
      throw new NoteNotFoundError(id);
    }

    const tags = existing.tags.includes(tag) ? existing.tags : [...existing.tags, tag];

    const updated: Note = {
      ...existing,
      tags,
      version: existing.version + 1,
    };

    return this.repository.save(updated);
  }

  /** Applies a full edit (title/content/tags) submitted by a client. */
  updateNote(id: string, payload: NoteUpdatePayload): Note {
    const existing = this.repository.getById(id);
    if (!existing) {
      throw new NoteNotFoundError(id);
    }

    const updated: Note = {
      id: existing.id,
      title: payload.title,
      content: payload.content,
      tags: payload.tags,
      version: existing.version + 1,
    };

    return this.repository.save(updated);
  }
}
