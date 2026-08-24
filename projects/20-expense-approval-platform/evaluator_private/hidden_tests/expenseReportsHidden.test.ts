/**
 * Hidden tests. Copy this file into candidate/tests/ (it is not present in
 * the candidate repo) and run `npm test` from candidate/ after applying a
 * candidate's fix, or after applying reference_solution/ to validate the
 * answer key.
 */
import request from 'supertest';
import { app } from '../src/app';
import {
  expenseReportRepository,
  createSeedExpenseReports,
} from '../src/repositories/expenseReportRepository';

beforeEach(() => {
  expenseReportRepository.resetWith(createSeedExpenseReports());
});

async function createReport(employeeId: string, assignedManagerId: string, amount = 50) {
  const response = await request(app)
    .post('/expense-reports')
    .set('X-User-Id', employeeId)
    .send({ assignedManagerId, amount });
  return response.body;
}

// ---------------------------------------------------------------------------
// The delegation feature must actually change who can approve/reject —
// not merely record a value that nothing else consults.
// ---------------------------------------------------------------------------

describe('delegated approval — approve path', () => {
  it('lets the delegate approve the report after the assigned manager delegates', async () => {
    const report = await createReport('user-1', 'user-3', 75);

    const delegateResponse = await request(app)
      .post(`/expense-reports/${report.id}/delegate`)
      .set('X-User-Id', 'user-3')
      .send({ delegateToUserId: 'user-4' });
    expect(delegateResponse.status).toBe(200);

    const approveResponse = await request(app)
      .post(`/expense-reports/${report.id}/approve`)
      .set('X-User-Id', 'user-4');

    expect(approveResponse.status).toBe(200);
    expect(approveResponse.body.status).toBe('approved');
  });
});

describe('delegated approval — reject path', () => {
  it('lets the delegate reject the report after the assigned manager delegates', async () => {
    const report = await createReport('user-2', 'user-4', 120);

    const delegateResponse = await request(app)
      .post(`/expense-reports/${report.id}/delegate`)
      .set('X-User-Id', 'user-4')
      .send({ delegateToUserId: 'user-3' });
    expect(delegateResponse.status).toBe(200);

    const rejectResponse = await request(app)
      .post(`/expense-reports/${report.id}/reject`)
      .set('X-User-Id', 'user-3');

    expect(rejectResponse.status).toBe(200);
    expect(rejectResponse.body.status).toBe('rejected');
  });
});

// ---------------------------------------------------------------------------
// Only the report's own assigned manager (or an admin) may delegate it.
// ---------------------------------------------------------------------------

describe('delegation authorization', () => {
  it('rejects a delegate request from a manager who is not this report\'s assigned manager', async () => {
    const report = await createReport('user-1', 'user-3', 60);

    const response = await request(app)
      .post(`/expense-reports/${report.id}/delegate`)
      .set('X-User-Id', 'user-4')
      .send({ delegateToUserId: 'user-4' });

    expect(response.status).toBe(403);

    const check = await request(app)
      .get(`/expense-reports/${report.id}`)
      .set('X-User-Id', 'user-1');
    expect(check.body.delegatedApproverId).toBeNull();
  });

  it('allows an admin to delegate a report on behalf of the assigned manager', async () => {
    const report = await createReport('user-1', 'user-3', 60);

    const response = await request(app)
      .post(`/expense-reports/${report.id}/delegate`)
      .set('X-User-Id', 'user-5')
      .send({ delegateToUserId: 'user-4' });

    expect(response.status).toBe(200);
    expect(response.body.delegatedApproverId).toBe('user-4');
  });

  it('rejects delegating to a user who is not a manager', async () => {
    const report = await createReport('user-1', 'user-3', 60);

    const response = await request(app)
      .post(`/expense-reports/${report.id}/delegate`)
      .set('X-User-Id', 'user-3')
      .send({ delegateToUserId: 'user-2' });

    expect([400, 422]).toContain(response.status);

    const check = await request(app)
      .get(`/expense-reports/${report.id}`)
      .set('X-User-Id', 'user-1');
    expect(check.body.delegatedApproverId).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// Delegation only makes sense while a report is still awaiting a decision.
// ---------------------------------------------------------------------------

describe('delegation and report state', () => {
  it('rejects delegating a report that has already been approved', async () => {
    const report = await createReport('user-1', 'user-3', 60);
    await request(app)
      .post(`/expense-reports/${report.id}/approve`)
      .set('X-User-Id', 'user-3');

    const response = await request(app)
      .post(`/expense-reports/${report.id}/delegate`)
      .set('X-User-Id', 'user-3')
      .send({ delegateToUserId: 'user-4' });

    expect([400, 409, 422]).toContain(response.status);
  });
});

// ---------------------------------------------------------------------------
// The original reported bug's fix must hold even once delegation exists,
// and the admin override must survive it too.
// ---------------------------------------------------------------------------

describe('delegation does not widen who else can act on the report', () => {
  it('leaves the originally assigned manager able to act after delegating to someone else', async () => {
    const report = await createReport('user-1', 'user-3', 90);
    await request(app)
      .post(`/expense-reports/${report.id}/delegate`)
      .set('X-User-Id', 'user-3')
      .send({ delegateToUserId: 'user-4' });

    // user-3 is still the assigned manager even after naming a delegate —
    // delegation adds an additional approver, it does not revoke the
    // original manager's own authority.
    const response = await request(app)
      .post(`/expense-reports/${report.id}/reject`)
      .set('X-User-Id', 'user-3');

    expect(response.status).toBe(200);
    expect(response.body.status).toBe('rejected');
  });

  it('lets an admin approve a report regardless of any delegation on it', async () => {
    const report = await createReport('user-2', 'user-4', 200);
    await request(app)
      .post(`/expense-reports/${report.id}/delegate`)
      .set('X-User-Id', 'user-4')
      .send({ delegateToUserId: 'user-3' });

    const response = await request(app)
      .post(`/expense-reports/${report.id}/approve`)
      .set('X-User-Id', 'user-5');

    expect(response.status).toBe(200);
    expect(response.body.status).toBe('approved');
  });
});
