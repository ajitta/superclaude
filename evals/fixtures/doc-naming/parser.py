"""Line-oriented config parser."""


def parse(text):
    """Parse KEY=VALUE lines into a dict. Blank lines and # comments skipped."""
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def dumps(data):
    """Serialize a dict back to KEY=VALUE lines, keys sorted."""
    return "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
