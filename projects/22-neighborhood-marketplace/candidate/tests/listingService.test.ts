import { ListingRepository, createSeedListings } from '../src/repositories/listingRepository';
import { ListingsCache } from '../src/cache/listingsCache';
import {
  ListingService,
  ListingNotFoundError,
  ListingNotReservableError,
  ListingNotPurchasableError,
  RESERVATION_WINDOW_MS,
} from '../src/services/listingService';
import { createOffsetClock } from '../src/clock';

/**
 * Every test in this file uses a fully fake clock (fixed base, advanced
 * only by explicit `advance()` calls) rather than real wall-clock time, so
 * time-based behavior is deterministic and instant to test.
 */
function makeService() {
  const clock = createOffsetClock(() => 0);
  const repository = new ListingRepository(clock.now, createSeedListings());
  const cache = new ListingsCache();
  const service = new ListingService(repository, cache);
  return { service, clock, repository, cache };
}

describe('ListingService.createListing', () => {
  it('creates a listing as available and includes it in the listings', () => {
    const { service } = makeService();
    const listing = service.createListing({ title: 'Patio chairs', price: 15 });

    expect(listing.status).toBe('available');
    expect(listing.reservedUntil).toBeNull();

    const all = service.getListings();
    expect(all.some((l) => l.id === listing.id)).toBe(true);
  });
});

describe('ListingService.getListing', () => {
  it('returns the correct listing by id', () => {
    const { service } = makeService();
    const target = service.getListings()[0];

    const fetched = service.getListing(target.id);
    expect(fetched).toEqual(target);
  });

  it('throws ListingNotFoundError for an unknown id', () => {
    const { service } = makeService();
    expect(() => service.getListing('does-not-exist')).toThrow(ListingNotFoundError);
  });
});

describe('ListingService.getListings', () => {
  it('returns all seeded listings', () => {
    const { service } = makeService();
    expect(service.getListings().length).toBe(4);
  });
});

describe('ListingService.reserveListing', () => {
  it('reserves an available listing and the list immediately reflects it', () => {
    const { service } = makeService();
    const target = service.getListings()[0];

    const reserved = service.reserveListing(target.id);
    expect(reserved.status).toBe('reserved');
    expect(reserved.reservedUntil).not.toBeNull();

    const all = service.getListings();
    const inList = all.find((l) => l.id === target.id);
    expect(inList?.status).toBe('reserved');
  });

  it('rejects reserving a listing that is already reserved', () => {
    const { service } = makeService();
    const target = service.getListings()[0];

    service.reserveListing(target.id);
    expect(() => service.reserveListing(target.id)).toThrow(ListingNotReservableError);
  });

  it('throws ListingNotReservableError for an unknown id', () => {
    const { service } = makeService();
    expect(() => service.reserveListing('does-not-exist')).toThrow(ListingNotReservableError);
  });
});

describe('ListingService.purchaseListing', () => {
  it('finalizes a reserved listing as sold, reflected in both single and list views', () => {
    const { service } = makeService();
    const target = service.getListings()[0];

    service.reserveListing(target.id);
    const purchased = service.purchaseListing(target.id);

    expect(purchased.status).toBe('sold');
    expect(service.getListing(target.id).status).toBe('sold');

    const all = service.getListings();
    expect(all.find((l) => l.id === target.id)?.status).toBe('sold');
  });

  it('rejects purchasing a listing that was never reserved', () => {
    const { service } = makeService();
    const target = service.getListings()[0];

    expect(() => service.purchaseListing(target.id)).toThrow(ListingNotPurchasableError);
  });
});

describe('reservation expiry on a direct read', () => {
  it('shows a listing as available immediately once the clock passes its reservation window', () => {
    const { service, clock } = makeService();
    const target = service.getListings()[0];

    service.reserveListing(target.id);
    expect(service.getListing(target.id).status).toBe('reserved');

    clock.advance(RESERVATION_WINDOW_MS);

    const afterExpiry = service.getListing(target.id);
    expect(afterExpiry.status).toBe('available');
    expect(afterExpiry.reservedUntil).toBeNull();
  });
});
