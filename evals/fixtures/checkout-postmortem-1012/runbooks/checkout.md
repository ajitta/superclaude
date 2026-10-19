# Checkout on-call

- Dashboard: "Checkout overview" (5xx rate, p95, orders per minute).
- Roll back a release: `deployctl rollback checkout --to <release>`.
- Escalate to payments on-call when card authorisations fail.
