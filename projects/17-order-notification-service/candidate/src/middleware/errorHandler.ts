import { Request, Response, NextFunction } from 'express';
import { OrderValidationError } from './validateOrderCreate';
import { WarehouseUnavailableError } from '../services/warehouseNotifier';

interface ErrorResponseBody {
  error: {
    code: string;
    message: string;
  };
}

/**
 * Central error-handling middleware — this defines the API's error
 * response contract. It must be registered with `app.use(errorHandler)`
 * AFTER every route/router so Express recognizes it as an error handler
 * (by its 4-argument signature) and routes errors here via `next(err)`.
 */
export function errorHandler(
  err: unknown,
  _req: Request,
  res: Response,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  _next: NextFunction
): void {
  if (err instanceof OrderValidationError) {
    const body: ErrorResponseBody = {
      error: { code: 'INVALID_ORDER', message: err.message },
    };
    res.status(400).json(body);
    return;
  }

  if (err instanceof WarehouseUnavailableError) {
    const body: ErrorResponseBody = {
      error: { code: 'WAREHOUSE_UNAVAILABLE', message: err.message },
    };
    res.status(502).json(body);
    return;
  }

  // eslint-disable-next-line no-console
  console.error(err);
  const body: ErrorResponseBody = {
    error: { code: 'INTERNAL_ERROR', message: 'An unexpected error occurred.' },
  };
  res.status(500).json(body);
}
