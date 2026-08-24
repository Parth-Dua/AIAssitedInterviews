import { Note } from '../types';

/**
 * In-memory store of notes, keyed by note id. In production this would be
 * backed by a real database table; for this exercise a Map is enough.
 */
export class NoteRepository {
  private readonly notesById: Map<string, Note> = new Map();

  constructor(seed: Note[] = []) {
    for (const note of seed) {
      this.notesById.set(note.id, note);
    }
  }

  getById(id: string): Note | undefined {
    return this.notesById.get(id);
  }

  getAll(): Note[] {
    return Array.from(this.notesById.values());
  }

  save(note: Note): Note {
    this.notesById.set(note.id, note);
    return note;
  }

  /** Test/dev helper: replace all stored notes with the given seed set. */
  reset(seed: Note[]): void {
    this.notesById.clear();
    for (const note of seed) {
      this.notesById.set(note.id, note);
    }
  }
}

let nextSeedId = 1;
function seedNote(title: string, content: string, tags: string[]): Note {
  const id = `note-${nextSeedId++}`;
  return { id, title, content, tags, version: 1 };
}

export function createSeedNotes(): Note[] {
  nextSeedId = 1;
  return [
    seedNote(
      'Onboarding checklist',
      'Accounts to set up: email, chat, VPN, repo access. Assign a buddy for the first week.',
      ['onboarding', 'process']
    ),
    seedNote(
      'Sprint retro notes',
      'Went well: deploy pipeline is faster. Needs work: standups running long.',
      ['retro', 'team']
    ),
    seedNote(
      'API design guidelines',
      'Use plural nouns for collection routes. Return 404 for missing resources, 400 for bad input.',
      ['engineering', 'reference']
    ),
    seedNote(
      'Q3 planning doc',
      'Top priorities: mobile app parity, reduce onboarding time, ship the reporting dashboard.',
      ['planning']
    ),
  ];
}

/** Default repository instance used by the app, seeded with sample data. */
export const noteRepository = new NoteRepository(createSeedNotes());
