import json
import sys


def summarize(path):
    with open(path, encoding="utf-8") as fh:
        rows = json.load(fh)
    return {"count": len(rows), "total": sum(r["amount"] for r in rows)}


if __name__ == "__main__":
    print(summarize(sys.argv[1]))
