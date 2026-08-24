import { Router } from 'express';
import { createOrder } from '../controllers/orderController';
import { validateOrderCreate } from '../middleware/validateOrderCreate';

const router = Router();

router.post('/orders', validateOrderCreate, createOrder);

export default router;
