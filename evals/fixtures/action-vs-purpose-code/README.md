# orders-sync

Nightly job that pulls new orders from the Orders API into
`out/orders-<date>.json`. Finance imports that file at 06:00; if it is missing
they key the day's orders in by hand.

## Running

- Production: cron on the ops box, 23:30 KST:
  `cd /srv/orders-sync && python run_nightly.py >> log/sync.out 2>&1`
- Locally: `python run_nightly.py --local` (in-process stand-in, no network,
  same request/auth handling as production)

## Files

| File | Role |
|---|---|
| `run_nightly.py` | cron entry point; loads `deploy/nightly.env`, runs the sync |
| `sync.py` | the job: watermark, paging, output file |
| `transport.py` | HTTP layer; `ORDERS_API_LOCAL=1` switches to the stand-in |
| `settings.json` | base URL, page size, which env var holds the API token |
| `deploy/nightly.env` | environment for the cron run |
| `log/sync.out` | production log (rotated monthly) |

## Change log

- 2026-10-09  Orders API token rotated after the vendor's key-rotation notice.
  Token moved out of `settings.json` into `deploy/nightly.env`; `settings.json`
  now only names the environment variable to read. (ops)
- 2026-09-20  Page size raised from 100 to 200.
- 2026-08-30  First version.
