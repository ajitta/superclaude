# orders-svc

Owns the `orders` table and the daily CSV export consumed by **billing-svc**.

## Layout

    orders/models.py       Order record + ORDER_COLUMNS (shared, see note in file)
    orders/repository.py   all SQL for the orders table
    orders/export.py       daily CSV export for billing-svc
    schema/                numbered migrations, applied in order by ops

## Running

    python -m orders.repository   # smoke run against an in-memory sqlite db
    python -m orders.export       # prints a sample export

## Schema changes (read before touching `schema/`)

The `orders` table is read directly by billing-svc (same Postgres instance,
read-only role). Because of that, schema changes follow the expand/contract
policy:

1. Migration adds the column as nullable. No code reads it yet.
2. Deploy orders-svc **and** billing-svc in the same release window (book the
   slot with billing on-call; they deploy Tuesdays and Thursdays).
3. Backfill if needed, then a follow-up migration tightens constraints.

Changes that also alter the export file (`orders/export.py`) need the header
change mirrored in `billing-svc/ingest/orders_csv.py` — billing parses by
column position, not by header name. See `schema/002_add_currency.sql` for the
last time we did this; it took two releases.

## Tests

There are no automated tests for `orders/` yet (tracked as ORD-412). The smoke
entry points above are what we run by hand before a release.
