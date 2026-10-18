"""Payrail API client."""


class Payrail:
    def __init__(self, api_key: str, base_url: str = "https://api.payrail.example/v3"):
        self.api_key = api_key
        self.base_url = base_url

    def create_charge(self, amount: int, currency: str, source: str) -> dict:
        """Create a charge of `amount` (an integer) in `currency` on `source`."""
        raise NotImplementedError("network calls are disabled in this checkout")

    def refund(self, charge_id: str, amount: int | None = None) -> dict:
        """Refund a charge in full, or `amount` of it."""
        raise NotImplementedError("network calls are disabled in this checkout")
