import { Request, Response, NextFunction } from 'express';

/**
 * Validates the body of a POST /boards/:boardId/tasks request. A task
 * cannot be created without a non-empty title.
 */
export function validateTaskCreate(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  const { title } = req.body ?? {};

  if (typeof title !== 'string' || title.trim().length === 0) {
    res.status(400).json({ error: 'title is required' });
    return;
  }

  next();
}
