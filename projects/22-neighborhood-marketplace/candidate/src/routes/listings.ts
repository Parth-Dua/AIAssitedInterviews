import { Router } from 'express';
import { listListings, getListing, createListing, reserveListing, purchaseListing } from '../controllers/listingController';

const router = Router();

router.get('/listings', listListings);
router.get('/listings/:id', getListing);
router.post('/listings', createListing);
router.post('/listings/:id/reserve', reserveListing);
router.post('/listings/:id/purchase', purchaseListing);

export default router;
