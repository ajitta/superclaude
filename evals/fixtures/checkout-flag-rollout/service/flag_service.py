"""Serve flag decisions to the apps. Loads flags/<env>.yaml at startup."""

import hashlib

from flags.effective import ceilings


def enabled(
    rollout: int,
    user_id: str,
    flag: str,
    tags: tuple[str, ...] = (),
    region: str | None = None,
) -> bool:
    by_tag = ceilings().get(region, {})
    rollout = min([rollout, *(by_tag[t] for t in tags if t in by_tag)])
    bucket = int(hashlib.sha1(f"{flag}:{user_id}".encode()).hexdigest(), 16) % 100
    return bucket < rollout
