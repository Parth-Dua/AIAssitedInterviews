import { ExpenseReport, ExpenseReportCreateInput } from '../types';
import { ExpenseReportRepository } from '../repositories/expenseReportRepository';
import { userRepository } from '../repositories/userRepository';

export class ExpenseReportNotFoundError extends Error {
  constructor(reportId: string) {
    super(`Expense report not found: ${reportId}`);
    this.name = 'ExpenseReportNotFoundError';
  }
}

export class InvalidExpenseReportStateError extends Error {
  constructor(reportId: string, status: string) {
    super(`Expense report ${reportId} is not pending (current status: ${status})`);
    this.name = 'InvalidExpenseReportStateError';
  }
}

export class ExpenseReportValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ExpenseReportValidationError';
  }
}

let nextGeneratedId = 1000;
function generateReportId(): string {
  return `report-${nextGeneratedId++}`;
}

/**
 * Business logic for reading and mutating expense reports. Sits between
 * the controllers (HTTP concerns) and the repository (storage concerns).
 */
export class ExpenseReportService {
  constructor(private readonly repository: ExpenseReportRepository) {}

  getReportById(reportId: string): ExpenseReport {
    const report = this.repository.getById(reportId);
    if (!report) {
      throw new ExpenseReportNotFoundError(reportId);
    }
    return report;
  }

  createReport(employeeId: string, input: ExpenseReportCreateInput): ExpenseReport {
    const manager = userRepository.getById(input.assignedManagerId);
    if (!manager || manager.role !== 'manager') {
      throw new ExpenseReportValidationError(
        `assignedManagerId must reference an existing manager: ${input.assignedManagerId}`
      );
    }
    if (typeof input.amount !== 'number' || !(input.amount > 0)) {
      throw new ExpenseReportValidationError('amount must be a positive number');
    }

    const report: ExpenseReport = {
      id: generateReportId(),
      employeeId,
      assignedManagerId: input.assignedManagerId,
      amount: input.amount,
      status: 'pending',
      delegatedApproverId: null,
    };
    return this.repository.save(report);
  }

  approveReport(reportId: string, actingUserId: string): ExpenseReport {
    const report = this.repository.getById(reportId);
    if (!report) {
      throw new ExpenseReportNotFoundError(reportId);
    }
    if (report.status !== 'pending') {
      throw new InvalidExpenseReportStateError(reportId, report.status);
    }

    report.status = 'approved';
    return this.repository.save(report);
  }

  rejectReport(reportId: string, actingUserId: string): ExpenseReport {
    const report = this.repository.getById(reportId);
    if (!report) {
      throw new ExpenseReportNotFoundError(reportId);
    }
    if (report.status !== 'pending') {
      throw new InvalidExpenseReportStateError(reportId, report.status);
    }

    report.status = 'rejected';
    return this.repository.save(report);
  }
}
