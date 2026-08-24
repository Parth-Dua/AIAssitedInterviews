import { Order } from '../types';

/**
 * In-memory store of orders, keyed by order id. In production this would be
 * backed by a real database table; for this exercise a Map is enough.
 */
export class OrderRepository {
  private readonly ordersById: Map<string, Order> = new Map();

  getById(id: string): Order | undefined {
    return this.ordersById.get(id);
  }

  list(): Order[] {
    return Array.from(this.ordersById.values());
  }

  save(order: Order): Order {
    this.ordersById.set(order.id, order);
    return order;
  }

  /** Test/dev helper: not used by request handlers. */
  clear(): void {
    this.ordersById.clear();
  }
}

/** Default repository instance used by the app. Starts empty — orders are
 * created through the API, there is no seed data for this service. */
export const orderRepository = new OrderRepository();
