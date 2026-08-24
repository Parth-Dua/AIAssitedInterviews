import { Request, Response, NextFunction } from 'express';
import { orderService } from '../services/orderService';
import { warehouseNotifier } from '../services/warehouseNotifier';

/**
 * Reference fix: wrap the async handler's body in try/catch and forward any
 * rejection (including one from `warehouseNotifier.notify`) to Express's
 * error-handling middleware via `next(err)`, instead of letting it become
 * an unhandled promise rejection that Express never turns into a response.
 *
 * An equally acceptable alternative (see bug_design.md) is to keep this
 * function's body exactly as it was and instead wrap the route registration
 * with a small `asyncHandler` utility that does the same
 * `Promise.resolve(fn(...)).catch(next)` forwarding once, for every route.
 */
export async function createOrder(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const order = orderService.createOrder(req.body);
    await warehouseNotifier.notify(order);
    res.status(201).json(order);
  } catch (err) {
    next(err);
  }
}
