"""
Tests for drift detection between source and installed files.
"""

from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import pytest

from superclaude.cli.verify_drift import (
    DRIFTED,
    EXTRA,
    MISSING,
    OK,
    verify_drift,
)


@contextmanager
def _mock_package_root(src_root: Path):
    """Patch _get_package_root in both install_paths and verify_drift modules."""
    with (
        patch("superclaude.cli.install_paths._get_package_root", return_value=src_root),
        patch("superclaude.cli.verify_drift._get_package_root", return_value=src_root),
    ):
        yield


def _setup_full(tmp_path, component_files=None):
    """Create a complete source/target layout.

    Args:
        tmp_path: pytest tmp_path
        component_files: dict of {component: {filename: (src, tgt_or_None)}}
                         Components not listed get empty dirs.
    """
    src_root = tmp_path / "src"
    base_path = tmp_path / "install"
    component_files = component_files or {}

    from superclaude.cli.install_paths import COMPONENTS

    for comp, (src_sub, tgt_sub, _) in COMPONENTS.items():
        (src_root / src_sub).mkdir(parents=True, exist_ok=True)
        (base_path / tgt_sub).mkdir(parents=True, exist_ok=True)

        if comp in component_files:
            for fname, (src_content, tgt_content) in component_files[comp].items():
                if comp == "skills":
                    skill_name, _, manifest = fname.partition("/")
                    skill_src = src_root / src_sub / skill_name
                    skill_src.mkdir(parents=True, exist_ok=True)
                    (skill_src / manifest).write_text(src_content, encoding="utf-8")
                    if tgt_content is not None:
                        skill_tgt = base_path / tgt_sub / skill_name
                        skill_tgt.mkdir(parents=True, exist_ok=True)
                        (skill_tgt / manifest).write_text(tgt_content, encoding="utf-8")
                else:
                    (src_root / src_sub / fname).write_text(src_content, encoding="utf-8")
                    if tgt_content is not None:
                        (base_path / tgt_sub / fname).write_text(tgt_content, encoding="utf-8")

    # CLAUDE_SC.md
    (src_root / "CLAUDE_SC.md").write_text("sc", encoding="utf-8")
    (base_path / "superclaude").mkdir(parents=True, exist_ok=True)
    (base_path / "superclaude" / "CLAUDE_SC.md").write_text("sc", encoding="utf-8")

    return src_root, base_path


class TestDriftDetection:
    """Test verify_drift() with synthetic source/target layouts."""

    def test_clean_no_drift(self, tmp_path):
        """All files match → clean=True."""
        src_root, base_path = _setup_full(tmp_path, {
            "commands": {
                "build.md": ("content", "content"),
                "test.md": ("abc", "abc"),
            },
        })

        with _mock_package_root(src_root):
            result = verify_drift(base_path, verbose=True)

        assert result["clean"] is True
        assert result["total_drifted"] == 0
        assert result["total_missing"] == 0
        assert result["total_extra"] == 0
        cmd_files = result["components"]["commands"]["files"]
        assert cmd_files["build.md"] == OK
        assert cmd_files["test.md"] == OK

    def test_missing_file_detected(self, tmp_path):
        """Source file not in target → MISSING."""
        src_root, base_path = _setup_full(tmp_path, {
            "commands": {"build.md": ("content", None)},
        })

        with _mock_package_root(src_root):
            result = verify_drift(base_path, verbose=True)

        assert result["clean"] is False
        assert result["total_missing"] >= 1
        assert result["components"]["commands"]["files"]["build.md"] == MISSING

    def test_content_drift_detected(self, tmp_path):
        """Content mismatch → DRIFTED."""
        src_root, base_path = _setup_full(tmp_path, {
            "commands": {"build.md": ("source content", "different content")},
        })

        with _mock_package_root(src_root):
            result = verify_drift(base_path, verbose=True)

        assert result["clean"] is False
        assert result["total_drifted"] >= 1
        assert result["components"]["commands"]["files"]["build.md"] == DRIFTED

    def test_extra_file_detected(self, tmp_path):
        """Target file not in source → EXTRA."""
        src_root, base_path = _setup_full(tmp_path, {
            "commands": {"build.md": ("src", "src")},
        })
        from superclaude.cli.install_paths import COMPONENTS
        tgt_sub = COMPONENTS["commands"][1]
        (base_path / tgt_sub / "orphan.md").write_text("extra", encoding="utf-8")

        with _mock_package_root(src_root):
            result = verify_drift(base_path, verbose=True)

        assert result["total_extra"] >= 1
        assert result["components"]["commands"]["files"]["orphan.md"] == EXTRA

    def test_claude_sc_md_checked(self, tmp_path):
        """CLAUDE_SC.md is separately verified."""
        src_root, base_path = _setup_full(tmp_path)

        with _mock_package_root(src_root):
            result = verify_drift(base_path)

        assert result["claude_sc_md"] == OK

    def test_claude_sc_md_drift(self, tmp_path):
        """CLAUDE_SC.md content mismatch → DRIFTED."""
        src_root, base_path = _setup_full(tmp_path)
        (base_path / "superclaude" / "CLAUDE_SC.md").write_text("modified", encoding="utf-8")

        with _mock_package_root(src_root):
            result = verify_drift(base_path)

        assert result["claude_sc_md"] == DRIFTED

    def test_skills_directory_comparison(self, tmp_path):
        """Skills are compared at SKILL.md level within subdirectories."""
        src_root, base_path = _setup_full(tmp_path, {
            "skills": {"my-skill/SKILL.md": ("skill content", "skill content")},
        })

        with _mock_package_root(src_root):
            result = verify_drift(base_path, verbose=True)

        assert result["components"]["skills"]["files"]["my-skill/SKILL.md"] == OK

    def test_verbose_false_omits_files(self, tmp_path):
        """When verbose=False, file details are not included."""
        src_root, base_path = _setup_full(tmp_path, {
            "commands": {"build.md": ("content", "content")},
        })

        with _mock_package_root(src_root):
            result = verify_drift(base_path, verbose=False)

        assert result["components"]["commands"]["files"] == {}
