import { Request, Response } from 'express';
import { PriceService, PriceUnavailableError } from '../services/priceService';
import { priceCache } from '../cache/priceCache';
import { pricingClient } from '../clients/pricingClient';
import { lastKnownPriceRepository } from '../repositories/lastKnownPriceRepository';

const DEFAULT_CURRENCY = 'USD';

const priceService = new PriceService(priceCache, pricingClient, lastKnownPriceRepository);

export async function getProductPrice(req: Request, res: Response): Promise<void> {
  const { productId } = req.params;
  const rawCurrency = req.query.currency;
  const currency =
    typeof rawCurrency === 'string' && rawCurrency.trim().length > 0
      ? rawCurrency.trim().toUpperCase()
      : DEFAULT_CURRENCY;

  try {
    const result = await priceService.getPrice(productId, currency);
    res.status(200).json({
      productId,
      currency,
      price: result.price,
      source: result.source,
    });
  } catch (err) {
    if (err instanceof PriceUnavailableError) {
      res.status(503).json({ error: err.message });
      return;
    }
    throw err;
  }
}
