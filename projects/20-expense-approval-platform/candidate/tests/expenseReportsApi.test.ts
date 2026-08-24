import request from 'supertest';
import { app } from '../src/app';
import {
  expenseReportRepository,
  createSeedExpenseReports,
} from '../src/repositories/expenseReportRepository';

beforeEach(() => {
  expenseReportRepository.resetWith(createSeedExpenseReports());
});

describe('GET /health', () => {
  it('returns 200', async () => {
    const response = await request(app).get('/health');
    expect(response.status).toBe(200);
  });
});

describe('POST /expense-reports', () => {
  it('lets an employee create a report with status "pending"', async () => {
    const response = await request(app)
      .post('/expense-reports')
      .set('X-User-Id', 'user-1')
      .send({ assignedManagerId: 'user-3', amount: 88.5 });

    expect(response.status).toBe(201);
    expect(response.body.status).toBe('pending');
    expect(response.body.employeeId).toBe('user-1');
    expect(response.body.assignedManagerId).toBe('user-3');
    expect(response.body.delegatedApproverId).toBeNull();
  });

  it('rejects creation from a non-employee role', async () => {
    const response = await request(app)
      .post('/expense-reports')
      .set('X-User-Id', 'user-3')
      .send({ assignedManagerId: 'user-4', amount: 15 });

    expect(response.status).toBe(403);
  });
});

describe('GET /expense-reports/:id', () => {
  it('returns the report including its assigned manager', async () => {
    const created = await request(app)
      .post('/expense-reports')
      .set('X-User-Id', 'user-1')
      .send({ assignedManagerId: 'user-3', amount: 30 });

    const response = await request(app)
      .get(`/expense-reports/${created.body.id}`)
      .set('X-User-Id', 'user-1');

    expect(response.status).toBe(200);
    expect(response.body.assignedManagerId).toBe('user-3');
  });

  it('returns 404 for a report that does not exist', async () => {
    const response = await request(app)
      .get('/expense-reports/does-not-exist')
      .set('X-User-Id', 'user-1');

    expect(response.status).toBe(404);
  });
});

describe('POST /expense-reports/:id/approve', () => {
  it("lets the report's assigned manager approve it", async () => {
    const created = await request(app)
      .post('/expense-reports')
      .set('X-User-Id', 'user-1')
      .send({ assignedManagerId: 'user-3', amount: 60 });

    const response = await request(app)
      .post(`/expense-reports/${created.body.id}/approve`)
      .set('X-User-Id', 'user-3');

    expect(response.status).toBe(200);
    expect(response.body.status).toBe('approved');
  });

  it('lets an admin approve any report', async () => {
    const created = await request(app)
      .post('/expense-reports')
      .set('X-User-Id', 'user-2')
      .send({ assignedManagerId: 'user-4', amount: 60 });

    const response = await request(app)
      .post(`/expense-reports/${created.body.id}/approve`)
      .set('X-User-Id', 'user-5');

    expect(response.status).toBe(200);
    expect(response.body.status).toBe('approved');
  });

  it('rejects approval from a plain employee', async () => {
    const created = await request(app)
      .post('/expense-reports')
      .set('X-User-Id', 'user-1')
      .send({ assignedManagerId: 'user-3', amount: 60 });

    const response = await request(app)
      .post(`/expense-reports/${created.body.id}/approve`)
      .set('X-User-Id', 'user-2');

    expect(response.status).toBe(403);
  });

  it("rejects approval from a manager who is not this report's assigned manager", async () => {
    // Support report: an employee noticed a manager other than their own
    // approved one of their expense reports.
    const created = await request(app)
      .post('/expense-reports')
      .set('X-User-Id', 'user-1')
      .send({ assignedManagerId: 'user-3', amount: 60 });

    const response = await request(app)
      .post(`/expense-reports/${created.body.id}/approve`)
      .set('X-User-Id', 'user-4');

    expect(response.status).toBe(403);

    const check = await request(app)
      .get(`/expense-reports/${created.body.id}`)
      .set('X-User-Id', 'user-1');
    expect(check.body.status).toBe('pending');
  });
});

describe('POST /expense-reports/:id/reject', () => {
  it("lets the report's assigned manager reject it", async () => {
    const created = await request(app)
      .post('/expense-reports')
      .set('X-User-Id', 'user-2')
      .send({ assignedManagerId: 'user-4', amount: 22 });

    const response = await request(app)
      .post(`/expense-reports/${created.body.id}/reject`)
      .set('X-User-Id', 'user-4');

    expect(response.status).toBe(200);
    expect(response.body.status).toBe('rejected');
  });
});

describe('POST /expense-reports/:id/delegate', () => {
  it('lets the assigned manager delegate approval to another manager', async () => {
    const created = await request(app)
      .post('/expense-reports')
      .set('X-User-Id', 'user-1')
      .send({ assignedManagerId: 'user-3', amount: 40 });

    const response = await request(app)
      .post(`/expense-reports/${created.body.id}/delegate`)
      .set('X-User-Id', 'user-3')
      .send({ delegateToUserId: 'user-4' });

    expect(response.status).toBe(200);
    expect(response.body.delegatedApproverId).toBe('user-4');
  });
});
