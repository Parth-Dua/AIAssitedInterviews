import { PriceCache } from '../cache/priceCache';
import { PricingClient } from '../clients/pricingClient';
import { LastKnownPriceRepository } from '../repositories/lastKnownPriceRepository';
import { PriceResult } from '../types';

export class PriceUnavailableError extends Error {
  constructor(productId: string, currency: string) {
    super(`Price unavailable for ${productId} in ${currency}`);
    this.name = 'PriceUnavailableError';
  }
}

/** How long a fetched price stays valid in the cache before it must be refetched. */
export const PRICE_TTL_MS = 5 * 60 * 1000; // 5 minutes

/** Builds the key a fetched price is cached under. */
export function buildCacheKey(productId: string, currency: string): string {
  return `price:${productId}:${currency}`;
}

/**
 * Looks up (and caches) the current price of a product, falling back to the
 * last known price if the pricing provider is unavailable.
 */
export class PriceService {
  constructor(
    private readonly cache: PriceCache,
    private readonly pricingClient: PricingClient,
    private readonly lastKnownPriceRepository: LastKnownPriceRepository
  ) {}

  async getPrice(productId: string, currency: string): Promise<PriceResult> {
    const cacheKey = buildCacheKey(productId, currency);
    const cached = this.cache.get(cacheKey);
    if (cached !== undefined) {
      return { price: cached, source: 'cache' };
    }

    try {
      const price = await this.pricingClient.fetchPrice(productId, currency);
      this.cache.set(cacheKey, price, PRICE_TTL_MS);
      return { price, source: 'live' };
    } catch (err) {
      const lastKnown = this.lastKnownPriceRepository.get(productId, currency);
      if (lastKnown === undefined) {
        throw new PriceUnavailableError(productId, currency);
      }
      return { price: lastKnown, source: 'fallback' };
    }
  }
}
