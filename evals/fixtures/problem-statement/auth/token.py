"""Bearer tokens for machine-to-machine calls."""

import hmac

SIGNING_KEY = "dev-secret-do-not-ship"


def sign(payload):
    return hmac.new(SIGNING_KEY.encode(), payload.encode(), "sha256").hexdigest()


def verify(payload, signature):
    return sign(payload) == signature
