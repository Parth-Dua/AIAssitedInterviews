import request from 'supertest';
import { app } from '../src/app';
import { taskRepository, createSeedTasks } from '../src/repositories/taskRepository';

beforeEach(() => {
  taskRepository.resetWith(createSeedTasks());
});

describe('GET /health', () => {
  it('returns 200', async () => {
    const response = await request(app).get('/health');
    expect(response.status).toBe(200);
  });
});

describe('POST /boards/:boardId/tasks', () => {
  it('creates a task with default status "todo"', async () => {
    const response = await request(app)
      .post('/boards/board-1/tasks')
      .send({ title: 'New task from API' });

    expect(response.status).toBe(201);
    expect(response.body.title).toBe('New task from API');
    expect(response.body.status).toBe('todo');
    expect(response.body.boardId).toBe('board-1');
  });

  it('rejects a task with a missing title', async () => {
    const response = await request(app).post('/boards/board-1/tasks').send({});

    expect(response.status).toBe(400);
  });
});

describe('GET /boards/:boardId/tasks', () => {
  it('lists only tasks for the requested board', async () => {
    const response = await request(app).get('/boards/board-1/tasks');

    expect(response.status).toBe(200);
    expect(Array.isArray(response.body)).toBe(true);
    expect(response.body.length).toBeGreaterThan(0);
    for (const task of response.body) {
      expect(task.boardId).toBe('board-1');
    }
  });
});

describe('PATCH /tasks/:id', () => {
  it('updates the title and preserves other fields', async () => {
    const list = await request(app).get('/boards/board-1/tasks');
    const target = list.body[0];

    const response = await request(app)
      .patch(`/tasks/${target.id}`)
      .send({ title: 'Updated title' });

    expect(response.status).toBe(200);
    expect(response.body.title).toBe('Updated title');
    expect(response.body.status).toBe(target.status);
    expect(response.body.priority).toBe(target.priority);
  });

  it('returns 404 for a task that does not exist', async () => {
    const response = await request(app)
      .patch('/tasks/does-not-exist')
      .send({ title: 'x' });

    expect(response.status).toBe(404);
  });

  it('moves a task from "todo" to "in_progress"', async () => {
    // Support report: "the request succeeds (200) but the status shown
    // afterward is still 'todo'." This test encodes the expected behavior.
    const list = await request(app).get('/boards/board-1/tasks');
    const target = list.body.find((t: { status: string }) => t.status === 'todo');
    expect(target).toBeDefined();

    const response = await request(app)
      .patch(`/tasks/${target.id}`)
      .send({ status: 'in_progress' });

    expect(response.status).toBe(200);
    expect(response.body.status).toBe('in_progress');
  });
});
