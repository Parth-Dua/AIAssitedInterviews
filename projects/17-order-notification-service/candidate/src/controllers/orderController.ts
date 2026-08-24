import { Request, Response } from 'express';
import { orderService } from '../services/orderService';
import { warehouseNotifier } from '../services/warehouseNotifier';

export async function createOrder(req: Request, res: Response) {
  const order = orderService.createOrder(req.body);
  await warehouseNotifier.notify(order);
  res.status(201).json(order);
}
