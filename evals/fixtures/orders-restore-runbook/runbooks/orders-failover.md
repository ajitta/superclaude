# Orders database failover

1. Confirm the primary is down: `pg_isready -h orders-db-0`.
2. Promote the replica: `pg_ctl promote -D /var/lib/postgresql/16/main` on `orders-db-1`.
3. Move the `orders-db` service selector to `orders-db-1`.
4. Rebuild the old primary as a replica with `pg_basebackup`.
