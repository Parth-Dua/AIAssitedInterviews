from app.models.schemas import Order


class OrderRepository:
    """In-memory store of orders. In production this would be backed by a
    database table owned by the orders service.
    """

    def __init__(self):
        self._orders: dict[int, Order] = {
            101: Order(id=101, status="pending", amount_paid_cents=0),
            102: Order(id=102, status="pending", amount_paid_cents=0),
            103: Order(id=103, status="pending", amount_paid_cents=0),
        }

    def get(self, order_id: int) -> Order | None:
        return self._orders.get(order_id)

    def save(self, order: Order) -> None:
        self._orders[order.id] = order
