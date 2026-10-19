# api-infra

Kubernetes manifests and server configuration for the public API.

- `deploy/<service>/` — Deployment, Service, HPA and config per service
- `db/<server>/` — database server configuration
- `loadtest/` — load test reports

Changes go through a PR; CI applies `deploy/` with `kubectl apply -k deploy/`.
