import express, { Express } from 'express';
import path from 'path';
import listingsRouter from './routes/listings';
import debugRouter from './routes/debug';

/**
 * Builds the Express application: serves the static frontend, registers
 * JSON body parsing, and mounts the API routes. Does not call `.listen()` —
 * that happens in server.ts so the app can be imported directly by tests
 * (via supertest) without binding a port.
 */
export function createApp(): Express {
  const app = express();
  app.use(express.json());

  app.use(express.static(path.join(__dirname, '..', 'public')));

  app.get('/health', (_req, res) => {
    res.status(200).json({ status: 'ok' });
  });

  app.use(listingsRouter);
  app.use(debugRouter);

  return app;
}

export const app = createApp();
