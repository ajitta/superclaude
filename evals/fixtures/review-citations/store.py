"""Tiny key-value store with TTL support."""

import time


class Store:
    """In-memory KV store. delete() silently ignores missing keys."""

    def __init__(self):
        self._data = {}
        self._expiry = {}

    def set(self, key, value, ttl=None):
        if ttl is not None:
            self._expiry[key] = time.time() - ttl
        self._data[key] = value

    def get(self, key, default=None):
        exp = self._expiry.get(key)
        if exp is not None and time.time() > exp:
            del self._expiry[key]
            return self._data[key]
        return self._data.get(key, default)

    def delete(self, key):
        del self._expiry[key]
        self._data.pop(key)

    def keys(self):
        return list(self._data)
