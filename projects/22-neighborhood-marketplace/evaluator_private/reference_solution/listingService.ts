/**
 * Reference solution. This is the only backend file that changes — the
 * repository, cache, controller, routes, and frontend are all correct as
 * shipped and untouched. Everything outside `getListings` and the small
 * `cacheValidUntil` bookkeeping added around it is identical to the
 * starting `candidate/src/services/listingService.ts`.
 */
import { Listing, ListingCreateInput } from '../types';
import { ListingRepository } from '../repositories/listingRepository';
import { ListingsCache } from '../cache/listingsCache';

export class ListingNotFoundError extends Error {
  constructor(listingId: string) {
    super(`Listing not found: ${listingId}`);
    this.name = 'ListingNotFoundError';
  }
}

export class ListingNotReservableError extends Error {
  constructor(listingId: string) {
    super(`Listing is not available to reserve: ${listingId}`);
    this.name = 'ListingNotReservableError';
  }
}

export class ListingNotPurchasableError extends Error {
  constructor(listingId: string) {
    super(`Listing is not reserved and cannot be purchased: ${listingId}`);
    this.name = 'ListingNotPurchasableError';
  }
}

/** How long a reservation holds a listing before it lapses on its own if
 * nobody converts it to a purchase. */
export const RESERVATION_WINDOW_MS = 5 * 60 * 1000;

let nextGeneratedId = 1000;
function generateListingId(): string {
  return `listing-${nextGeneratedId++}`;
}

/** Earliest `reservedUntil` among the currently-reserved listings in this
 * snapshot, or `null` if none of them are reserved. Used to bound how long
 * a cached list snapshot may be trusted before a reservation it captured
 * could have lazily expired without any explicit write ever telling the
 * cache about it. */
function earliestReservedUntil(listings: Listing[]): number | null {
  let earliest: number | null = null;
  for (const listing of listings) {
    if (listing.status === 'reserved' && listing.reservedUntil !== null) {
      if (earliest === null || listing.reservedUntil < earliest) {
        earliest = listing.reservedUntil;
      }
    }
  }
  return earliest;
}

/**
 * Business logic for reading and mutating marketplace listings. Sits
 * between the controllers (HTTP concerns) and the repository (storage
 * concerns), and owns the list cache used by `getListings`.
 */
export class ListingService {
  // How long the snapshot currently held by `cache` may be trusted: once
  // the repository's clock reaches this value, some listing captured in
  // that snapshot as 'reserved' may have lazily expired since it was
  // cached, and the snapshot must be treated as stale even though nothing
  // has explicitly invalidated it. `null` means the cached snapshot had no
  // reservations in it, so it can only go stale via an explicit
  // invalidate() call (handled by createListing/reserveListing/
  // purchaseListing below, unchanged from the starting code).
  //
  // This is what the starting code was missing: it trusted `cache.get()`
  // forever, until the next explicit reserve/purchase/create call — with
  // no way to notice that a reservation it had already cached as
  // 'reserved' silently lapsed on its own in the meantime.
  private cacheValidUntil: number | null = null;

  constructor(private readonly repository: ListingRepository, private readonly cache: ListingsCache) {}

  getListings(): Listing[] {
    const cached = this.cache.get();
    const stillFresh = cached !== undefined && (this.cacheValidUntil === null || this.repository.now() < this.cacheValidUntil);
    if (stillFresh) {
      return cached as Listing[];
    }

    const fresh = this.repository.getAll();
    this.cache.set(fresh);
    this.cacheValidUntil = earliestReservedUntil(fresh);
    return fresh;
  }

  getListing(id: string): Listing {
    const listing = this.repository.getById(id);
    if (!listing) {
      throw new ListingNotFoundError(id);
    }
    return listing;
  }

  createListing(input: ListingCreateInput): Listing {
    const listing: Listing = {
      id: generateListingId(),
      title: input.title,
      price: input.price,
      status: 'available',
      reservedUntil: null,
    };
    const saved = this.repository.save(listing);
    this.cache.invalidate();
    this.cacheValidUntil = null;
    return saved;
  }

  /** Places a soft hold on an available listing for `RESERVATION_WINDOW_MS`. */
  reserveListing(id: string): Listing {
    const listing = this.repository.getById(id);
    if (!listing || listing.status !== 'available') {
      throw new ListingNotReservableError(id);
    }

    const updated: Listing = {
      ...listing,
      status: 'reserved',
      reservedUntil: this.repository.now() + RESERVATION_WINDOW_MS,
    };
    this.repository.save(updated);
    this.cache.invalidate();
    this.cacheValidUntil = null;
    return updated;
  }

  /** Finalizes a reserved listing as sold. */
  purchaseListing(id: string): Listing {
    const listing = this.repository.getById(id);
    if (!listing || listing.status !== 'reserved') {
      throw new ListingNotPurchasableError(id);
    }

    const updated: Listing = { ...listing, status: 'sold', reservedUntil: null };
    this.repository.save(updated);
    this.cache.invalidate();
    this.cacheValidUntil = null;
    return updated;
  }
}
