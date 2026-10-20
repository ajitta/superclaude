import json

import todo


def test_add_assigns_increasing_ids():
    items = []
    assert todo.add(items, "a") == 1
    assert todo.add(items, "b") == 2


def test_mark_done():
    items = []
    todo.add(items, "a")
    assert todo.mark_done(items, 1)
    assert items[0]["done"] is True
    assert not todo.mark_done(items, 9)


def test_roundtrip(tmp_path):
    p = tmp_path / "todos.json"
    todo.save([{"id": 1, "title": "x", "done": False}], p)
    assert todo.load(p) == json.loads(p.read_text())
