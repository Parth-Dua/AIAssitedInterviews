export interface OrderItem {
  sku: string;
  quantity: number;
}

export type OrderStatus = 'created';

export interface Order {
  id: string;
  customerId: string;
  warehouseId: string;
  items: OrderItem[];
  status: OrderStatus;
  createdAt: string;
}

/** Shape accepted by POST /orders. */
export interface OrderCreateInput {
  customerId: string;
  warehouseId: string;
  items: OrderItem[];
}
