import { Router } from 'express';
import { listingRepository, createSeedListings, appClock } from '../repositories/listingRepository';
import { listingsCache } from '../cache/listingsCache';

const router = Router();

/**
 * Testing utility: resets the in-memory listing store back to its seeded
 * starting state and clears the debug time offset. Not part of the "real"
 * product surface.
 */
router.post('/debug/reset', (_req, res) => {
  listingRepository.reset(createSeedListings());
  listingsCache.invalidate();
  appClock.reset();
  res.status(200).json({ status: 'reset' });
});

/**
 * Testing utility: advances the app's shared clock by `advanceByMs`, so
 * time-based behavior (like a reservation expiring) can be explored
 * deterministically without waiting in real time. Not part of the "real"
 * product surface.
 */
router.post('/debug/advance-time', (req, res) => {
  const { advanceByMs } = req.body ?? {};

  if (typeof advanceByMs !== 'number' || !Number.isFinite(advanceByMs) || advanceByMs < 0) {
    res.status(400).json({ error: 'advanceByMs must be a non-negative number' });
    return;
  }

  appClock.advance(advanceByMs);
  res.status(200).json({ status: 'advanced', advanceByMs });
});

export default router;
