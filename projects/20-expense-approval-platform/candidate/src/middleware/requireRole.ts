import { Request, Response, NextFunction } from 'express';
import { UserRole } from '../types';

/**
 * Returns middleware that allows the request through only if `req.user`'s
 * role is one of `allowedRoles`. Must run after `attachUser`, which is
 * responsible for populating `req.user` in the first place. Responds 401
 * if no user is attached, 403 if the attached user's role is not allowed.
 */
export function requireRole(...allowedRoles: UserRole[]) {
  return (req: Request, res: Response, next: NextFunction): void => {
    if (!req.user) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    if (!allowedRoles.includes(req.user.role)) {
      res.status(403).json({ error: 'Forbidden: insufficient role' });
      return;
    }

    next();
  };
}
