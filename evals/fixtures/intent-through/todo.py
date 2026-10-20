"""Tiny todo CLI: add, list, done. Data lives in todos.json."""

import json
import sys
from pathlib import Path

DATA = Path("todos.json")


def load(path=DATA):
    if not path.exists():
        return []
    return json.loads(path.read_text())


def save(items, path=DATA):
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2))


def add(items, title):
    next_id = max((i["id"] for i in items), default=0) + 1
    items.append({"id": next_id, "title": title, "done": False})
    return next_id


def mark_done(items, item_id):
    for i in items:
        if i["id"] == item_id:
            i["done"] = True
            return True
    return False


def main(argv):
    items = load()
    if not argv or argv[0] == "list":
        for i in items:
            print(f"{i['id']:>3} [{'x' if i['done'] else ' '}] {i['title']}")
        return 0
    if argv[0] == "add" and len(argv) > 1:
        print(add(items, " ".join(argv[1:])))
        save(items)
        return 0
    if argv[0] == "done" and len(argv) == 2:
        ok = mark_done(items, int(argv[1]))
        save(items)
        return 0 if ok else 1
    print("usage: todo.py [list | add TITLE | done ID]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
