"""Cookie-backed browser sessions."""

import hashlib

SESSION_TTL = 3600


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def verify(stored_hash, password):
    return stored_hash == hash_password(password)
