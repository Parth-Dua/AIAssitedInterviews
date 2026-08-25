import { Listing } from '../types';
import { ClockFn, createOffsetClock } from '../clock';

/**
 * In-memory store of marketplace listings, keyed by id. In production this
 * would be backed by a real database table; for this exercise a Map is
 * enough.
 *
 * A reservation automatically lapses once its `reservedUntil` clock value
 * has passed. Rather than running a background timer, expiry is applied
 * lazily: the moment a listing is read (individually via `getById`, or as
 * part of a full scan via `getAll`) and found to be past its reservation
 * window, it's flipped back to `available` right then and the change is
 * persisted before the (now-corrected) listing is returned. This is a
 * common, legitimate pattern for time-based state in a simple store — no
 * separate expiry process to schedule, crash-recover, or keep in sync.
 */
export class ListingRepository {
  private readonly listingsById: Map<string, Listing> = new Map();
  private readonly clock: ClockFn;

  constructor(clock: ClockFn = () => Date.now(), seed: Listing[] = []) {
    this.clock = clock;
    for (const listing of seed) {
      this.listingsById.set(listing.id, listing);
    }
  }

  /** The repository's current time, per its injectable clock. */
  now(): number {
    return this.clock();
  }

  private applyExpiry(listing: Listing): Listing {
    if (listing.status === 'reserved' && listing.reservedUntil !== null && listing.reservedUntil <= this.clock()) {
      // Build a new object rather than mutating `listing` in place: a
      // caller (e.g. the service's list cache) may be holding an earlier
      // snapshot that includes this exact object reference, and mutating
      // it in place would silently change that snapshot's contents too.
      const expired: Listing = { ...listing, status: 'available', reservedUntil: null };
      this.listingsById.set(expired.id, expired);
      return expired;
    }
    return listing;
  }

  getById(id: string): Listing | undefined {
    const listing = this.listingsById.get(id);
    if (!listing) {
      return undefined;
    }
    return this.applyExpiry(listing);
  }

  getAll(): Listing[] {
    return Array.from(this.listingsById.values()).map((listing) => this.applyExpiry(listing));
  }

  save(listing: Listing): Listing {
    this.listingsById.set(listing.id, listing);
    return listing;
  }

  /** Test/dev helper: replace all stored listings with the given seed set. */
  reset(seed: Listing[]): void {
    this.listingsById.clear();
    for (const listing of seed) {
      this.listingsById.set(listing.id, listing);
    }
  }
}

let nextSeedId = 1;
function seedListing(title: string, price: number): Listing {
  const id = `listing-${nextSeedId++}`;
  return { id, title, price, status: 'available', reservedUntil: null };
}

export function createSeedListings(): Listing[] {
  nextSeedId = 1;
  return [
    seedListing('Wooden bookshelf', 25),
    seedListing('Kids bike, 16-inch', 40),
    seedListing('Box of gardening tools', 0),
    seedListing('Standing desk', 60),
  ];
}

/** The app's shared clock: real time plus a debug-controlled offset, so
 * `/debug/advance-time` can fast-forward the whole app deterministically. */
export const appClock = createOffsetClock();

/** Default repository instance used by the app, seeded with sample data. */
export const listingRepository = new ListingRepository(appClock.now, createSeedListings());
