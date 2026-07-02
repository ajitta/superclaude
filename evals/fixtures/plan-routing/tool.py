"""Report generator CLI."""

import json
import sys


def main():
    data = json.load(sys.stdin)
    for row in data:
        print(f"{row['name']}: {row['total']}")


if __name__ == "__main__":
    main()
