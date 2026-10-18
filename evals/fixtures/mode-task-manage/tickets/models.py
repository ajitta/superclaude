"""The Ticket record and its validation rules."""

from dataclasses import dataclass

STATUSES = ("open", "closed")


@dataclass
class Ticket:
    id: int
    title: str
    status: str = "open"

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("title must not be empty")
        if self.status not in STATUSES:
            raise ValueError(f"unknown status: {self.status!r}")
