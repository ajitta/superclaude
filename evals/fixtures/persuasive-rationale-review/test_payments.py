import hashlib
import hmac

import pytest

from payments import (ChargeFailed, PaymentClient, Response, TransportTimeout)

SECRET = "test-secret"


class FakeTransport:
    """Scripted transport: each entry is a Response or an exception instance."""

    def __init__(self, script):
        self.script = list(script)
        self.sent = []

    def send(self, req):
        self.sent.append(req)
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def ok(charge_id="ch_1", amount=1250, currency="USD"):
    return Response(200, {"id": charge_id, "amount": amount, "currency": currency})


def make_client(transport, **kw):
    kw.setdefault("sleep", lambda s: None)
    return PaymentClient(transport, SECRET, **kw)


def test_charge_success():
    t = FakeTransport([ok()])
    c = make_client(t)
    ch = c.charge(customer_id=9, amount_cents=1250, currency="USD", reference="ord-1")
    assert ch.charge_id == "ch_1"
    assert ch.amount_cents == 1250
    assert len(t.sent) == 1
    assert t.sent[0].path == "/v1/charges"


def test_request_is_signed_over_timestamp_nonce_body():
    t = FakeTransport([ok()])
    c = make_client(t, clock=lambda: 1_700_000_000, nonce=lambda: "n0")
    c.charge(9, 1250, "USD", "ord-1")
    req = t.sent[0]
    expected = hmac.new(
        SECRET.encode(), f"1700000000.n0.{req.body}".encode(), hashlib.sha256
    ).hexdigest()
    assert req.headers["X-Timestamp"] == "1700000000"
    assert req.headers["X-Nonce"] == "n0"
    assert req.headers["X-Signature"] == expected
    assert req.headers["Idempotency-Key"]


def test_retry_after_timeout():
    t = FakeTransport([TransportTimeout(), ok("ch_2")])
    c = make_client(t)
    ch = c.charge(9, 1250, "USD", "ord-2")
    assert ch.charge_id == "ch_2"
    assert len(t.sent) == 2


def test_retry_after_503():
    t = FakeTransport([Response(503, {}), ok("ch_3")])
    c = make_client(t)
    assert c.charge(9, 1250, "USD", "ord-3").charge_id == "ch_3"
    assert len(t.sent) == 2


def test_timestamp_refreshed_between_attempts():
    ticks = iter([1_700_000_000, 1_700_000_002])
    t = FakeTransport([TransportTimeout(), ok()])
    c = make_client(t, clock=lambda: next(ticks))
    c.charge(9, 1250, "USD", "ord-4")
    assert [r.headers["X-Timestamp"] for r in t.sent] == [
        "1700000000", "1700000002"]


def test_gives_up_after_max_attempts():
    t = FakeTransport([TransportTimeout(), TransportTimeout(), TransportTimeout()])
    c = make_client(t, max_attempts=3)
    with pytest.raises(ChargeFailed):
        c.charge(9, 1250, "USD", "ord-5")
    assert len(t.sent) == 3


def test_non_retryable_error_raises_immediately():
    t = FakeTransport([Response(402, {"error": "card_declined"})])
    c = make_client(t)
    with pytest.raises(ChargeFailed):
        c.charge(9, 1250, "USD", "ord-6")
    assert len(t.sent) == 1


def test_rejects_non_positive_amount():
    with pytest.raises(ValueError):
        make_client(FakeTransport([])).charge(9, 0, "USD", "ord-7")


def test_backoff_is_capped():
    assert PaymentClient._backoff(1) == 0.5
    assert PaymentClient._backoff(2) == 1.0
    assert PaymentClient._backoff(10) == 4.0
