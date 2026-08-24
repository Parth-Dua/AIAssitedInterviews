export type PriceSource = 'live' | 'cache' | 'fallback';

export interface PriceResult {
  price: number;
  source: PriceSource;
}

/** Shape returned by GET /products/:productId/price. */
export interface PriceResponse {
  productId: string;
  currency: string;
  price: number;
  source: PriceSource;
}
