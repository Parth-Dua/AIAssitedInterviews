/**
 * Hidden tests. Copy this file into candidate/tests/ (it is not present in
 * the candidate repo) and run `npm test` from candidate/ after applying a
 * candidate's fix, or after applying reference_solution/ to validate the
 * answer key.
 */
import request from 'supertest';
import { app } from '../src/app';
import { noteRepository, createSeedNotes } from '../src/repositories/noteRepository';

beforeEach(() => {
  noteRepository.reset(createSeedNotes());
});

describe('PUT /notes/:id — stale save after a quick-added tag', () => {
  it('does not lose a quick-added tag when a stale full-edit save follows', async () => {
    const list = await request(app).get('/notes');
    const target = list.body[0];

    // "Open the edit view" — captures a snapshot including the version.
    const loaded = await request(app).get(`/notes/${target.id}`);

    // Meanwhile, someone quick-adds a tag from the list view.
    const afterQuickAdd = await request(app)
      .post(`/notes/${target.id}/tags`)
      .send({ tag: 'urgent' });
    expect(afterQuickAdd.status).toBe(200);
    expect(afterQuickAdd.body.tags).toContain('urgent');

    // The still-open edit form now saves using its stale snapshot — old
    // version, tags that don't include 'urgent'.
    const staleSave = await request(app)
      .put(`/notes/${target.id}`)
      .send({
        title: loaded.body.title,
        content: loaded.body.content,
        tags: loaded.body.tags,
        version: loaded.body.version,
      });

    // The stale save must be rejected outright, not silently applied.
    expect(staleSave.status).toBe(409);

    const after = await request(app).get(`/notes/${target.id}`);
    expect(after.body.tags).toContain('urgent');
  });
});

describe('PUT /notes/:id — lost update between two sequential sessions', () => {
  it('rejects the second of two stale content saves instead of silently discarding the first', async () => {
    const list = await request(app).get('/notes');
    const target = list.body[0];

    // Two "sessions" both load the note at the same version before either
    // one saves.
    const sessionA = await request(app).get(`/notes/${target.id}`);
    const sessionB = await request(app).get(`/notes/${target.id}`);

    const saveA = await request(app)
      .put(`/notes/${target.id}`)
      .send({
        title: sessionA.body.title,
        content: 'Content from session A',
        tags: sessionA.body.tags,
        version: sessionA.body.version,
      });
    expect(saveA.status).toBe(200);
    expect(saveA.body.content).toBe('Content from session A');

    // Session B never re-fetched, so it still has the pre-A version.
    const saveB = await request(app)
      .put(`/notes/${target.id}`)
      .send({
        title: sessionB.body.title,
        content: 'Content from session B',
        tags: sessionB.body.tags,
        version: sessionB.body.version,
      });

    // This is the case a tags-only merge fix does NOT catch: nothing about
    // this scenario touches tags at all, only content. Session B's stale
    // save must be rejected, and session A's change must survive.
    expect(saveB.status).toBe(409);

    const after = await request(app).get(`/notes/${target.id}`);
    expect(after.body.content).toBe('Content from session A');
  });
});

describe('PUT /notes/:id — current version still succeeds', () => {
  it('allows a normal full-edit save when the version is current', async () => {
    const list = await request(app).get('/notes');
    const target = list.body[0];
    const loaded = await request(app).get(`/notes/${target.id}`);

    const response = await request(app)
      .put(`/notes/${target.id}`)
      .send({
        title: 'Freshly edited title',
        content: loaded.body.content,
        tags: loaded.body.tags,
        version: loaded.body.version,
      });

    expect(response.status).toBe(200);
    expect(response.body.title).toBe('Freshly edited title');
    expect(response.body.version).toBe(loaded.body.version + 1);
  });
});

describe('PUT /notes/:id — nonexistent note', () => {
  it('still returns 404, not a version conflict, for a note that does not exist', async () => {
    const response = await request(app)
      .put('/notes/does-not-exist')
      .send({ title: 'x', content: 'y', tags: [], version: 1 });

    expect(response.status).toBe(404);
  });
});

describe('quick-add-tag racing ahead of a rejected stale PUT', () => {
  it('keeps tags intact end-to-end across a rejected save and a further quick-add', async () => {
    const list = await request(app).get('/notes');
    const target = list.body[0];

    // Edit form opens, capturing version V.
    const loaded = await request(app).get(`/notes/${target.id}`);

    const quickAdd1 = await request(app)
      .post(`/notes/${target.id}/tags`)
      .send({ tag: 'race-1' });
    expect(quickAdd1.status).toBe(200);

    // The stale save (still holding version V) must be rejected.
    const staleSave = await request(app)
      .put(`/notes/${target.id}`)
      .send({
        title: loaded.body.title,
        content: loaded.body.content,
        tags: loaded.body.tags,
        version: loaded.body.version,
      });
    expect(staleSave.status).toBe(409);

    // A further quick-add after the rejection should still work normally
    // and both tags should be present.
    const quickAdd2 = await request(app)
      .post(`/notes/${target.id}/tags`)
      .send({ tag: 'race-2' });
    expect(quickAdd2.status).toBe(200);
    expect(quickAdd2.body.tags).toEqual(expect.arrayContaining(['race-1', 'race-2']));

    const final = await request(app).get(`/notes/${target.id}`);
    expect(final.body.tags).toEqual(expect.arrayContaining(['race-1', 'race-2']));
  });
});
