import { ExpenseReport } from '../types';

/**
 * In-memory store of expense reports, keyed by report id. In production
 * this would be backed by a real database table; for this exercise a Map
 * is enough.
 */
export class ExpenseReportRepository {
  private readonly reportsById: Map<string, ExpenseReport> = new Map();

  constructor(seed: ExpenseReport[] = []) {
    for (const report of seed) {
      this.reportsById.set(report.id, report);
    }
  }

  getById(id: string): ExpenseReport | undefined {
    return this.reportsById.get(id);
  }

  listByEmployee(employeeId: string): ExpenseReport[] {
    return Array.from(this.reportsById.values()).filter(
      (report) => report.employeeId === employeeId
    );
  }

  save(report: ExpenseReport): ExpenseReport {
    this.reportsById.set(report.id, report);
    return report;
  }

  /** Test/dev helper: not used by request handlers. */
  clear(): void {
    this.reportsById.clear();
  }

  /** Test/dev helper: replace all stored reports with the given set. */
  resetWith(reports: ExpenseReport[]): void {
    this.clear();
    for (const report of reports) {
      this.reportsById.set(report.id, report);
    }
  }
}

let nextSeedId = 1;
function seedReport(
  employeeId: string,
  assignedManagerId: string,
  amount: number,
  status: ExpenseReport['status'],
  delegatedApproverId: string | null
): ExpenseReport {
  const id = `report-${nextSeedId++}`;
  return { id, employeeId, assignedManagerId, amount, status, delegatedApproverId };
}

export function createSeedExpenseReports(): ExpenseReport[] {
  nextSeedId = 1;
  return [
    seedReport('user-1', 'user-3', 128.5, 'pending', null),
    seedReport('user-1', 'user-3', 42.0, 'approved', null),
    seedReport('user-2', 'user-4', 310.75, 'pending', null),
    seedReport('user-2', 'user-4', 19.99, 'rejected', null),
  ];
}

/** Default repository instance used by the app, seeded with sample data. */
export const expenseReportRepository = new ExpenseReportRepository(createSeedExpenseReports());
