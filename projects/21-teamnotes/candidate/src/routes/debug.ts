import { Router } from 'express';
import { noteRepository, createSeedNotes } from '../repositories/noteRepository';

const router = Router();

/**
 * Testing utility: resets the in-memory note store back to its seeded
 * starting state. Not part of the "real" product surface.
 */
router.post('/debug/reset', (_req, res) => {
  noteRepository.reset(createSeedNotes());
  res.status(200).json({ status: 'reset' });
});

export default router;
