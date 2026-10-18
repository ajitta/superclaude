import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tickets.cli import main


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "tickets.csv"

    def run_cli(self, *args):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["--file", str(self.path), *args])
        return code, buf.getvalue()

    def test_add_then_list(self):
        self.run_cli("add", "Fix login")
        code, out = self.run_cli("list")
        self.assertEqual(code, 0)
        self.assertIn("Fix login", out)
        self.assertIn("open", out)

    def test_close_marks_ticket_closed(self):
        self.run_cli("add", "Fix login")
        code, _ = self.run_cli("close", "1")
        self.assertEqual(code, 0)
        _, out = self.run_cli("list")
        self.assertIn("closed", out)

    def test_add_with_priority_shows_in_list(self):
        self.run_cli("add", "Fix login", "--priority", "high")
        self.run_cli("add", "Update docs")
        code, out = self.run_cli("list")
        self.assertEqual(code, 0)
        first, second = out.splitlines()
        self.assertIn("high", first)
        self.assertIn("medium", second)


if __name__ == "__main__":
    unittest.main()
