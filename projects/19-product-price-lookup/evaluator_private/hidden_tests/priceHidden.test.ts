/**
 * Hidden tests. Copy this file into candidate/tests/ (it is not present in
 * the candidate repo) and run `npm test` from candidate/ after applying a
 * candidate's fix, or after applying reference_solution/ to validate the
 * answer key.
 */
import { PriceCache, ManualClock } from '../src/cache/priceCache';
import { PricingClient } from '../src/clients/pricingClient';
import {
  LastKnownPriceRepository,
  createSeedLastKnownPrices,
} from '../src/repositories/lastKnownPriceRepository';
import { PriceService, buildCacheKey, PRICE_TTL_MS } from '../src/services/priceService';

function makeService(clock?: ManualClock) {
  const cache = new PriceCache(clock);
  const client = new PricingClient();
  const repo = new LastKnownPriceRepository(createSeedLastKnownPrices());
  return { service: new PriceService(cache, client, repo), cache, client, repo };
}

describe('buildCacheKey — composite key collision safety', () => {
  it('does not collide when productId and currency concatenate to the same raw string', () => {
    // A naive `price:${productId}${currency}` (no delimiter) key would make
    // these two genuinely different (productId, currency) pairs collide:
    // "P1" + "2EUR" and "P12" + "EUR" both concatenate to "P12EUR". A
    // delimiter-safe key construction must keep them distinct.
    const keyA = buildCacheKey('P1', '2EUR');
    const keyB = buildCacheKey('P12', 'EUR');

    expect(keyA).not.toBe(keyB);
  });
});

describe('getPrice — end-to-end collision safety for concatenation-alike inputs', () => {
  it('does not treat ("P1","2EUR") and ("P12","EUR") as the same cache entry', async () => {
    // Black-box variant of the test above: doesn't assume the fix keeps a
    // function named `buildCacheKey` — it just observes getPrice's
    // behavior, so it still catches a delimiter-unsafe fix even if the
    // candidate inlined the key construction.
    const { service } = makeService();

    const first = await service.getPrice('P1', '2EUR');
    expect(first.source).toBe('live');

    const second = await service.getPrice('P12', 'EUR');
    // A delimiter-unsafe cache key would make both of these collide on the
    // string "price:P12EUR", so the second call would incorrectly come
    // back as a cache hit for a pair that was never actually fetched.
    expect(second.source).toBe('live');
  });
});

describe('getPrice — different products never collide in the cache', () => {
  it('a cache hit for one product never returns a different product price', async () => {
    // Sanity check that the fix doesn't overcorrect into a single
    // global cache entry shared across all products.
    const { service } = makeService();

    const a1 = await service.getPrice('prod-A', 'USD');
    const b1 = await service.getPrice('prod-B', 'USD');
    const a2 = await service.getPrice('prod-A', 'USD');
    const b2 = await service.getPrice('prod-B', 'USD');

    expect(a1.source).toBe('live');
    expect(b1.source).toBe('live');
    expect(a2.source).toBe('cache');
    expect(b2.source).toBe('cache');
    expect(a2.price).toBe(a1.price);
    expect(b2.price).toBe(b1.price);
  });
});

describe('getPrice — TTL expiry is per (product, currency)', () => {
  it('re-fetches live after the TTL elapses, independently for USD and EUR', async () => {
    const clock = new ManualClock(0);
    const { service } = makeService(clock);

    const usd1 = await service.getPrice('prod-T', 'USD');
    const eur1 = await service.getPrice('prod-T', 'EUR');
    expect(usd1.source).toBe('live');
    expect(eur1.source).toBe('live');

    // Still within TTL: both should be cache hits.
    clock.advance(PRICE_TTL_MS - 1);
    const usd2 = await service.getPrice('prod-T', 'USD');
    const eur2 = await service.getPrice('prod-T', 'EUR');
    expect(usd2.source).toBe('cache');
    expect(eur2.source).toBe('cache');

    // Past TTL for both: both should re-fetch live independently.
    clock.advance(2);
    const usd3 = await service.getPrice('prod-T', 'USD');
    const eur3 = await service.getPrice('prod-T', 'EUR');
    expect(usd3.source).toBe('live');
    expect(eur3.source).toBe('live');
  });
});

describe('getPrice — fallback path is currency-correct', () => {
  it('falls back to the EUR last-known price on a EUR failure, not the USD one', async () => {
    const { service, client, repo } = makeService();
    // Seed data (createSeedLastKnownPrices) already has both a USD and a
    // EUR last-known price for 'prod-1', and they differ.
    const usdLastKnown = repo.get('prod-1', 'USD');
    const eurLastKnown = repo.get('prod-1', 'EUR');
    expect(usdLastKnown).toBeDefined();
    expect(eurLastKnown).toBeDefined();
    expect(usdLastKnown).not.toBe(eurLastKnown);

    client.configureFailure('prod-1', 'EUR');
    const result = await service.getPrice('prod-1', 'EUR');

    expect(result.source).toBe('fallback');
    expect(result.price).toBe(eurLastKnown);
    expect(result.price).not.toBe(usdLastKnown);
  });
});
