export interface Clock {
  now(): number;
}

export const systemClock: Clock = {
  now: () => Date.now(),
};

/**
 * A clock whose time only moves when told to. Lets tests exercise TTL
 * expiry deterministically instead of sleeping for real.
 */
export class ManualClock implements Clock {
  constructor(private currentMs: number = 0) {}

  now(): number {
    return this.currentMs;
  }

  advance(ms: number): void {
    this.currentMs += ms;
  }

  set(ms: number): void {
    this.currentMs = ms;
  }
}

interface CacheEntry {
  value: number;
  expiresAt: number;
}

/**
 * Simple in-memory TTL cache keyed by string, storing numeric prices. Takes
 * an injectable clock (defaulting to the real system clock) so callers and
 * tests can control what "now" means.
 */
export class PriceCache {
  private readonly store: Map<string, CacheEntry> = new Map();

  constructor(private readonly clock: Clock = systemClock) {}

  get(key: string): number | undefined {
    const entry = this.store.get(key);
    if (!entry) {
      return undefined;
    }
    if (entry.expiresAt <= this.clock.now()) {
      this.store.delete(key);
      return undefined;
    }
    return entry.value;
  }

  set(key: string, value: number, ttlMs: number): void {
    this.store.set(key, { value, expiresAt: this.clock.now() + ttlMs });
  }

  /** Test/dev helper: not used by request handlers. */
  clear(): void {
    this.store.clear();
  }
}

/** Default cache instance used by the app. */
export const priceCache = new PriceCache();
