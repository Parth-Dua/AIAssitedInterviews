import { Note, NoteCreateInput, NoteUpdatePayload } from '../types';
import { NoteRepository } from '../repositories/noteRepository';

export class NoteNotFoundError extends Error {
  constructor(noteId: string) {
    super(`Note not found: ${noteId}`);
    this.name = 'NoteNotFoundError';
  }
}

/**
 * Thrown when a full-edit save (`PUT /notes/:id`) is submitted against a
 * note that has changed since the client loaded its editing snapshot. The
 * client's payload is rejected outright — none of it is applied.
 */
export class VersionConflictError extends Error {
  constructor(
    public readonly noteId: string,
    public readonly expectedVersion: number,
    public readonly actualVersion: number
  ) {
    super(
      `Note ${noteId} has changed since it was loaded (expected version ${expectedVersion}, current version is ${actualVersion}).`
    );
    this.name = 'VersionConflictError';
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

  /**
   * Applies a full edit (title/content/tags) submitted by a client. The
   * client must include the version its edit form was loaded with; if the
   * note has changed since then (via any other write, e.g. a quick-added
   * tag), the save is rejected instead of silently overwriting the newer
   * state with the client's stale snapshot.
   */
  updateNote(id: string, payload: NoteUpdatePayload): Note {
    const existing = this.repository.getById(id);
    if (!existing) {
      throw new NoteNotFoundError(id);
    }

    if (payload.version !== existing.version) {
      throw new VersionConflictError(id, payload.version, existing.version);
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
