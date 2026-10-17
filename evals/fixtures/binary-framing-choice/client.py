"""Payment client used by the checkout worker."""
import logging
import time

import gateway

log = logging.getLogger(__name__)


class ChargeFailed(Exception):
    pass


def with_retry(fn, attempts: int = 3, backoff: float = 0.5):
    """Call ``fn(idempotency_key)`` up to ``attempts`` times with one key.

    The key is minted once per logical charge so every attempt is the same
    request as far as the gateway is concerned.
    """
    key = gateway.new_idempotency_key()
    for n in range(attempts):
        try:
            return fn(key)
        except gateway.GatewayError as exc:
            log.warning("charge attempt %d failed: %s", n + 1, type(exc).__name__)
            if n + 1 < attempts:
                time.sleep(backoff * (2 ** n))
    raise ChargeFailed(f"gave up after {attempts} attempts") from None


def charge(order_id: str, amount_cents: int) -> dict:
    """Charge the card on file for ``order_id`` and return the gateway receipt."""

    def attempt(key: str) -> dict:
        return gateway.post_charge(order_id, amount_cents, idempotency_key=key)

    return with_retry(attempt)
