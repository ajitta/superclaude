"""Apply migrations/*.sql in filename order to a SQLite file; --seed loads sample data.

Usage: python scripts/migrate.py <db-file> [--seed]
"""

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    db = sqlite3.connect(sys.argv[1])
    for path in sorted((ROOT / "migrations").glob("*.sql")):
        db.executescript(path.read_text(encoding="utf-8"))
        print(f"applied {path.name}")
    if "--seed" in sys.argv[2:]:
        db.executescript((ROOT / "seed" / "orders.sql").read_text(encoding="utf-8"))
        print("loaded seed/orders.sql")
    db.commit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
