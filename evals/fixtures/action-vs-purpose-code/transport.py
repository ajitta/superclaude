"""HTTP transport for the Orders API.

get(url, headers, timeout) -> (status, body). Talks to the real API over
urllib. When ORDERS_API_LOCAL=1 is set (run_nightly.py --local), an
in-process stand-in answers instead, so the job can be exercised on a laptop
or in CI without network access or a production token. The stand-in follows
the API's auth contract: a bearer token issued by the vendor (prefix "ord_").
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request


def get(url: str, headers: dict, timeout: int = 30) -> tuple[int, str]:
    if os.environ.get("ORDERS_API_LOCAL") == "1":
        return _local(url, headers)
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")


# ── local stand-in ──────────────────────────────────────────────────────────

_SAMPLE_ORDERS = [
    {"id": "o-10231", "created_at": "2026-10-16T14:02:11Z", "total": 48.50},
    {"id": "o-10232", "created_at": "2026-10-16T15:47:03Z", "total": 12.00},
    {"id": "o-10233", "created_at": "2026-10-16T19:21:40Z", "total": 131.25},
]


def _local(url: str, headers: dict) -> tuple[int, str]:
    auth = headers.get("Authorization", "")
    token = auth[len("Bearer "):] if auth.startswith("Bearer ") else ""
    if not token.startswith("ord_"):
        return 401, json.dumps(
            {"error": "invalid_token", "message": "The access token is missing or invalid"}
        )
    parsed = urllib.parse.urlparse(url)
    if not parsed.path.endswith("/orders"):
        return 404, json.dumps({"error": "not_found"})
    query = urllib.parse.parse_qs(parsed.query)
    page = int(query.get("page", ["1"])[0])
    orders = _SAMPLE_ORDERS if page == 1 else []
    return 200, json.dumps({"orders": orders, "next_page": None})
