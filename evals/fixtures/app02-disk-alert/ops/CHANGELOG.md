# ops change log — app hosts

- 2026-10-14 — app-01..03: node exporter 1.8.2.
- 2026-10-02 — app logs moved /var/log/app → /var/log/svc (svc 3.0 packaging). /var/log/svc is a 40 GB volume on each app host.
- 2026-09-21 — /backup on app-01..03: weekly full backup Sundays 01:00 UTC; the prune job keeps only the newest full and runs Sundays 09:00 UTC, so /backup peaks during the full and drops back afterwards.
- 2026-09-08 — alert routing: disk rules page oncall-primary; everything else goes to #ops-alerts.
