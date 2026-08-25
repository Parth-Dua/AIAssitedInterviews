/**
 * Hidden tests. Copy this file into candidate/tests/ (it is not present in
 * the candidate repo) and run `npm test` from candidate/ after applying a
 * candidate's fix, or after applying reference_solution/ to validate the
 * answer key.
 */
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

describe('GET /listings reflects a lazily-expired reservation with no further explicit action', () => {
  it('shows the listing as available in the list once its reservation lapses, purely from the passage of time', async () => {
    const list = await request(app).get('/listings');
    const target = list.body[0];

    await request(app).post(`/listings/${target.id}/reserve`);

    const afterReserve = await request(app).get('/listings');
    expect(afterReserve.body.find((l: { id: string }) => l.id === target.id).status).toBe('reserved');

    // Advance the deterministic debug clock, not real wall-clock time, past
    // the reservation window. Zero real time elapses during this test.
    await request(app).post('/debug/advance-time').send({ advanceByMs: RESERVATION_WINDOW_MS });

    // The individual detail view reads live and already correctly shows
    // the expiry (this is the given, correct lazy-expiry mechanism).
    const detail = await request(app).get(`/listings/${target.id}`);
    expect(detail.body.status).toBe('available');

    // The list view must reflect the same truth, without any further
    // explicit reserve/purchase/create action having happened anywhere.
    const after = await request(app).get('/listings');
    const inList = after.body.find((l: { id: string }) => l.id === target.id);
    expect(inList.status).toBe('available');
    expect(inList.reservedUntil).toBeNull();

    // Calling it again should be stably correct too, not a one-off fluke.
    const again = await request(app).get('/listings');
    expect(again.body.find((l: { id: string }) => l.id === target.id).status).toBe('available');
  });

  it('reflects the expiry in the list even when nobody ever opened the individual detail view first', async () => {
    const list = await request(app).get('/listings');
    const target = list.body[0];

    await request(app).post(`/listings/${target.id}/reserve`);
    // Populate the list cache while the reservation is still active.
    await request(app).get('/listings');

    await request(app).post('/debug/advance-time').send({ advanceByMs: RESERVATION_WINDOW_MS });

    // Go straight back to the list — never touch GET /listings/:id at all.
    const after = await request(app).get('/listings');
    const inList = after.body.find((l: { id: string }) => l.id === target.id);
    expect(inList.status).toBe('available');
  });
});

describe('multiple listings where only one reservation has expired', () => {
  it('updates only the expired listing in the list, leaving the still-active reservation untouched', async () => {
    const list = await request(app).get('/listings');
    const [first, second] = list.body;

    // Reserve the first listing, then move time forward part-way through
    // its window before reserving the second — so their expiries land at
    // different absolute times.
    await request(app).post(`/listings/${first.id}/reserve`);
    await request(app).post('/debug/advance-time').send({ advanceByMs: 200000 });
    await request(app).post(`/listings/${second.id}/reserve`);

    // Populate the cache with both still reserved.
    const midway = await request(app).get('/listings');
    expect(midway.body.find((l: { id: string }) => l.id === first.id).status).toBe('reserved');
    expect(midway.body.find((l: { id: string }) => l.id === second.id).status).toBe('reserved');

    // Advance far enough that only the first listing's window has fully
    // elapsed; the second's has not.
    await request(app).post('/debug/advance-time').send({ advanceByMs: 150000 });

    const after = await request(app).get('/listings');
    const firstAfter = after.body.find((l: { id: string }) => l.id === first.id);
    const secondAfter = after.body.find((l: { id: string }) => l.id === second.id);

    expect(firstAfter.status).toBe('available');
    expect(firstAfter.reservedUntil).toBeNull();
    expect(secondAfter.status).toBe('reserved');
    expect(secondAfter.reservedUntil).not.toBeNull();
  });
});

describe('purchasing a listing whose reservation just expired', () => {
  it('rejects the purchase as not-purchasable, and the list subsequently reflects it as available', async () => {
    const list = await request(app).get('/listings');
    const target = list.body[0];

    await request(app).post(`/listings/${target.id}/reserve`);
    await request(app).get('/listings'); // populate the cache while reserved

    await request(app).post('/debug/advance-time').send({ advanceByMs: RESERVATION_WINDOW_MS });

    // The reservation has already lapsed by the time this purchase
    // attempt reads the listing, so it must be rejected exactly as if the
    // listing had never been reserved at all — not silently "succeed" and
    // not throw an unrelated error.
    const purchaseAttempt = await request(app).post(`/listings/${target.id}/purchase`);
    expect(purchaseAttempt.status).toBe(409);

    const detail = await request(app).get(`/listings/${target.id}`);
    expect(detail.body.status).toBe('available');

    const after = await request(app).get('/listings');
    const inList = after.body.find((l: { id: string }) => l.id === target.id);
    expect(inList.status).toBe('available');
  });
});

describe('sanity: a fresh reservation still appears correctly in the list immediately', () => {
  it('is not broken by whatever fixes the expiry-staleness gap', async () => {
    const list = await request(app).get('/listings');
    const target = list.body[0];

    // Populate the cache first with nothing reserved.
    await request(app).get('/listings');

    const reserveResponse = await request(app).post(`/listings/${target.id}/reserve`);
    expect(reserveResponse.status).toBe(200);

    const after = await request(app).get('/listings');
    expect(after.body.find((l: { id: string }) => l.id === target.id).status).toBe('reserved');
  });
});
