import { Request, Response, NextFunction } from 'express';

/**
 * Minimal request logger. Purely observational — it never blocks, mutates
 * the request/response, or short-circuits the chain. Included so there's
 * more than one link in the middleware chain to read through when tracing
 * a request end to end.
 */
export function requestLogger(req: Request, _res: Response, next: NextFunction): void {
  // eslint-disable-next-line no-console
  console.log(`[request] ${req.method} ${req.originalUrl}`);
  next();
}
