import { Listing } from '../types';

/**
 * A simple in-memory cache of the full listings array, used by
 * `GET /listings` to avoid recomputing the list on every request. It holds
 * one snapshot at a time and has no logic of its own about *when* that
 * snapshot should be considered stale — that's entirely the caller's
 * responsibility.
 */
export class ListingsCache {
  private cached: Listing[] | undefined;

  /** The cached snapshot, or `undefined` if nothing is currently cached. */
  get(): Listing[] | undefined {
    return this.cached;
  }

  /** Replaces the cached snapshot. */
  set(listings: Listing[]): void {
    this.cached = listings;
  }

  /** Clears the cached snapshot, so the next `get()` returns `undefined`. */
  invalidate(): void {
    this.cached = undefined;
  }
}

/** Default cache instance used by the app. */
export const listingsCache = new ListingsCache();
