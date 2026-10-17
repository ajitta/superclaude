"""Entry point used by cron.

Loads deploy/nightly.env into the environment (values already present in the
environment win), then runs the sync.

    python run_nightly.py            # production
    python run_nightly.py --local    # in-process stand-in, no network
"""
import os
import pathlib
import sys

import sync

ENV_FILE = pathlib.Path(__file__).resolve().parent / "deploy" / "nightly.env"


def load_env_file(path: pathlib.Path) -> None:
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


if __name__ == "__main__":
    if "--local" in sys.argv[1:]:
        os.environ["ORDERS_API_LOCAL"] = "1"
    load_env_file(ENV_FILE)
    sys.exit(sync.main())
