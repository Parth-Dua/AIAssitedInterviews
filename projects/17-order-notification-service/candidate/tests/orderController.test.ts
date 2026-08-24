import { orderService } from '../src/services/orderService';
import { orderRepository } from '../src/repositories/orderRepository';
import { warehouseNotifier, WarehouseUnavailableError } from '../src/services/warehouseNotifier';

beforeEach(() => {
  orderRepository.clear();
  warehouseNotifier.resetLastNotifyOutcome();
});

describe('OrderService.createOrder', () => {
  it('creates an order with status "created" and the given fields', () => {
    const order = orderService.createOrder({
      customerId: 'cust-1',
      warehouseId: 'wh-1',
      items: [{ sku: 'sku-1', quantity: 3 }],
    });

    expect(order.status).toBe('created');
    expect(order.customerId).toBe('cust-1');
    expect(order.warehouseId).toBe('wh-1');
    expect(order.items).toEqual([{ sku: 'sku-1', quantity: 3 }]);
    expect(order.id).toEqual(expect.any(String));
    expect(order.createdAt).toEqual(expect.any(String));
  });

  it('generates a unique id for each order', () => {
    const a = orderService.createOrder({
      customerId: 'cust-1',
      warehouseId: 'wh-1',
      items: [{ sku: 'sku-1', quantity: 1 }],
    });
    const b = orderService.createOrder({
      customerId: 'cust-2',
      warehouseId: 'wh-1',
      items: [{ sku: 'sku-1', quantity: 1 }],
    });

    expect(a.id).not.toBe(b.id);
  });
});

describe('warehouseNotifier.notify — tested in isolation from the API', () => {
  // These tests call the notifier directly, with no Express/HTTP involved.
  // They establish independently whether the notifier itself resolves and
  // rejects promptly and correctly for a given warehouse id — useful
  // evidence when narrowing down where an order-placement problem
  // actually lives.

  it('resolves for a reachable warehouse', async () => {
    const order = orderService.createOrder({
      customerId: 'cust-1',
      warehouseId: 'wh-1',
      items: [{ sku: 'sku-1', quantity: 1 }],
    });

    await expect(warehouseNotifier.notify(order)).resolves.toBeUndefined();
    expect(warehouseNotifier.getLastNotifyOutcome()).toMatchObject({
      warehouseId: 'wh-1',
      result: 'resolved',
    });
  });

  it('rejects with WarehouseUnavailableError for an offline warehouse', async () => {
    const order = orderService.createOrder({
      customerId: 'cust-1',
      warehouseId: 'wh-offline-1',
      items: [{ sku: 'sku-1', quantity: 1 }],
    });

    await expect(warehouseNotifier.notify(order)).rejects.toBeInstanceOf(
      WarehouseUnavailableError
    );
    expect(warehouseNotifier.getLastNotifyOutcome()).toMatchObject({
      warehouseId: 'wh-offline-1',
      result: 'rejected',
    });
  });
});
