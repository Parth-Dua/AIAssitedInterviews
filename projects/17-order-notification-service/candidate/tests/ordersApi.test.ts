import http from 'http';
import request from 'supertest';
import { app } from '../src/app';
import { orderRepository } from '../src/repositories/orderRepository';
import { warehouseNotifier } from '../src/services/warehouseNotifier';

// This file exercises the API end to end over real HTTP (via supertest),
// including a request that the current code is reported to leave hanging.
// A generous file-level ceiling is set so a genuinely slow environment
// doesn't produce a flaky failure, but the "does it hang" test below does
// NOT rely on this timeout to detect the bug — it races the request
// against a short internal timer so the reproduction is fast and
// deterministic either way.
jest.setTimeout(10000);

const NEVER_RESOLVED = Symbol('never-resolved');
const RACE_WINDOW_MS = 300;

let server: http.Server;

beforeAll((done) => {
  server = app.listen(0, done);
});

afterAll((done) => {
  // Force-close any socket left open by the unresolved request in the
  // "hang" test below, then close the server itself, so this file never
  // leaves an open handle behind for Jest to wait on.
  server.closeAllConnections?.();
  server.close(done);
});

beforeEach(() => {
  orderRepository.clear();
  warehouseNotifier.resetLastNotifyOutcome();
});

describe('GET /health', () => {
  it('returns 200', async () => {
    const response = await request(server).get('/health');
    expect(response.status).toBe(200);
  });
});

describe('POST /orders — reachable warehouse', () => {
  it('returns 201 with the created order', async () => {
    const response = await request(server)
      .post('/orders')
      .send({
        customerId: 'cust-1',
        warehouseId: 'wh-1',
        items: [{ sku: 'sku-1', quantity: 2 }],
      });

    expect(response.status).toBe(201);
    expect(response.body.customerId).toBe('cust-1');
    expect(response.body.warehouseId).toBe('wh-1');
    expect(response.body.status).toBe('created');
  });
});

describe('POST /orders — missing required fields', () => {
  it('returns 400 and does not create an order', async () => {
    const response = await request(server).post('/orders').send({});

    expect(response.status).toBe(400);
    expect(orderRepository.list()).toHaveLength(0);
  });
});

describe('POST /orders — warehouse unreachable (bug report reproduction)', () => {
  it('eventually sends a response instead of leaving the request hanging', async () => {
    // Support report: "the client just waits and eventually times out"
    // for an order whose warehouse can't be reached. Reproduce that
    // concretely and quickly: race the request against a short timer
    // instead of waiting on a real client-side timeout. A correct
    // implementation only awaits a same-microtask rejection, so it should
    // respond almost immediately — well within this window.
    const pending = request(server)
      .post('/orders')
      .send({
        customerId: 'cust-2',
        warehouseId: 'wh-offline-1',
        items: [{ sku: 'sku-1', quantity: 1 }],
      });

    const raced = await Promise.race([
      pending,
      new Promise((resolve) => setTimeout(() => resolve(NEVER_RESOLVED), RACE_WINDOW_MS)),
    ]);

    // Swallow whatever eventually happens to a still-pending request (it
    // gets aborted when the server closes in afterAll) so it never
    // surfaces as an unhandled rejection.
    pending.catch(() => {});

    // A response must arrive — success or a clear error, either is fine
    // here; this test only proves the request doesn't hang. What shape a
    // correct error response must have is checked elsewhere.
    expect(raced).not.toBe(NEVER_RESOLVED);

    // Confirm *why* a response was expected at all: the warehouse notifier
    // really did reject for this order, ruling out "the notifier itself
    // hangs" (see tests/orderController.test.ts, which shows the notifier
    // rejects promptly on its own) as an alternative explanation.
    expect(warehouseNotifier.getLastNotifyOutcome()).toMatchObject({
      warehouseId: 'wh-offline-1',
      result: 'rejected',
    });
  });
});
