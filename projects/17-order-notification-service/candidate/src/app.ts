import express, { Express } from 'express';
import ordersRouter from './routes/orders';
import { requestLogger } from './middleware/requestLogger';
import { errorHandler } from './middleware/errorHandler';

/**
 * Builds the Express application: registers middleware and mounts routes.
 * Does not call `.listen()` — that happens in server.ts so the app can be
 * imported directly by tests (via supertest) without binding a port.
 */
export function createApp(): Express {
  const app = express();
  app.use(express.json());
  app.use(requestLogger);

  app.get('/health', (_req, res) => {
    res.status(200).json({ status: 'ok' });
  });

  app.use(ordersRouter);

  // Error-handling middleware MUST be registered last, after every route,
  // so Express recognizes it (by its 4-argument signature) and routes any
  // error passed to `next(err)` here.
  app.use(errorHandler);

  return app;
}

export const app = createApp();
