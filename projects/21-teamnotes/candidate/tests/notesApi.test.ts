import request from 'supertest';
import { app } from '../src/app';
import { noteRepository, createSeedNotes } from '../src/repositories/noteRepository';

beforeEach(() => {
  noteRepository.reset(createSeedNotes());
});

describe('GET /health', () => {
  it('returns 200', async () => {
    const response = await request(app).get('/health');
    expect(response.status).toBe(200);
  });
});

describe('POST /notes', () => {
  it('creates a note with version 1', async () => {
    const response = await request(app)
      .post('/notes')
      .send({ title: 'New note from API', content: 'hello', tags: ['x'] });

    expect(response.status).toBe(201);
    expect(response.body.title).toBe('New note from API');
    expect(response.body.version).toBe(1);
  });

  it('rejects a note with a missing title', async () => {
    const response = await request(app).post('/notes').send({});
    expect(response.status).toBe(400);
  });
});

describe('GET /notes', () => {
  it('lists all seeded notes', async () => {
    const response = await request(app).get('/notes');

    expect(response.status).toBe(200);
    expect(Array.isArray(response.body)).toBe(true);
    expect(response.body.length).toBe(4);
  });
});

describe('GET /notes/:id', () => {
  it('returns the full note', async () => {
    const list = await request(app).get('/notes');
    const target = list.body[0];

    const response = await request(app).get(`/notes/${target.id}`);

    expect(response.status).toBe(200);
    expect(response.body.id).toBe(target.id);
    expect(response.body).toHaveProperty('content');
  });

  it('returns 404 for an unknown note', async () => {
    const response = await request(app).get('/notes/does-not-exist');
    expect(response.status).toBe(404);
  });
});

describe('POST /notes/:id/tags', () => {
  it('adds a tag and increments version', async () => {
    const list = await request(app).get('/notes');
    const target = list.body[0];

    const response = await request(app).post(`/notes/${target.id}/tags`).send({ tag: 'urgent' });

    expect(response.status).toBe(200);
    expect(response.body.tags).toContain('urgent');
    expect(response.body.version).toBe(target.version + 1);
  });

  it('does not duplicate an already-present tag', async () => {
    const list = await request(app).get('/notes');
    const target = list.body[0];
    const existingTag = target.tags[0];

    const response = await request(app)
      .post(`/notes/${target.id}/tags`)
      .send({ tag: existingTag });

    expect(response.status).toBe(200);
    const occurrences = response.body.tags.filter((t: string) => t === existingTag).length;
    expect(occurrences).toBe(1);
  });
});

describe('PUT /notes/:id', () => {
  it('updates fields and increments version when given the current version', async () => {
    const list = await request(app).get('/notes');
    const target = list.body[0];
    const full = await request(app).get(`/notes/${target.id}`);

    const response = await request(app)
      .put(`/notes/${target.id}`)
      .send({
        title: 'Updated title',
        content: 'Updated content',
        tags: ['x', 'y'],
        version: full.body.version,
      });

    expect(response.status).toBe(200);
    expect(response.body.title).toBe('Updated title');
    expect(response.body.content).toBe('Updated content');
    expect(response.body.tags).toEqual(['x', 'y']);
    expect(response.body.version).toBe(full.body.version + 1);
  });

  it('returns 404 for a note that does not exist', async () => {
    const response = await request(app)
      .put('/notes/does-not-exist')
      .send({ title: 'x', content: 'y', tags: [], version: 1 });

    expect(response.status).toBe(404);
  });
});

describe('POST /debug/reset', () => {
  it('restores the seeded starting state', async () => {
    await request(app).post('/notes').send({ title: 'Temporary note' });

    const beforeReset = await request(app).get('/notes');
    expect(beforeReset.body.length).toBe(5);

    const resetResponse = await request(app).post('/debug/reset');
    expect(resetResponse.status).toBe(200);

    const afterReset = await request(app).get('/notes');
    expect(afterReset.body.length).toBe(4);
  });
});
