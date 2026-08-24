class FulfillmentClient:
    """Fake client standing in for the real fulfillment system. Records
    every call made to it instead of doing any real I/O, so tests can
    assert exactly how many times (and for which orders) fulfillment was
    triggered.
    """

    def __init__(self):
        self.calls: list[int] = []

    def fulfill(self, order_id: int) -> None:
        self.calls.append(order_id)

    def call_count_for_order(self, order_id: int) -> int:
        return sum(1 for call in self.calls if call == order_id)
