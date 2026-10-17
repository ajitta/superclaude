# gateway-client

Thin client for the card gateway used by checkout. `payments.py` is the whole
thing; `test_payments.py` runs with `python -m pytest -q` (stdlib + pytest).

Gateway contract we code against:

* Every request is signed: `X-Timestamp`, `X-Nonce`, `X-Signature`
  (HMAC-SHA256 over `timestamp.nonce.body`). The gateway rejects requests
  whose timestamp is more than 30 s old or whose nonce was already seen.
* `POST /v1/charges` is deduplicated by the `Idempotency-Key` header: a
  repeated key within 24 h returns the original charge instead of charging
  again.
* 503 and transport timeouts are retryable; a timeout does **not** tell you
  whether the gateway processed the charge.
