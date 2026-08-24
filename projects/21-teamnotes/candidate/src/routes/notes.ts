import { Router } from 'express';
import { listNotes, getNote, createNote, addTag, updateNote } from '../controllers/noteController';

const router = Router();

router.get('/notes', listNotes);
router.get('/notes/:id', getNote);
router.post('/notes', createNote);
router.post('/notes/:id/tags', addTag);
router.put('/notes/:id', updateNote);

export default router;
