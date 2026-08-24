import { Request, Response, NextFunction } from 'express';
import { userRepository } from '../repositories/userRepository';

/**
 * Reads the `X-User-Id` header, looks up the corresponding user, and
 * attaches it to `req.user`. Downstream middleware and handlers read
 * `req.user` to find out who is making the request. Responds 401 if the
 * header is missing or does not match a known user.
 */
export function attachUser(req: Request, res: Response, next: NextFunction): void {
  const headerValue = req.header('X-User-Id');

  if (!headerValue) {
    res.status(401).json({ error: 'X-User-Id header is required' });
    return;
  }

  const user = userRepository.getById(headerValue);
  if (!user) {
    res.status(401).json({ error: `Unknown user: ${headerValue}` });
    return;
  }

  req.user = user;
  next();
}
