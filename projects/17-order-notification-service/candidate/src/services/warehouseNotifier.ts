import { Order } from '../types';

/**
 * Raised when the (simulated) warehouse system cannot be reached for a
 * given warehouse id.
 */
export class WarehouseUnavailableError extends Error {
  constructor(public readonly warehouseId: string) {
    super(`Warehouse system unreachable for warehouse "${warehouseId}"`);
    this.name = 'WarehouseUnavailableError';
  }
}

/**
 * Fake client for the external warehouse-notification system. Stands in
 * for a real HTTP call to a warehouse-management service — no actual
 * network I/O happens here, and nothing in this module uses timers, so
 * every call settles on the next microtask.
 *
 * A fixed set of warehouse ids are simulated as "offline"; notifying one
 * of them rejects, exactly like a real HTTP client would reject on a
 * connection failure or a 5xx response from the warehouse system.
 */
const OFFLINE_WAREHOUSE_IDS = new Set(['wh-offline-1', 'wh-offline-2']);

export interface NotifyOutcome {
  orderId: string;
  warehouseId: string;
  result: 'resolved' | 'rejected';
}

let lastNotifyOutcome: NotifyOutcome | null = null;

export const warehouseNotifier = {
  /**
   * Simulates notifying the warehouse system that an order was placed.
   * Resolves for a reachable warehouse; rejects with a
   * `WarehouseUnavailableError` for a warehouse id in the simulated
   * offline set.
   */
  notify(order: Order): Promise<void> {
    const offline = OFFLINE_WAREHOUSE_IDS.has(order.warehouseId);

    lastNotifyOutcome = {
      orderId: order.id,
      warehouseId: order.warehouseId,
      result: offline ? 'rejected' : 'resolved',
    };

    if (offline) {
      return Promise.reject(new WarehouseUnavailableError(order.warehouseId));
    }

    return Promise.resolve();
  },

  /**
   * Test hook: the outcome of the most recent `notify()` call, or `null`
   * if `notify()` hasn't been called since the last reset. Lets tests
   * confirm what the notifier actually did without depending on timing.
   */
  getLastNotifyOutcome(): NotifyOutcome | null {
    return lastNotifyOutcome;
  },

  /** Test hook: clear the recorded outcome between tests. */
  resetLastNotifyOutcome(): void {
    lastNotifyOutcome = null;
  },
};
