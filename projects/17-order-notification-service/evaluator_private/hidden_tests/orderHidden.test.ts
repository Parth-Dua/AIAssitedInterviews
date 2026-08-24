/**
 * Hidden tests. Copy this file into candidate/tests/ (it is not present in
 * the candidate repo) and run `npm test` from candidate/ after applying a
 * candidate's fix, or after applying reference_solution/ to validate the
 * answer key.
 *
 * All HTTP-level tests here race each request against a short timer so
 * that running them against an unfixed (still-hanging) submission fails
 * fast with a clear assertion instead of hanging the test run.
 */
import http from 'http';
import request from 'supertest';
import { app } from '../src/app';
import { orderRepository } from '../src/repositories/orderRepository';
import { warehouseNotifier } from '../src/services/warehouseNotifier';

jest.setTimeout(10000);

const NEVER_RESOLVED = Symbol('never-resolved');
const RACE_WINDOW_MS = 500;

let server: http.Server;

beforeAll((done) => {
  server = app.listen(0, done);
});

afterAll((done) => {
  server.closeAllConnections?.();
  server.close(done);
});

beforeEach(() => {
  orderRepository.clear();
  warehouseNotifier.resetLastNotifyOutcome();
});

async function postOrderBounded(body: unknown) {
  const pending = request(server).post('/orders').send(body as object);
  const raced = await Promise.race([
    pending,
    new Promise((resolve) => setTimeout(() => resolve(NEVER_RESOLVED), RACE_WINDOW_MS)),
  ]);
  pending.catch(() => {});
  return raced;
}

describe('POST /orders — error contract for an unreachable warehouse', () => {
  // Catches the tempting-but-incomplete fix: wrapping the handler in a
  // try/catch that responds directly (e.g. res.status(500).send('failed'))
  // instead of forwarding to next(err). That "fixes" the hang but bypasses
  // the app's real error contract, which middleware/errorHandler.ts alone
  // is supposed to define. A correct fix (forwarding to next(err), by
  // whatever mechanism) produces exactly the contract asserted here.
  it("responds with the app's real error contract, not an ad-hoc bypass response", async () => {
    const raced = await postOrderBounded({
      customerId: 'cust-1',
      warehouseId: 'wh-offline-1',
      items: [{ sku: 'sku-1', quantity: 1 }],
    });

    expect(raced).not.toBe(NEVER_RESOLVED);
    const response = raced as request.Response;

    expect(response.status).toBe(502);
    expect(response.body).toEqual({
      error: {
        code: 'WAREHOUSE_UNAVAILABLE',
        message: expect.any(String),
      },
    });
  });
});

describe('POST /orders — a second, different offline warehouse also fails cleanly', () => {
  // Generalization check: the fix must not be special-cased to the one
  // warehouse id exercised by the public failing test.
  it('produces the same proper error response for a different offline warehouse id', async () => {
    const raced = await postOrderBounded({
      customerId: 'cust-2',
      warehouseId: 'wh-offline-2',
      items: [{ sku: 'sku-1', quantity: 1 }],
    });

    expect(raced).not.toBe(NEVER_RESOLVED);
    const response = raced as request.Response;

    expect(response.status).toBe(502);
    expect(response.body.error.code).toBe('WAREHOUSE_UNAVAILABLE');
  });
});

describe('POST /orders — a failed order does not leave the service in a bad state', () => {
  it('still successfully creates the next order for a reachable warehouse', async () => {
    const first = await postOrderBounded({
      customerId: 'cust-3',
      warehouseId: 'wh-offline-1',
      items: [{ sku: 'sku-1', quantity: 1 }],
    });
    expect(first).not.toBe(NEVER_RESOLVED);
    expect((first as request.Response).status).toBe(502);

    const second = await postOrderBounded({
      customerId: 'cust-4',
      warehouseId: 'wh-1',
      items: [{ sku: 'sku-1', quantity: 1 }],
    });

    expect(second).not.toBe(NEVER_RESOLVED);
    const response = second as request.Response;
    expect(response.status).toBe(201);
    expect(response.body.customerId).toBe('cust-4');
    expect(response.body.status).toBe('created');
  });
});
