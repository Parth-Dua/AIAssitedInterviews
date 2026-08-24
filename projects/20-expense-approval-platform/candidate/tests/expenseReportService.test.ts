import {
  ExpenseReportRepository,
  createSeedExpenseReports,
} from '../src/repositories/expenseReportRepository';
import {
  ExpenseReportService,
  ExpenseReportNotFoundError,
  InvalidExpenseReportStateError,
} from '../src/services/expenseReportService';

function makeService(): ExpenseReportService {
  return new ExpenseReportService(new ExpenseReportRepository(createSeedExpenseReports()));
}

describe('ExpenseReportService.createReport', () => {
  it('creates a report with status "pending" and no delegate', () => {
    const service = makeService();
    const report = service.createReport('user-1', { assignedManagerId: 'user-3', amount: 55 });

    expect(report.status).toBe('pending');
    expect(report.delegatedApproverId).toBeNull();
    expect(report.employeeId).toBe('user-1');
    expect(report.assignedManagerId).toBe('user-3');
  });
});

describe('ExpenseReportService.approveReport', () => {
  it('allows the assigned manager to approve their report', () => {
    const service = makeService();
    const report = service.createReport('user-1', { assignedManagerId: 'user-3', amount: 55 });

    const approved = service.approveReport(report.id, 'user-3');

    expect(approved.status).toBe('approved');
  });

  it('allows an admin to approve any report', () => {
    const service = makeService();
    const report = service.createReport('user-1', { assignedManagerId: 'user-3', amount: 55 });

    const approved = service.approveReport(report.id, 'user-5');

    expect(approved.status).toBe('approved');
  });

  it("rejects approval from a manager who is not this report's assigned manager", () => {
    // Reproduces the support report: a manager other than the employee's
    // own assigned manager was able to approve their report.
    const service = makeService();
    const report = service.createReport('user-1', { assignedManagerId: 'user-3', amount: 55 });

    expect(() => service.approveReport(report.id, 'user-4')).toThrow();

    const reloaded = service.getReportById(report.id);
    expect(reloaded.status).toBe('pending');
  });

  it('throws ExpenseReportNotFoundError for an unknown report id', () => {
    const service = makeService();
    expect(() => service.approveReport('does-not-exist', 'user-3')).toThrow(
      ExpenseReportNotFoundError
    );
  });

  it('rejects approving a report that is not pending', () => {
    const service = makeService();
    const report = service.createReport('user-1', { assignedManagerId: 'user-3', amount: 55 });
    service.approveReport(report.id, 'user-3');

    expect(() => service.approveReport(report.id, 'user-3')).toThrow(
      InvalidExpenseReportStateError
    );
  });
});

describe('ExpenseReportService.rejectReport', () => {
  it('allows the assigned manager to reject their report', () => {
    const service = makeService();
    const report = service.createReport('user-2', { assignedManagerId: 'user-4', amount: 20 });

    const rejected = service.rejectReport(report.id, 'user-4');

    expect(rejected.status).toBe('rejected');
  });

  it("rejects rejection from a manager who is not this report's assigned manager", () => {
    const service = makeService();
    const report = service.createReport('user-2', { assignedManagerId: 'user-4', amount: 20 });

    expect(() => service.rejectReport(report.id, 'user-3')).toThrow();

    const reloaded = service.getReportById(report.id);
    expect(reloaded.status).toBe('pending');
  });
});
