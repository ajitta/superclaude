# acme-web

Flask site. Templates live in `web/templates/`, static files in `web/static/`.
`python web/assets/fingerprint.py` writes `web/static/assets.json`, which the
`asset()` template helper reads. A deploy syncs `web/static/` to the CDN origin.
