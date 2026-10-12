"""
Shipped content names no symbol or memory MCP server.

The Serena server was dropped from everything under `src/superclaude/` by the
01-discovery Q2-Q5 decisions: code exploration is the tool-neutral
Symbolic-First rule, and session memory lives in `.claude/memories/` plus
Claude auto memory. This guard keeps the name from coming back. It has no
allowlist. Background: docs/features/serena-removal/
"""

from pathlib import Path

SRC = Path(__file__).parent.parent.parent / "src" / "superclaude"
FORBIDDEN = "serena"


def _shipped_files() -> list[Path]:
    files = []
    for path in sorted(SRC.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        files.append(path)
    return files


def test_shipped_content_names_no_server() -> None:
    hits = []
    for path in _shipped_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if FORBIDDEN in line.casefold():
                rel = path.relative_to(SRC.parent.parent).as_posix()
                hits.append(f"{rel}:{lineno}")
    assert not hits, "server name found in shipped content:\n" + "\n".join(hits)
