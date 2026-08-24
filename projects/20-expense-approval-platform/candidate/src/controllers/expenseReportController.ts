import { Request, Response } from 'express';
import {
  ExpenseReportService,
  ExpenseReportNotFoundError,
  InvalidExpenseReportStateError,
  ExpenseReportValidationError,
} from '../services/expenseReportService';
import { expenseReportRepository } from '../repositories/expenseReportRepository';

const expenseReportService = new ExpenseReportService(expenseReportRepository);

export function createExpenseReport(req: Request, res: Response): void {
  try {
    const report = expenseReportService.createReport(req.user!.id, req.body ?? {});
    res.status(201).json(report);
  } catch (err) {
    if (err instanceof ExpenseReportValidationError) {
      res.status(400).json({ error: err.message });
      return;
    }
    throw err;
  }
}

export function getExpenseReport(req: Request, res: Response): void {
  const { id } = req.params;
  try {
    const report = expenseReportService.getReportById(id);
    res.status(200).json(report);
  } catch (err) {
    if (err instanceof ExpenseReportNotFoundError) {
      res.status(404).json({ error: err.message });
      return;
    }
    throw err;
  }
}

export function approveExpenseReport(req: Request, res: Response): void {
  const { id } = req.params;
  try {
    const report = expenseReportService.approveReport(id, req.user!.id);
    res.status(200).json(report);
  } catch (err) {
    if (err instanceof ExpenseReportNotFoundError) {
      res.status(404).json({ error: err.message });
      return;
    }
    if (err instanceof InvalidExpenseReportStateError) {
      res.status(409).json({ error: err.message });
      return;
    }
    throw err;
  }
}

export function rejectExpenseReport(req: Request, res: Response): void {
  const { id } = req.params;
  try {
    const report = expenseReportService.rejectReport(id, req.user!.id);
    res.status(200).json(report);
  } catch (err) {
    if (err instanceof ExpenseReportNotFoundError) {
      res.status(404).json({ error: err.message });
      return;
    }
    if (err instanceof InvalidExpenseReportStateError) {
      res.status(409).json({ error: err.message });
      return;
    }
    throw err;
  }
}
