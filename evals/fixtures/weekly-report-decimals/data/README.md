# data/

`orders.csv` is the weekly export from the payments database: one row per order, every status. The export runs on Mondays at 06:00 UTC and replaces the file.

| column | meaning |
|---|---|
| `order_id` | `O-<n>` |
| `created_at` | order time, UTC, ISO 8601 |
| `method` | `card`, `bank` or `wallet` |
| `status` | `paid`, `refunded` or `failed` |
| `amount` | order total, USD |

## Change log

- 2026-10-06 — payments v2: card payments recorded as `settled` (was `paid`). Bank and wallet payments still use `paid`.
- 2026-09-01 — `method` column added.
- 2026-08-03 — export moved from daily to weekly (Mondays).
