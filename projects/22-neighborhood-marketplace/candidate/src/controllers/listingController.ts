import { Request, Response } from 'express';
import {
  ListingService,
  ListingNotFoundError,
  ListingNotReservableError,
  ListingNotPurchasableError,
} from '../services/listingService';
import { listingRepository } from '../repositories/listingRepository';
import { listingsCache } from '../cache/listingsCache';

const listingService = new ListingService(listingRepository, listingsCache);

export function listListings(req: Request, res: Response): void {
  res.status(200).json(listingService.getListings());
}

export function getListing(req: Request, res: Response): void {
  const { id } = req.params;

  try {
    const listing = listingService.getListing(id);
    res.status(200).json(listing);
  } catch (err) {
    if (err instanceof ListingNotFoundError) {
      res.status(404).json({ error: err.message });
      return;
    }
    throw err;
  }
}

export function createListing(req: Request, res: Response): void {
  const { title, price } = req.body ?? {};

  if (typeof title !== 'string' || title.trim().length === 0) {
    res.status(400).json({ error: 'title is required' });
    return;
  }

  if (typeof price !== 'number' || !Number.isFinite(price) || price < 0) {
    res.status(400).json({ error: 'price must be a non-negative number' });
    return;
  }

  const listing = listingService.createListing({ title, price });
  res.status(201).json(listing);
}

export function reserveListing(req: Request, res: Response): void {
  const { id } = req.params;

  try {
    const listing = listingService.reserveListing(id);
    res.status(200).json(listing);
  } catch (err) {
    if (err instanceof ListingNotReservableError) {
      res.status(409).json({ error: err.message });
      return;
    }
    throw err;
  }
}

export function purchaseListing(req: Request, res: Response): void {
  const { id } = req.params;

  try {
    const listing = listingService.purchaseListing(id);
    res.status(200).json(listing);
  } catch (err) {
    if (err instanceof ListingNotPurchasableError) {
      res.status(409).json({ error: err.message });
      return;
    }
    throw err;
  }
}
