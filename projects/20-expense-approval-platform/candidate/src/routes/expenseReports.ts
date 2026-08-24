import { Router } from 'express';
import { attachUser } from '../middleware/attachUser';
import { requireRole } from '../middleware/requireRole';
import {
  createExpenseReport,
  getExpenseReport,
  approveExpenseReport,
  rejectExpenseReport,
} from '../controllers/expenseReportController';

const router = Router();

router.post('/expense-reports', attachUser, requireRole('employee'), createExpenseReport);
router.get('/expense-reports/:id', attachUser, getExpenseReport);
router.post(
  '/expense-reports/:id/approve',
  attachUser,
  requireRole('manager', 'admin'),
  approveExpenseReport
);
router.post(
  '/expense-reports/:id/reject',
  attachUser,
  requireRole('manager', 'admin'),
  rejectExpenseReport
);

export default router;
