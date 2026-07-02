"""Tests for /sc:init docs-scaffold templates and their installer wiring."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
TEMPLATES_SRC = REPO_ROOT / "src" / "superclaude" / "templates" / "docs-scaffold"
INIT_MD = REPO_ROOT / "src" / "superclaude" / "commands" / "init.md"

EXPECTED_TEMPLATES = {
    "PRD.md",
    "ARCHITECTURE.md",
    "ADR-0001-template.md",
    "UI-GUIDE.md",
}


class TestTemplateSourceTree:
    def test_templates_directory_exists(self):
        assert TEMPLATES_SRC.is_dir(), f"missing: {TEMPLATES_SRC}"

    def test_all_expected_templates_present(self):
        present = {p.name for p in TEMPLATES_SRC.glob("*.md")}
        missing = EXPECTED_TEMPLATES - present
        assert not missing, f"missing templates: {missing}"

    def test_prd_has_required_sections(self):
        body = (TEMPLATES_SRC / "PRD.md").read_text(encoding="utf-8")
        for section in ("## Goal", "## Core Features", "## MVP Exclusions"):
            assert section in body, f"PRD missing section: {section}"

    def test_architecture_has_required_sections(self):
        body = (TEMPLATES_SRC / "ARCHITECTURE.md").read_text(encoding="utf-8")
        for section in ("## Directory Layout", "## Tech Stack", "## Data Flow"):
            assert section in body, f"ARCHITECTURE missing section: {section}"

    def test_adr_has_required_sections(self):
        body = (TEMPLATES_SRC / "ADR-0001-template.md").read_text(encoding="utf-8")
        for section in ("## Context", "## Decision", "## Consequences"):
            assert section in body, f"ADR missing section: {section}"


class TestInstallerShipsTemplates:
    def test_install_templates_component(self, tmp_path):
        """install_component('templates') ships docs-scaffold outside commands/."""
        from superclaude.cli.install_components import install_component

        installed, skipped, failed, failed_names = install_component(
            component="templates",
            base_path=tmp_path,
            force=True,
            scope="user",
        )
        assert failed == 0, f"install failed: {failed_names}"

        target = tmp_path / "superclaude" / "templates" / "docs-scaffold"
        assert target.is_dir(), f"templates dir not shipped to {target}"
        present = {p.name for p in target.glob("*.md")}
        missing = EXPECTED_TEMPLATES - present
        assert not missing, f"missing after install: {missing}"

    def test_templates_not_installed_under_commands(self, tmp_path):
        """Regression: templates must NOT land under commands/ — CC would
        discover them as slash commands."""
        from superclaude.cli.install_components import install_all

        install_all(base_path=tmp_path, force=True, scope="user")
        bad = tmp_path / "commands" / "sc" / "templates"
        assert not bad.exists(), (
            "templates must not ship under commands/sc/ — would be picked "
            "up as /sc:templates:* slash commands"
        )

    def test_install_is_idempotent_for_templates(self, tmp_path):
        from superclaude.cli.install_components import install_component

        # First install
        install_component(
            component="templates",
            base_path=tmp_path,
            force=True,
            scope="user",
        )
        target = tmp_path / "superclaude" / "templates" / "docs-scaffold"
        prd_path = target / "PRD.md"
        assert prd_path.is_file()
        original_mtime = prd_path.stat().st_mtime

        # Second install without force — should skip
        installed, skipped, failed, _ = install_component(
            component="templates",
            base_path=tmp_path,
            force=False,
            scope="user",
        )
        assert failed == 0
        assert skipped >= 1, "expected at least the templates subdir to skip"
        assert prd_path.stat().st_mtime == original_mtime


class TestInitCommandDeclaresTaskI:
    """init.md must declare task [i] across menu, dependency_graph,
    task_outputs, safety_rules, and the --full preset."""

    @pytest.fixture
    def init_body(self):
        return INIT_MD.read_text(encoding="utf-8")

    def test_menu_has_task_i(self, init_body):
        assert "[i]" in init_body and "docs" in init_body.lower(), (
            "task [i] missing from init.md menu"
        )

    def test_dependency_graph_lists_i(self, init_body):
        # Task [i] has no deps → should appear in Batch 1
        dep_section = init_body.split("dependency_graph")[1].split(
            "</dependency_graph>"
        )[0]
        assert "i" in dep_section.replace(",", " ").split(), (
            "task [i] not listed in dependency_graph"
        )

    def test_task_outputs_row_for_i(self, init_body):
        # Look for a table row starting with "| i |"
        assert "| i |" in init_body, "task_outputs row for [i] missing"

    def test_safety_rules_mention_docs_scaffold(self, init_body):
        safety = init_body.split("safety_rules")[1].split("</safety_rules>")[0]
        assert "docs" in safety.lower() and "idempotent" in safety.lower(), (
            "safety_rules must cover docs-scaffold idempotency"
        )

    def test_full_preset_includes_i(self, init_body):
        # --full preset must list i among selected tasks
        assert "a,b,c,d,e,f,g,h,i" in init_body, "--full preset must include task i"
