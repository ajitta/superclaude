# shop-db

SQLite schema and reports for the shop. Production `orders` holds about 2.3 million rows.

- `migrations/` — applied in filename order (`python scripts/migrate.py <db-file>`; add `--seed` for the sample data in `seed/`)
- `report/` — report queries run by the reporting cron
- `log/slow.out` — queries over 1 s from production
