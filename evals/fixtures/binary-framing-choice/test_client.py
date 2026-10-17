import pytest

import client
import gateway


@pytest.fixture(autouse=True)
def _fast_and_clean(monkeypatch):
    monkeypatch.setattr(client.time, "sleep", lambda s: None)
    gateway.reset()
    yield
    gateway.transport = None


def script(*outcomes):
    """Transport that yields the given outcomes in order (exception or (receipt, delivered))."""
    queue = list(outcomes)

    def transport(order_id, amount_cents):
        out = queue.pop(0)
        if isinstance(out, Exception):
            raise out
        return out

    gateway.transport = transport


def test_success_first_try():
    script(({"id": "rcpt-1"}, True))
    assert client.charge("o-1", 1999)["id"] == "rcpt-1"
    assert len(gateway.CHARGES) == 1


def test_unavailable_then_success_is_one_charge():
    script(gateway.GatewayUnavailable("502"), ({"id": "rcpt-2"}, True))
    assert client.charge("o-2", 1999)["id"] == "rcpt-2"
    assert len(gateway.CHARGES) == 1


def test_timeout_after_charge_recorded_does_not_charge_twice():
    # First attempt lands but the response is lost; the retry replays the receipt.
    script(({"id": "rcpt-3"}, False))
    assert client.charge("o-3", 1999)["id"] == "rcpt-3"
    assert len(gateway.CHARGES) == 1


def test_declined_raises_charge_failed():
    script(*[gateway.GatewayDeclined("insufficient_funds")] * 3)
    with pytest.raises(client.ChargeFailed):
        client.charge("o-4", 1999)
    assert gateway.CHARGES == []
