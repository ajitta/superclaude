"""Event ingestion entrypoint."""


def ingest(event):
    if not event.get("id"):
        raise ValueError("event id required")
    return {"status": "ok", "id": event["id"]}
