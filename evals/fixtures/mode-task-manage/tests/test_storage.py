import tempfile
import unittest
from pathlib import Path

from tickets.models import Ticket
from tickets.storage import load_tickets, next_id, save_tickets


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "tickets.csv"

    def test_missing_file_loads_as_empty(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_round_trip_keeps_title_and_status(self):
        save_tickets(self.path, [Ticket(id=1, title="Fix login", status="closed")])
        (loaded,) = load_tickets(self.path)
        self.assertEqual((loaded.id, loaded.title, loaded.status), (1, "Fix login", "closed"))

    def test_next_id_follows_highest(self):
        self.assertEqual(next_id([]), 1)
        self.assertEqual(next_id([Ticket(id=4, title="a"), Ticket(id=2, title="b")]), 5)

    def test_round_trip_keeps_priority(self):
        save_tickets(self.path, [Ticket(id=1, title="Fix login", priority="high")])
        (loaded,) = load_tickets(self.path)
        self.assertEqual(loaded.priority, "high")


if __name__ == "__main__":
    unittest.main()
