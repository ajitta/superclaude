"""CSV persistence for tickets.

The file has a header row. Every column the store reads or writes is listed
in FIELDS, in order; anything not listed there is dropped on save.
"""

import csv
from pathlib import Path

from .models import Ticket

FIELDS = ["id", "title", "status"]


def load_tickets(path):
    path = Path(path)
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return [_from_row(row) for row in csv.DictReader(fh)]


def save_tickets(path, tickets):
    path = Path(path)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        for ticket in tickets:
            writer.writerow(_to_row(ticket))


def next_id(tickets):
    return max((t.id for t in tickets), default=0) + 1


def _to_row(ticket):
    return {"id": ticket.id, "title": ticket.title, "status": ticket.status}


def _from_row(row):
    return Ticket(id=int(row["id"]), title=row["title"], status=row["status"])
