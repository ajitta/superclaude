"""Thin wrapper over the hosted card gateway.

Transport is pluggable so the local harness and the tests can script
outcomes. The hosted gateway de-duplicates requests that carry the same
``idempotency_key`` for 24 hours and replays the original receipt; the local
stand-in below mirrors that behaviour.
"""
import uuid


class GatewayError(Exception):
    """Base class for anything the gateway can raise."""


class GatewayTimeout(GatewayError):
    """No response within the deadline. The charge may or may not have landed."""


class GatewayUnavailable(GatewayError):
    """5xx from the gateway; safe to retry."""


class GatewayDeclined(GatewayError):
    """The issuer declined the card. Retrying returns the same answer."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


# Replaced by the HTTPS transport at service start-up; tests script it.
# Signature: transport(order_id, amount_cents) -> (receipt, response_delivered)
# or raises a GatewayError before any charge is recorded.
transport = None

_ledger: dict[str, dict] = {}   # idempotency_key -> receipt
CHARGES: list[dict] = []        # every charge actually recorded by the gateway


def new_idempotency_key() -> str:
    return uuid.uuid4().hex


def post_charge(order_id: str, amount_cents: int, idempotency_key: str) -> dict:
    if idempotency_key in _ledger:
        return _ledger[idempotency_key]
    receipt, delivered = transport(order_id, amount_cents)
    _ledger[idempotency_key] = receipt
    CHARGES.append(receipt)
    if not delivered:
        # Charge recorded but the response was lost on the wire.
        raise GatewayTimeout("response lost after the charge was recorded")
    return receipt


def reset() -> None:
    _ledger.clear()
    CHARGES.clear()
