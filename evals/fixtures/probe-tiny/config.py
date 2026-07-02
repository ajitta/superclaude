"""Config loading: env vars first, then config file, then defaults."""

import json
import os
import pathlib

DEFAULTS = {"timeout": 30, "retries": 3}


def load(path="config.json"):
    cfg = dict(DEFAULTS)
    p = pathlib.Path(path)
    if p.exists():
        cfg.update(json.loads(p.read_text()))
    for key in cfg:
        env = os.environ.get(f"APP_{key.upper()}")
        if env is not None:
            cfg[key] = type(cfg[key])(env)
    return cfg
