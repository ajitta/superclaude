# Scheduled jobs

Times are KST.

| job | schedule | database access | owner | notes |
|---|---|---|---|---|
| nightly-export | daily 03:00 | replica-1 (read) | @hyun | |
| billing-close | Fridays 22:30 | primary (write) | @mina | closes the week's invoices; fails in read-only; can run by hand later the same night |
| search-reindex | Saturdays 04:00 | replica-2 (read) | @hyun | |
| metrics-rollup | hourly at :40 | metrics DB (write) | @sol | separate database, not pg-main |
| session-cleanup | daily 05:30 | primary (write) | @joon | |
