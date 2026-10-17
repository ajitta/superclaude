"""Nightly orders sync.

Pulls orders created since the last watermark from the Orders API and writes
them to out/orders-<date>.json for the 06:00 finance import.
"""
import datetime as dt
import json
import logging
import os
import pathlib
import sys

import transport

ROOT = pathlib.Path(__file__).resolve().parent
log = logging.getLogger("sync")


class SyncError(Exception):
    pass


def load_settings() -> dict:
    return json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))


def read_watermark(path: pathlib.Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def write_watermark(path: pathlib.Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value + "\n", encoding="utf-8")


def fetch_orders(settings: dict, since: str) -> list[dict]:
    token = os.environ.get(settings["token_env"], "")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    orders: list[dict] = []
    page = 1
    while True:
        url = (
            f"{settings['base_url']}/orders?since={since}"
            f"&page={page}&page_size={settings['page_size']}"
        )
        status, body = transport.get(url, headers, settings["timeout_seconds"])
        if status != 200:
            raise SyncError(f"GET {url} -> {status} {body[:160]}")
        data = json.loads(body)
        orders.extend(data["orders"])
        if not data.get("next_page"):
            return orders
        page = data["next_page"]


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,
    )
    settings = load_settings()
    watermark = ROOT / settings["watermark_file"]
    since = read_watermark(watermark)
    started = dt.datetime.now(dt.timezone.utc)
    log.info("sync start since=%s", since)
    try:
        orders = fetch_orders(settings, since)
    except (SyncError, OSError) as exc:
        log.error("%s", exc)
        log.error("sync aborted")
        return 1
    out = ROOT / "out" / f"orders-{started:%Y-%m-%d}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(orders, indent=2) + "\n", encoding="utf-8")
    write_watermark(watermark, started.strftime("%Y-%m-%dT%H:%M:%SZ"))
    log.info(
        "sync ok: %d orders written to %s", len(orders), out.relative_to(ROOT).as_posix()
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
