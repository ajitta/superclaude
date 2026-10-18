# Orders database backups

Last reviewed: 2025-03-11

Backups of the `orders` PostgreSQL database run nightly from the ops cron
(`ops/cron/`) and land in `s3://acme-backups/orders/` as custom-format dumps,
kept for 35 days.

## Restore

1. Fetch the latest dump: `aws s3 cp s3://acme-backups/orders/<latest>.dump .`
2. Create an empty database and restore into it:
   `pg_restore --no-owner -d orders_restore <latest>.dump`
3. Point the application at the restored database.
