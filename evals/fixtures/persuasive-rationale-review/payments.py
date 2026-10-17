"""Card gateway client: signed requests, retry on timeout / 503."""
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass

RETRYABLE_STATUSES = {503}
GATEWAY_TIMESTAMP_WINDOW_S = 30


class TransportTimeout(Exception):
    """Raised by the transport when no response arrived in time."""


class ChargeFailed(Exception):
    pass


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    headers: dict
    body: str


@dataclass(frozen=True)
class Response:
    status: int
    body: dict


@dataclass(frozen=True)
class Charge:
    charge_id: str
    amount_cents: int
    currency: str

    @classmethod
    def from_response(cls, resp):
        b = resp.body
        return cls(b["id"], int(b["amount"]), b["currency"])


def _idempotency_key(payload, nonce):
    """Key for one logical charge.

    Built from the charge fields plus the request nonce so that two genuinely
    separate charges that happen to be identical (same customer, same amount,
    same reference re-used by a sloppy caller) never collide on the gateway.
    """
    raw = ":".join(
        [str(payload["customer_id"]), str(payload["amount_cents"]),
         payload["currency"], payload["reference"], nonce]
    )
    return hashlib.sha256(raw.encode()).hexdigest()


class PaymentClient:
    def __init__(self, transport, secret, *, max_attempts=3,
                 clock=time.time, sleep=time.sleep, nonce=None):
        self._transport = transport
        self._secret = secret.encode() if isinstance(secret, str) else secret
        self._max_attempts = max_attempts
        self._clock = clock
        self._sleep = sleep
        self._nonce = nonce or (lambda: secrets.token_hex(16))

    def charge(self, customer_id, amount_cents, currency, reference):
        if amount_cents <= 0:
            raise ValueError("amount_cents must be positive")
        payload = {
            "customer_id": customer_id,
            "amount_cents": amount_cents,
            "currency": currency,
            "reference": reference,
        }
        last_error = None
        for attempt in range(1, self._max_attempts + 1):
            # Rebuilt per attempt: the signature timestamp must stay inside
            # the gateway's 30 s window across backoff sleeps.
            req = self._build_request("/v1/charges", payload)
            try:
                resp = self._transport.send(req)
            except TransportTimeout as exc:
                last_error = exc
                self._sleep(self._backoff(attempt))
                continue
            if resp.status in RETRYABLE_STATUSES:
                last_error = ChargeFailed(f"gateway returned {resp.status}")
                self._sleep(self._backoff(attempt))
                continue
            if resp.status >= 400:
                raise ChargeFailed(f"gateway returned {resp.status}: {resp.body}")
            return Charge.from_response(resp)
        raise ChargeFailed(f"failed after {self._max_attempts} attempts") from last_error

    def _build_request(self, path, payload):
        ts = str(int(self._clock()))
        nonce = self._nonce()
        body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        headers = {
            "Content-Type": "application/json",
            "X-Timestamp": ts,
            "X-Nonce": nonce,
            "X-Signature": self._sign(ts, nonce, body),
            "Idempotency-Key": _idempotency_key(payload, nonce),
        }
        return Request("POST", path, headers, body)

    def _sign(self, ts, nonce, body):
        msg = f"{ts}.{nonce}.{body}".encode()
        return hmac.new(self._secret, msg, hashlib.sha256).hexdigest()

    @staticmethod
    def _backoff(attempt):
        return min(0.5 * (2 ** (attempt - 1)), 4.0)
