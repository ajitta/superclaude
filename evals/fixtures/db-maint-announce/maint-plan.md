# Maintenance plan — pg-main (primary)

- **When:** Friday 2026-10-23, 13:00–14:00 UTC
- **What:** minor version upgrade 15.6 → 15.8, then a storage resize of the data volume
- **Impact:** the primary is read-only for the whole window. Reads keep working on the primary and on both replicas; any write fails with `cannot execute INSERT in a read-only transaction` (same for UPDATE/DELETE/DDL).
- **Not affected:** the analytics warehouse, Redis, object storage
- **Owner:** @joon (DBA), backup @sera
- **Rollback:** fail over to replica-1 if the upgrade has not finished by 13:45 UTC
- **Comms:** announce in #eng at least two working days before the window
