class PricingRepository:
    """In-memory store of active promotional discount codes.

    Maps a discount code to a percent-off value (0-100). In production this
    would be backed by a database table maintained by the marketing team.
    """

    def __init__(self):
        self._codes = {
            "WELCOME10": 10,
            "SAVE20": 20,
            "VIP30": 30,
        }

    def get_discount_percent(self, code: str) -> int | None:
        return self._codes.get(code.upper())
