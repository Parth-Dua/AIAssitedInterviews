export type ListingStatus = 'available' | 'reserved' | 'sold';

export interface Listing {
  id: string;
  title: string;
  price: number;
  status: ListingStatus;
  /** Clock-tick value (from the repository's injectable clock, not
   * necessarily wall-clock time) at which an active reservation lapses if
   * it isn't converted to a purchase first. `null` when the listing isn't
   * currently reserved. */
  reservedUntil: number | null;
}

/** Shape accepted by POST /listings. */
export interface ListingCreateInput {
  title: string;
  price: number;
}
