"""Tests for file_size_guard.py PreToolUse hook."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

GUARD_SCRIPT = (
    Path(__file__).parent.parent.parent
    / "src"
    / "superclaude"
    / "scripts"
    / "file_size_guard.py"
)


def run_guard(tool_input: dict, env_override: dict | None = None) -> dict:
    """Run file_size_guard.py with given tool_input and return parsed JSON output."""
    stdin_data = json.dumps({"tool_input": tool_input})
    env = os.environ.copy()
    # Ensure guard is enabled by default
    env.pop("SUPERCLAUDE_SIZE_GUARD", None)
    if env_override:
        env.update(env_override)

    result = subprocess.run(
        [sys.executable, str(GUARD_SCRIPT)],
        input=stdin_data,
        capture_output=True,
        text=True,
        env=env,
    )
    return json.loads(result.stdout.strip() or "{}")


def _create_file(tmp_path: Path, name: str, size: int) -> str:
    """Create a temp file of given size and return its path."""
    path = tmp_path / name
    path.write_bytes(b"x" * size)
    return str(path)


class TestApprove:
    """Reads the guard lets through: it prints nothing, so the normal
    permission flow applies (a legacy `approve` would skip the prompt)."""

    @pytest.mark.parametrize(
        ("name", "size", "extra_input"),
        [
            ("small.py", 3_000, {}),
            ("big.py", 35_000, {"limit": 500}),
            ("doc.pdf", 35_000, {"pages": "1-5"}),
            ("config.yaml", 20_000, {}),
            ("settings.json", 25_000, {}),
            ("pyproject.toml", 10_000, {}),
            (".env", 1_000, {}),
            ("image.png", 1_000_000, {}),
            # Code file between 5-30KB with limit should pass.
            ("medium.py", 15_000, {"limit": 500}),
            # Code file between 5KB (small exempt) and 30KB (threshold) without
            # limit — intentional friction zone, but under SIZE_THRESHOLD: no
            # decision printed.
            ("module.py", 15_000, {}),
        ],
        ids=[
            "small-file-exempt",
            "with-limit-parameter",
            "with-pages-parameter",
            "config-yaml-under-threshold",
            "config-json-under-threshold",
            "config-toml-under-threshold",
            "config-env-under-threshold",
            "binary-file",
            "file-between-5kb-and-30kb-with-limit",
            "code-file-between-5kb-and-30kb",
        ],
    )
    def test_silent_for_exempt_read(self, tmp_path, name, size, extra_input):
        path = _create_file(tmp_path, name, size)
        result = run_guard({"file_path": path, **extra_input})
        assert result == {}  # silent: Claude Code's own permission flow decides

    def test_invalid_json_on_stdin_fails_open(self):
        result = subprocess.run(
            [sys.executable, str(GUARD_SCRIPT)],
            input="not json",
            capture_output=True,
            text=True,
        )
        assert result.stdout.strip() == ""

    def test_env_var_disabled(self, tmp_path):
        path = _create_file(tmp_path, "big.py", 50_000)
        result = run_guard(
            {"file_path": path}, env_override={"SUPERCLAUDE_SIZE_GUARD": "0"}
        )
        assert result == {}  # silent: Claude Code's own permission flow decides

    @pytest.mark.parametrize(
        "tool_input",
        [{}, {"file_path": ""}, {"file_path": "/nonexistent/path/file.py"}],
        ids=["empty-input", "no-file-path", "nonexistent-file"],
    )
    def test_silent_without_a_readable_file(self, tool_input):
        result = run_guard(tool_input)
        assert result == {}  # silent: Claude Code's own permission flow decides


class TestBlock:
    """Tests where the guard should block the Read."""

    @pytest.mark.parametrize(
        ("name", "size", "reason_words"),
        [
            ("big.py", 35_000, ("30KB", "limit")),
            ("data.json", 35_000, ("jq",)),
            ("logs.jsonl", 50_000, ("jq",)),
            # package-lock.json style — config extension but over threshold.
            ("package-lock.json", 500_000, ()),
            # Large YAML over threshold — not exempt.
            ("huge.yaml", 50_000, ()),
            ("component.ts", 40_000, ("Grep",)),
            # File exactly at 30KB threshold — should block, with the same unit
            # and inclusive wording as the threshold it enforces.
            ("exact.py", 30_000, ("30KB (30,000 bytes)", "at or over")),
        ],
        ids=[
            "code-file-over-threshold",
            "json-file-over-threshold",
            "jsonl-file-over-threshold",
            "large-config-json",
            "large-yaml",
            "ts-file-over-threshold",
            "code-file-at-threshold",
        ],
    )
    def test_blocks_oversized_read(self, tmp_path, name, size, reason_words):
        path = _create_file(tmp_path, name, size)
        result = run_guard({"file_path": path})
        assert result["decision"] == "block"
        for word in reason_words:
            assert word in result["reason"]


class TestBlockMessage:
    """Tests for context-aware block messages."""

    @pytest.mark.parametrize(
        ("name", "present", "absent"),
        [
            ("script.py", ("limit", "Grep"), ("jq",)),
            ("data.json", ("jq", "limit"), ()),
            ("big.py", ("50KB",), ()),  # decimal KB: 50000 // 1000
        ],
        ids=["python-file-message", "json-file-message", "message-includes-size"],
    )
    def test_message_matches_file_kind(self, tmp_path, name, present, absent):
        path = _create_file(tmp_path, name, 50_000)
        result = run_guard({"file_path": path})
        for word in present:
            assert word in result["reason"]
        for word in absent:
            assert word not in result["reason"]


def test_threshold_described_as_inclusive():
    """The guard blocks at size >= SIZE_THRESHOLD, so docs say "≥30KB", never ">30KB"."""
    repo = GUARD_SCRIPT.parents[3]
    targets = [repo / "README.md"] + [
        p
        for p in (repo / "src" / "superclaude").rglob("*")
        if p.suffix in {".md", ".json", ".py"} and "__pycache__" not in p.parts
    ]
    pattern = re.compile(r">\s?30\s?KB|above 30\s?KB|exceeds?\b[\s\S]{0,60}?\b30\s?KB")
    hits = [
        f"{p.relative_to(repo).as_posix()}: {m.group(0)}"
        for p in targets
        for m in pattern.finditer(p.read_text(encoding="utf-8"))
    ]
    assert not hits, f"exclusive 30KB threshold wording: {hits}"
