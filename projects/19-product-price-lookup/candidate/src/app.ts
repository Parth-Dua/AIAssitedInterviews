import express, { Express } from 'express';
import pricesRouter from './routes/prices';

/**
 * Builds the Express application: registers middleware and mounts routes.
 * Does not call `.listen()` — that happens in server.ts so the app can be
 * imported directly by tests (via supertest) without binding a port.
 */
export function createApp(): Express {
  const app = express();
  app.use(express.json());

  app.get('/health', (_req, res) => {
    res.status(200).json({ status: 'ok' });
  });

  app.use(pricesRouter);

  return app;
}

export const app = createApp();
