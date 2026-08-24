import { NoteRepository, createSeedNotes } from '../src/repositories/noteRepository';
import { NoteService, NoteNotFoundError } from '../src/services/noteService';

function makeService(): NoteService {
  return new NoteService(new NoteRepository(createSeedNotes()));
}

describe('NoteService.createNote', () => {
  it('creates a note with version 1', () => {
    const service = makeService();
    const note = service.createNote({ title: 'New note', content: 'Some content', tags: ['x'] });

    expect(note.version).toBe(1);
    expect(note.title).toBe('New note');
    expect(note.content).toBe('Some content');
    expect(note.tags).toEqual(['x']);
  });

  it('defaults content and tags when omitted', () => {
    const service = makeService();
    const note = service.createNote({ title: 'Bare note' });

    expect(note.content).toBe('');
    expect(note.tags).toEqual([]);
  });
});

describe('NoteService.getNote', () => {
  it('returns the correct note by id', () => {
    const service = makeService();
    const target = service.listNotes()[0];

    const fetched = service.getNote(target.id);
    expect(fetched).toEqual(target);
  });

  it('throws NoteNotFoundError for an unknown id', () => {
    const service = makeService();
    expect(() => service.getNote('does-not-exist')).toThrow(NoteNotFoundError);
  });
});

describe('NoteService.listNotes', () => {
  it('returns all seeded notes', () => {
    const service = makeService();
    const notes = service.listNotes();
    expect(notes.length).toBe(4);
  });
});

describe('NoteService.addTag', () => {
  it('adds a new tag and increments the version', () => {
    const service = makeService();
    const target = service.listNotes()[0];

    const updated = service.addTag(target.id, 'urgent');

    expect(updated.tags).toContain('urgent');
    expect(updated.version).toBe(target.version + 1);
  });

  it('does not duplicate a tag that is already present', () => {
    const service = makeService();
    const target = service.listNotes()[0];
    const existingTag = target.tags[0];

    const updated = service.addTag(target.id, existingTag);

    const occurrences = updated.tags.filter((t) => t === existingTag).length;
    expect(occurrences).toBe(1);
  });

  it('throws NoteNotFoundError for an unknown id', () => {
    const service = makeService();
    expect(() => service.addTag('does-not-exist', 'x')).toThrow(NoteNotFoundError);
  });
});

describe('NoteService.updateNote', () => {
  it('updates fields and increments version when given the current version', () => {
    const service = makeService();
    const target = service.getNote(service.listNotes()[0].id);

    const updated = service.updateNote(target.id, {
      title: 'Renamed',
      content: 'New content',
      tags: ['a', 'b'],
      version: target.version,
    });

    expect(updated.title).toBe('Renamed');
    expect(updated.content).toBe('New content');
    expect(updated.tags).toEqual(['a', 'b']);
    expect(updated.version).toBe(target.version + 1);
  });

  it('throws NoteNotFoundError for an unknown id', () => {
    const service = makeService();
    expect(() =>
      service.updateNote('does-not-exist', { title: 'x', content: 'y', tags: [], version: 1 })
    ).toThrow(NoteNotFoundError);
  });
});
