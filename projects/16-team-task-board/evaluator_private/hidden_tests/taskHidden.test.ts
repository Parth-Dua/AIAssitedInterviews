/**
 * Hidden tests. Copy this file into candidate/tests/ (it is not present in
 * the candidate repo) and run `npm test` from candidate/ after applying a
 * candidate's fix, or after applying reference_solution/ to validate the
 * answer key.
 */
import request from 'supertest';
import { app } from '../src/app';
import { taskRepository, createSeedTasks } from '../src/repositories/taskRepository';

beforeEach(() => {
  taskRepository.resetWith(createSeedTasks());
});

describe('PATCH /tasks/:id — invalid status value', () => {
  it('rejects an invalid status value and leaves the stored status unchanged', async () => {
    const list = await request(app).get('/boards/board-1/tasks');
    const target = list.body.find((t: { status: string }) => t.status === 'todo');
    expect(target).toBeDefined();

    const response = await request(app)
      .patch(`/tasks/${target.id}`)
      .send({ status: 'bogus-value' });

    expect([400, 422]).toContain(response.status);

    const after = await request(app).get('/boards/board-1/tasks');
    const stillThere = after.body.find((t: { id: string }) => t.id === target.id);
    expect(stillThere.status).toBe('todo');
  });
});

describe('PATCH /tasks/:id — no linear status transition enforcement', () => {
  it('allows jumping directly from "todo" to "done", skipping "in_progress"', async () => {
    const list = await request(app).get('/boards/board-1/tasks');
    const target = list.body.find((t: { status: string }) => t.status === 'todo');
    expect(target).toBeDefined();

    const response = await request(app)
      .patch(`/tasks/${target.id}`)
      .send({ status: 'done' });

    expect(response.status).toBe(200);
    expect(response.body.status).toBe('done');
  });
});

describe('PATCH /tasks/:id — empty body', () => {
  it('changes nothing and returns 200', async () => {
    const list = await request(app).get('/boards/board-1/tasks');
    const target = list.body[0];

    const response = await request(app).patch(`/tasks/${target.id}`).send({});

    expect(response.status).toBe(200);
    expect(response.body).toEqual(target);
  });
});

describe('PATCH /tasks/:id — sequential partial updates', () => {
  it('accumulates changes across multiple single-field PATCH requests', async () => {
    const list = await request(app).get('/boards/board-1/tasks');
    const target = list.body[0];

    const afterTitle = await request(app)
      .patch(`/tasks/${target.id}`)
      .send({ title: 'Step 1 title' });
    expect(afterTitle.status).toBe(200);

    const afterPriority = await request(app)
      .patch(`/tasks/${target.id}`)
      .send({ priority: 'high' });
    expect(afterPriority.status).toBe(200);

    const afterAssignee = await request(app)
      .patch(`/tasks/${target.id}`)
      .send({ assigneeId: 'user-9' });
    expect(afterAssignee.status).toBe(200);

    const final = afterAssignee.body;
    expect(final.title).toBe('Step 1 title');
    expect(final.priority).toBe('high');
    expect(final.assigneeId).toBe('user-9');
    // status was never touched by these three requests
    expect(final.status).toBe(target.status);
  });
});
