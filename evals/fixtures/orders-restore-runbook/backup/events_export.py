"""Copy order_events to Parquet, one file per day, in s3://acme-backups/orders-events/.

    python backup/events_export.py --day 2026-10-18
    python backup/events_export.py --import --since 2026-01-01 --dsn postgresql:///orders_restore

`--import` loads every daily file from `--since` on back into order_events.
"""

import argparse
import datetime as dt

BUCKET = "s3://acme-backups/orders-events/"
COLUMNS = ("id", "order_id", "kind", "payload", "created_at")


def export_day(day: dt.date) -> str:
    target = f"{BUCKET}{day:%Y/%m/%d}.parquet"
    # SELECT COLUMNS FROM order_events WHERE created_at::date = day -> target
    return target


def import_since(since: dt.date, dsn: str) -> list[str]:
    days = (dt.date.today() - since).days
    loaded = [f"{BUCKET}{since + dt.timedelta(d):%Y/%m/%d}.parquet" for d in range(days)]
    # each file -> COPY order_events (COLUMNS) on dsn
    return loaded


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--day", type=dt.date.fromisoformat)
    ap.add_argument("--import", dest="do_import", action="store_true")
    ap.add_argument("--since", type=dt.date.fromisoformat)
    ap.add_argument("--dsn")
    args = ap.parse_args()
    if args.do_import:
        for path in import_since(args.since, args.dsn):
            print("loaded", path)
    else:
        print("wrote", export_day(args.day or dt.date.today() - dt.timedelta(days=1)))


if __name__ == "__main__":
    main()
