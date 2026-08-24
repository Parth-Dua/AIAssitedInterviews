import { Router } from 'express';
import { getProductPrice } from '../controllers/priceController';

const router = Router();

router.get('/products/:productId/price', getProductPrice);

export default router;
