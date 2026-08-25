import request from 'supertest';
import { app } from '../src/app';
import { listingRepository, createSeedListings, appClock } from '../src/repositories/listingRepository';
import { listingsCache } from '../src/cache/listingsCache';
import { RESERVATION_WINDOW_MS } from '../src/services/listingService';

beforeEach(() => {
  listingRepository.reset(createSeedListings());
  listingsCache.invalidate();
  appClock.reset();
});

describe('GET /health', () => {
  it('returns 200', async () => {
    const response = await request(app).get('/health');
    expect(response.status).toBe(200);
  });
});

describe('POST /listings', () => {
  it('creates a listing as available and it appears in GET /listings', async () => {
    const response = await request(app).post('/listings').send({ title: 'Patio chairs', price: 15 });

    expect(response.status).toBe(201);
    expect(response.body.title).toBe('Patio chairs');
    expect(response.body.status).toBe('available');

    const list = await request(app).get('/listings');
    expect(list.body.some((l: { id: string }) => l.id === response.body.id)).toBe(true);
  });

  it('rejects a listing with a missing title', async () => {
    const response = await request(app).post('/listings').send({ price: 10 });
    expect(response.status).toBe(400);
  });

  it('rejects a listing with an invalid price', async () => {
    const response = await request(app).post('/listings').send({ title: 'Bad price', price: -5 });
    expect(response.status).toBe(400);
  });
});

describe('GET /listings', () => {
  it('lists all seeded listings', async () => {
    const response = await request(app).get('/listings');

    expect(response.status).toBe(200);
    expect(Array.isArray(response.body)).toBe(true);
    expect(response.body.length).toBe(4);
  });
});

describe('GET /listings/:id', () => {
  it('returns the full listing', async () => {
    const list = await request(app).get('/listings');
    const target = list.body[0];

    const response = await request(app).get(`/listings/${target.id}`);

    expect(response.status).toBe(200);
    expect(response.body.id).toBe(target.id);
    expect(response.body).toHaveProperty('status');
  });

  it('returns 404 for an unknown listing', async () => {
    const response = await request(app).get('/listings/does-not-exist');
    expect(response.status).toBe(404);
  });
});

describe('POST /listings/:id/reserve', () => {
  it('reserves an available listing and the list immediately reflects it', async () => {
    const list = await request(app).get('/listings');
    const target = list.body[0];

    const response = await request(app).post(`/listings/${target.id}/reserve`);
    expect(response.status).toBe(200);
    expect(response.body.status).toBe('reserved');

    const after = await request(app).get('/listings');
    const inList = after.body.find((l: { id: string }) => l.id === target.id);
    expect(inList.status).toBe('reserved');
  });

  it('rejects reserving a listing that is already reserved', async () => {
    const list = await request(app).get('/listings');
    const target = list.body[0];

    await request(app).post(`/listings/${target.id}/reserve`);
    const response = await request(app).post(`/listings/${target.id}/reserve`);

    expect(response.status).toBe(409);
  });
});

describe('POST /listings/:id/purchase', () => {
  it('finalizes a reserved listing as sold, reflected in both detail and list views', async () => {
    const list = await request(app).get('/listings');
    const target = list.body[0];

    await request(app).post(`/listings/${target.id}/reserve`);
    const response = await request(app).post(`/listings/${target.id}/purchase`);

    expect(response.status).toBe(200);
    expect(response.body.status).toBe('sold');

    const detail = await request(app).get(`/listings/${target.id}`);
    expect(detail.body.status).toBe('sold');

    const after = await request(app).get('/listings');
    const inList = after.body.find((l: { id: string }) => l.id === target.id);
    expect(inList.status).toBe('sold');
  });

  it('rejects purchasing a listing that was never reserved', async () => {
    const list = await request(app).get('/listings');
    const target = list.body[0];

    const response = await request(app).post(`/listings/${target.id}/purchase`);
    expect(response.status).toBe(409);
  });
});

describe('reservation expiry on a direct read', () => {
  it('GET /listings/:id shows available immediately once the debug clock passes the reservation window', async () => {
    const list = await request(app).get('/listings');
    const target = list.body[0];

    await request(app).post(`/listings/${target.id}/reserve`);

    await request(app)
      .post('/debug/advance-time')
      .send({ advanceByMs: RESERVATION_WINDOW_MS });

    const detail = await request(app).get(`/listings/${target.id}`);
    expect(detail.status).toBe(200);
    expect(detail.body.status).toBe('available');
    expect(detail.body.reservedUntil).toBeNull();
  });
});

describe('POST /debug/advance-time', () => {
  it('accepts a non-negative advance amount', async () => {
    const response = await request(app).post('/debug/advance-time').send({ advanceByMs: 1000 });
    expect(response.status).toBe(200);
  });

  it('rejects a negative or missing advance amount', async () => {
    const negative = await request(app).post('/debug/advance-time').send({ advanceByMs: -5 });
    expect(negative.status).toBe(400);

    const missing = await request(app).post('/debug/advance-time').send({});
    expect(missing.status).toBe(400);
  });
});

describe('POST /debug/reset', () => {
  it('restores the seeded starting state', async () => {
    await request(app).post('/listings').send({ title: 'Temporary listing', price: 5 });

    const beforeReset = await request(app).get('/listings');
    expect(beforeReset.body.length).toBe(5);

    const resetResponse = await request(app).post('/debug/reset');
    expect(resetResponse.status).toBe(200);

    const afterReset = await request(app).get('/listings');
    expect(afterReset.body.length).toBe(4);
    expect(afterReset.body.every((l: { status: string }) => l.status === 'available')).toBe(true);
  });
});
