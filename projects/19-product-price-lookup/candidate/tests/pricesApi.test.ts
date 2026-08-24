import request from 'supertest';
import { app } from '../src/app';
import { priceCache } from '../src/cache/priceCache';
import { pricingClient } from '../src/clients/pricingClient';
import {
  lastKnownPriceRepository,
  createSeedLastKnownPrices,
} from '../src/repositories/lastKnownPriceRepository';

beforeEach(() => {
  priceCache.clear();
  pricingClient.clearAllFailures();
  lastKnownPriceRepository.resetWith(createSeedLastKnownPrices());
});

describe('GET /health', () => {
  it('returns 200', async () => {
    const response = await request(app).get('/health');
    expect(response.status).toBe(200);
  });
});

describe('GET /products/:productId/price', () => {
  it('returns a live price and defaults currency to USD when omitted', async () => {
    const response = await request(app).get('/products/prod-1/price');

    expect(response.status).toBe(200);
    expect(response.body.currency).toBe('USD');
    expect(response.body.source).toBe('live');
    expect(typeof response.body.price).toBe('number');
  });

  it('returns a cached price on a repeated request for the same product and currency', async () => {
    const first = await request(app).get('/products/prod-1/price?currency=USD');
    const second = await request(app).get('/products/prod-1/price?currency=USD');

    expect(second.status).toBe(200);
    expect(second.body.source).toBe('cache');
    expect(second.body.price).toBe(first.body.price);
  });

  it('returns a fallback price with 200 when the pricing provider fails but a last-known price exists', async () => {
    pricingClient.configureFailure('prod-2', 'USD');

    const response = await request(app).get('/products/prod-2/price?currency=USD');

    expect(response.status).toBe(200);
    expect(response.body.source).toBe('fallback');
  });

  it('returns 503 when the pricing provider fails and there is no last-known price', async () => {
    pricingClient.configureFailure('prod-unknown', 'USD');

    const response = await request(app).get('/products/prod-unknown/price?currency=USD');

    expect(response.status).toBe(503);
  });

  it('shows the correct live EUR price after a USD price was already cached for the same product', async () => {
    // Reproduces the customer-facing report: switching the storefront's
    // display currency from USD to EUR must never show the exact same
    // number that was showing for USD.
    const usdResponse = await request(app).get('/products/prod-1/price?currency=USD');
    const eurResponse = await request(app).get('/products/prod-1/price?currency=EUR');

    expect(eurResponse.status).toBe(200);
    expect(eurResponse.body.source).toBe('live');
    expect(eurResponse.body.price).not.toBe(usdResponse.body.price);
  });
});
