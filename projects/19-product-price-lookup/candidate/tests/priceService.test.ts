import { PriceCache } from '../src/cache/priceCache';
import { PricingClient } from '../src/clients/pricingClient';
import {
  LastKnownPriceRepository,
  createSeedLastKnownPrices,
} from '../src/repositories/lastKnownPriceRepository';
import { PriceService, PriceUnavailableError } from '../src/services/priceService';

function makeService() {
  const cache = new PriceCache();
  const client = new PricingClient();
  const repo = new LastKnownPriceRepository(createSeedLastKnownPrices());
  return { service: new PriceService(cache, client, repo), cache, client, repo };
}

describe('PriceService.getPrice', () => {
  it('fetches a product price live on the first request', async () => {
    const { service } = makeService();
    const result = await service.getPrice('prod-1', 'USD');

    expect(result.source).toBe('live');
    expect(typeof result.price).toBe('number');
  });

  it('returns the cached price on a repeated request for the same product and currency', async () => {
    const { service } = makeService();
    const first = await service.getPrice('prod-1', 'USD');
    const second = await service.getPrice('prod-1', 'USD');

    expect(second.source).toBe('cache');
    expect(second.price).toBe(first.price);
  });

  it('falls back to the last-known price when the pricing client fails', async () => {
    const { service, client, repo } = makeService();
    client.configureFailure('prod-2', 'USD');
    const expected = repo.get('prod-2', 'USD');
    expect(expected).toBeDefined();

    const result = await service.getPrice('prod-2', 'USD');

    expect(result.source).toBe('fallback');
    expect(result.price).toBe(expected);
  });

  it('throws PriceUnavailableError when the client fails and there is no last-known price', async () => {
    const { service, client } = makeService();
    client.configureFailure('prod-unknown', 'USD');

    await expect(service.getPrice('prod-unknown', 'USD')).rejects.toThrow(
      PriceUnavailableError
    );
  });

  it('fetches a live EUR price for a product already cached in USD, instead of reusing the USD value', async () => {
    // Reproduces the support report: switching a product's displayed
    // currency from USD to EUR must never show the previous USD price.
    const { service } = makeService();
    const usd = await service.getPrice('prod-1', 'USD');
    const eur = await service.getPrice('prod-1', 'EUR');

    expect(eur.source).toBe('live');
    expect(eur.price).not.toBe(usd.price);
  });
});

describe('PricingClient.fetchPrice (direct)', () => {
  it('returns different prices for the same product in different currencies', async () => {
    const client = new PricingClient();
    const usd = await client.fetchPrice('prod-1', 'USD');
    const eur = await client.fetchPrice('prod-1', 'EUR');

    expect(usd).not.toBe(eur);
  });
});
