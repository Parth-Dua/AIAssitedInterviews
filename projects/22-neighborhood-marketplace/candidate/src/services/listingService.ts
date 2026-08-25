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

/**
 * Business logic for reading and mutating marketplace listings. Sits
 * between the controllers (HTTP concerns) and the repository (storage
 * concerns), and owns the list cache used by `getListings`.
 */
export class ListingService {
  constructor(private readonly repository: ListingRepository, private readonly cache: ListingsCache) {}

  getListings(): Listing[] {
    const cached = this.cache.get();
    if (cached) {
      return cached;
    }
    const fresh = this.repository.getAll();
    this.cache.set(fresh);
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
    return updated;
  }
}
