"""
Content usage audit tests for SuperClaude.

Validates:
- All MODE_*.md files are mapped in TRIGGER_MAP
- All MCP_*.md files are mapped in TRIGGER_MAP or COMPOSITE_FLAGS
- TRIGGER_MAP file references actually exist
- COMPOSITE_FLAGS file references actually exist
"""

import re
from pathlib import Path

import pytest

from superclaude.scripts.context_loader import COMPOSITE_FLAGS, TRIGGER_MAP

_SRC = Path(__file__).parent.parent.parent / "src" / "superclaude"
MODES_DIR = _SRC / "modes"
MCP_DIR = _SRC / "mcp"


def _trigger_map_paths() -> set[str]:
    """Extract all file paths from TRIGGER_MAP."""
    return {entry[1] for entry in TRIGGER_MAP}


def _composite_flags_paths() -> set[str]:
    """Extract all file paths from COMPOSITE_FLAGS."""
    paths = set()
    for files in COMPOSITE_FLAGS.values():
        for file_path, _ in files:
            paths.add(file_path)
    return paths


def _all_mapped_paths() -> set[str]:
    """Union of TRIGGER_MAP and COMPOSITE_FLAGS paths."""
    return _trigger_map_paths() | _composite_flags_paths()


class TestModeMapping:
    """Every MODE_*.md must appear in TRIGGER_MAP."""

    def test_all_modes_mapped(self):
        """Each mode file should have at least one trigger in TRIGGER_MAP."""
        if not MODES_DIR.exists():
            pytest.skip("No modes directory")

        mode_files = sorted(MODES_DIR.glob("MODE_*.md"))
        assert mode_files, "No MODE_*.md files found"

        mapped = _all_mapped_paths()
        unmapped = []
        for mode_file in mode_files:
            relative = f"modes/{mode_file.name}"
            if relative not in mapped:
                unmapped.append(mode_file.name)

        assert not unmapped, (
            f"Modes not in TRIGGER_MAP or COMPOSITE_FLAGS: {unmapped}\n"
            f"Add triggers to context_loader.py TRIGGER_MAP"
        )


class TestMcpMapping:
    """Every MCP_*.md must appear in TRIGGER_MAP or COMPOSITE_FLAGS."""

    def test_all_mcp_mapped(self):
        """Each MCP doc should be reachable via some trigger."""
        if not MCP_DIR.exists():
            pytest.skip("No MCP directory")

        mcp_files = sorted(MCP_DIR.glob("MCP_*.md"))
        assert mcp_files, "No MCP_*.md files found"

        mapped = _all_mapped_paths()
        unmapped = []
        for mcp_file in mcp_files:
            relative = f"mcp/{mcp_file.name}"
            if relative not in mapped:
                unmapped.append(mcp_file.name)

        assert not unmapped, (
            f"MCP docs not in TRIGGER_MAP or COMPOSITE_FLAGS: {unmapped}\n"
            f"Add triggers to context_loader.py"
        )


class TestTriggerMapIntegrity:
    """TRIGGER_MAP file references must point to existing source files."""

    def test_trigger_map_files_exist(self):
        """Every path in TRIGGER_MAP must correspond to a real source file."""
        missing = []
        for _, file_path, _ in TRIGGER_MAP:
            # file_path is relative like "modes/MODE_Brainstorming.md"
            # At runtime these resolve from ~/.claude/superclaude/
            # At test time, check they exist in source
            parts = file_path.split("/", 1)
            if len(parts) != 2:
                missing.append(file_path)
                continue
            subdir, filename = parts
            source_file = _SRC / subdir / filename
            if not source_file.exists():
                missing.append(file_path)

        assert not missing, (
            f"TRIGGER_MAP references non-existent source files: {missing}"
        )

    def test_composite_flags_files_exist(self):
        """Every path in COMPOSITE_FLAGS must correspond to a real source file."""
        missing = []
        for flag, files in COMPOSITE_FLAGS.items():
            for file_path, _ in files:
                parts = file_path.split("/", 1)
                if len(parts) != 2:
                    missing.append(f"{flag}: {file_path}")
                    continue
                subdir, filename = parts
                source_file = _SRC / subdir / filename
                if not source_file.exists():
                    missing.append(f"{flag}: {file_path}")

        assert not missing, (
            f"COMPOSITE_FLAGS references non-existent source files: {missing}"
        )
