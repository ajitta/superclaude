"""Tests for file_size_guard.py PreToolUse hook."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

GUARD_SCRIPT = Path(__file__).parent.parent.parent / "src" / "superclaude" / "scripts" / "file_size_guard.py"


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
    return json.loads(result.stdout.strip())


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


def _create_file(temp_dir: Path, name: str, size: int) -> str:
    """Create a temp file of given size and return its path."""
    path = temp_dir / name
    path.write_bytes(b"x" * size)
    return str(path)


class TestApprove:
    """Tests where the guard should approve (allow) the Read."""

    def test_small_file_exempt(self, temp_dir):
        path = _create_file(temp_dir, "small.py", 3_000)
        result = run_guard({"file_path": path})
        assert result["decision"] == "approve"

    def test_with_limit_parameter(self, temp_dir):
        path = _create_file(temp_dir, "big.py", 35_000)
        result = run_guard({"file_path": path, "limit": 500})
        assert result["decision"] == "approve"

    def test_with_pages_parameter(self, temp_dir):
        path = _create_file(temp_dir, "doc.pdf", 35_000)
        result = run_guard({"file_path": path, "pages": "1-5"})
        assert result["decision"] == "approve"

    def test_config_yaml_under_threshold(self, temp_dir):
        path = _create_file(temp_dir, "config.yaml", 20_000)
        result = run_guard({"file_path": path})
        assert result["decision"] == "approve"

    def test_config_json_under_threshold(self, temp_dir):
        path = _create_file(temp_dir, "settings.json", 25_000)
        result = run_guard({"file_path": path})
        assert result["decision"] == "approve"

    def test_config_toml_under_threshold(self, temp_dir):
        path = _create_file(temp_dir, "pyproject.toml", 10_000)
        result = run_guard({"file_path": path})
        assert result["decision"] == "approve"

    def test_config_env_under_threshold(self, temp_dir):
        path = _create_file(temp_dir, ".env", 1_000)
        result = run_guard({"file_path": path})
        assert result["decision"] == "approve"

    def test_binary_file(self, temp_dir):
        path = _create_file(temp_dir, "image.png", 1_000_000)
        result = run_guard({"file_path": path})
        assert result["decision"] == "approve"

    def test_env_var_disabled(self, temp_dir):
        path = _create_file(temp_dir, "big.py", 50_000)
        result = run_guard({"file_path": path}, env_override={"SUPERCLAUDE_SIZE_GUARD": "0"})
        assert result["decision"] == "approve"

    def test_empty_input(self):
        result = run_guard({})
        assert result["decision"] == "approve"

    def test_no_file_path(self):
        result = run_guard({"file_path": ""})
        assert result["decision"] == "approve"

    def test_nonexistent_file(self):
        result = run_guard({"file_path": "/nonexistent/path/file.py"})
        assert result["decision"] == "approve"

    def test_file_between_5kb_and_30kb_with_limit(self, temp_dir):
        """Code file between 5-30KB with limit should pass."""
        path = _create_file(temp_dir, "medium.py", 15_000)
        result = run_guard({"file_path": path, "limit": 500})
        assert result["decision"] == "approve"


class TestBlock:
    """Tests where the guard should block the Read."""

    def test_code_file_over_threshold(self, temp_dir):
        path = _create_file(temp_dir, "big.py", 35_000)
        result = run_guard({"file_path": path})
        assert result["decision"] == "block"
        assert "30KB" in result["reason"]
        assert "limit" in result["reason"]

    def test_json_file_over_threshold(self, temp_dir):
        path = _create_file(temp_dir, "data.json", 35_000)
        result = run_guard({"file_path": path})
        assert result["decision"] == "block"
        assert "jq" in result["reason"]

    def test_jsonl_file_over_threshold(self, temp_dir):
        path = _create_file(temp_dir, "logs.jsonl", 50_000)
        result = run_guard({"file_path": path})
        assert result["decision"] == "block"
        assert "jq" in result["reason"]

    def test_large_config_json(self, temp_dir):
        """package-lock.json style — config extension but over threshold."""
        path = _create_file(temp_dir, "package-lock.json", 500_000)
        result = run_guard({"file_path": path})
        assert result["decision"] == "block"

    def test_large_yaml(self, temp_dir):
        """Large YAML over threshold — not exempt."""
        path = _create_file(temp_dir, "huge.yaml", 50_000)
        result = run_guard({"file_path": path})
        assert result["decision"] == "block"

    def test_ts_file_over_threshold(self, temp_dir):
        path = _create_file(temp_dir, "component.ts", 40_000)
        result = run_guard({"file_path": path})
        assert result["decision"] == "block"
        assert "Grep" in result["reason"]

    def test_code_file_between_5kb_and_30kb(self, temp_dir):
        """Code file between 5-30KB without limit — intentional friction zone."""
        path = _create_file(temp_dir, "module.py", 15_000)
        result = run_guard({"file_path": path})
        # 15KB code file is between 5KB (small exempt) and 30KB (threshold)
        # Should approve because it's under SIZE_THRESHOLD
        assert result["decision"] == "approve"

    def test_code_file_at_threshold(self, temp_dir):
        """File exactly at 30KB threshold — should block."""
        path = _create_file(temp_dir, "exact.py", 30_000)
        result = run_guard({"file_path": path})
        assert result["decision"] == "block"


class TestBlockMessage:
    """Tests for context-aware block messages."""

    def test_python_file_message(self, temp_dir):
        path = _create_file(temp_dir, "script.py", 50_000)
        result = run_guard({"file_path": path})
        assert "limit" in result["reason"]
        assert "Grep" in result["reason"]
        assert "jq" not in result["reason"]

    def test_json_file_message(self, temp_dir):
        path = _create_file(temp_dir, "data.json", 50_000)
        result = run_guard({"file_path": path})
        assert "jq" in result["reason"]
        assert "limit" in result["reason"]

    def test_message_includes_size(self, temp_dir):
        path = _create_file(temp_dir, "big.py", 50_000)
        result = run_guard({"file_path": path})
        assert "48KB" in result["reason"]  # 50000 // 1024 = 48
