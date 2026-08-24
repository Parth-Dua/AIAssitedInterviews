export type UserRole = 'employee' | 'manager' | 'admin';

export interface User {
  id: string;
  name: string;
  role: UserRole;
}

export type ExpenseReportStatus = 'pending' | 'approved' | 'rejected';

export interface ExpenseReport {
  id: string;
  employeeId: string;
  assignedManagerId: string;
  amount: number;
  status: ExpenseReportStatus;
  delegatedApproverId: string | null;
}

/** Shape accepted by POST /expense-reports. */
export interface ExpenseReportCreateInput {
  assignedManagerId: string;
  amount: number;
}

/** Shape accepted by POST /expense-reports/:id/delegate. */
export interface DelegateApprovalInput {
  delegateToUserId: string;
}

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace Express {
    interface Request {
      user?: User;
    }
  }
}
