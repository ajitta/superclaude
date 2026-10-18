# shop-infra

Kubernetes manifests and server configuration for the shop.

- `deploy/<service>/` — Deployment, Service, HPA and ConfigMap per service
- `db/<server>/` — database server configuration
- `loadtest/` — load test reports

Changes go through a PR; CI applies `deploy/` with `kubectl apply -k deploy/`.
