import { Request, Response, NextFunction } from 'express';

/** Raised when a POST /orders body is missing or malformed. */
export class OrderValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'OrderValidationError';
  }
}

/**
 * Validates the body of a POST /orders request. An order cannot be placed
 * without a customer id, a warehouse id, and at least one line item with a
 * sku and a positive quantity. Forwards a typed error to Express's error
 * handling via `next(err)` rather than responding directly, so
 * `middleware/errorHandler.ts` is the single place that decides the shape
 * of an error response.
 */
export function validateOrderCreate(req: Request, _res: Response, next: NextFunction): void {
  const body = (req.body ?? {}) as Record<string, unknown>;
  const { customerId, warehouseId, items } = body;

  if (typeof customerId !== 'string' || customerId.trim().length === 0) {
    next(new OrderValidationError('customerId is required'));
    return;
  }

  if (typeof warehouseId !== 'string' || warehouseId.trim().length === 0) {
    next(new OrderValidationError('warehouseId is required'));
    return;
  }

  if (!Array.isArray(items) || items.length === 0) {
    next(new OrderValidationError('items must be a non-empty array'));
    return;
  }

  for (const item of items) {
    const record = item as Record<string, unknown>;
    const validSku = typeof record?.sku === 'string' && record.sku.trim().length > 0;
    const validQuantity = typeof record?.quantity === 'number' && record.quantity > 0;
    if (!validSku || !validQuantity) {
      next(new OrderValidationError('each item requires a sku and a positive quantity'));
      return;
    }
  }

  next();
}
