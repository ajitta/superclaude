import unittest

from tickets.models import Ticket


class TicketTests(unittest.TestCase):
    def test_status_defaults_to_open(self):
        self.assertEqual(Ticket(id=1, title="Fix login").status, "open")

    def test_rejects_unknown_status(self):
        with self.assertRaises(ValueError):
            Ticket(id=1, title="Fix login", status="pending")

    def test_rejects_blank_title(self):
        with self.assertRaises(ValueError):
            Ticket(id=1, title="   ")

    def test_priority_defaults_to_medium_and_is_validated(self):
        self.assertEqual(Ticket(id=1, title="Fix login").priority, "medium")
        self.assertEqual(
            Ticket(id=2, title="Fix login", priority="high").priority, "high"
        )
        with self.assertRaises(ValueError):
            Ticket(id=3, title="Fix login", priority="urgent")


if __name__ == "__main__":
    unittest.main()
