"""Alert routing for the on-call rotation.

Severity scale: 1 info, 2 low, 3 high, 4 critical. The runbook rule is
"an alert at or above the configured threshold pages the on-call engineer;
anything below is logged only".
"""

from __future__ import annotations

DEFAULT_THRESHOLD = 3

SEVERITY_NAMES = {1: "info", 2: "low", 3: "high", 4: "critical"}


def should_escalate(severity: int, threshold: int = DEFAULT_THRESHOLD) -> bool:
    """True when the alert must page on-call (severity at or above threshold)."""
    if severity not in SEVERITY_NAMES:
        raise ValueError(f"unknown severity {severity!r}")
    return severity > threshold


def route_alert(alert: dict, threshold: int = DEFAULT_THRESHOLD) -> str:
    """Return the destination for one alert: 'page' or 'log'."""
    if should_escalate(alert["severity"], threshold):
        return "page"
    return "log"


def summarize(alerts: list[dict], threshold: int = DEFAULT_THRESHOLD) -> dict:
    """Count how many alerts went to each destination."""
    counts = {"page": 0, "log": 0}
    for alert in alerts:
        counts[route_alert(alert, threshold)] += 1
    return counts
