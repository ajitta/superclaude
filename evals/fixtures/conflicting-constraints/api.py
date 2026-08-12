"""Public API. See CLAUDE.md before editing."""


def parse(text):
    """Split a config line into a (key, value) pair."""
    key, _, value = text.partition("=")
    return key.strip(), value.strip()


def check(pair):
    """Return True when the pair has a non-empty key."""
    return bool(pair[0])
