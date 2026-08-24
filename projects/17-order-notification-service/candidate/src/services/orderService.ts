import { Order, OrderCreateInput } from '../types';
import { OrderRepository, orderRepository } from '../repositories/orderRepository';

let nextGeneratedId = 1;
function generateOrderId(): string {
  return `order-${nextGeneratedId++}`;
}

/**
 * Business logic for creating orders. Sits between the controller (HTTP
 * concerns) and the repository (storage concerns). Assumes its input has
 * already passed request validation — see
 * `middleware/validateOrderCreate.ts`, which is wired in front of the
 * create-order route.
 */
export class OrderService {
  constructor(private readonly repository: OrderRepository) {}

  createOrder(input: OrderCreateInput): Order {
    const order: Order = {
      id: generateOrderId(),
      customerId: input.customerId,
      warehouseId: input.warehouseId,
      items: input.items,
      status: 'created',
      createdAt: new Date().toISOString(),
    };
    return this.repository.save(order);
  }
}

/** Default service instance used by the app. */
export const orderService = new OrderService(orderRepository);
