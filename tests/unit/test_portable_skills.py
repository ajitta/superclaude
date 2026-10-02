"""Portable skills under ``portable-skills/`` must stay uploadable everywhere.

claude.ai upload and the Skills API reject any frontmatter key outside the Agent
Skills spec (``Unexpected key(s) in SKILL.md frontmatter``), and the spec requires
``name`` to match the folder. Claude Code accepts more keys, so a local run never
shows the failure; only this check does. See
docs/features/socratic-brainstorm-skill/02-research.md §3.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

_ROOT = Path(__file__).resolve().parents[2]
_DIR = _ROOT / "portable-skills"
_SKILLS = sorted(p for p in _DIR.iterdir() if (p / "SKILL.md").is_file())


def _packager():
    spec = importlib.util.spec_from_file_location("pkg", _DIR / "package.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_at_least_one_portable_skill():
    assert _SKILLS, "portable-skills/ has no SKILL.md folders"


@pytest.mark.parametrize("skill", _SKILLS, ids=lambda p: p.name)
def test_validator_passes(skill):
    assert _packager().validate(skill) == []


@pytest.mark.parametrize("skill", _SKILLS, ids=lambda p: p.name)
def test_frontmatter_parses_as_yaml_with_spec_keys_only(skill):
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    data = yaml.safe_load(text.split("---\n")[1])
    assert set(data) <= _packager().ALLOWED_KEYS
    assert data["name"] == skill.name
    assert 1 <= len(data["description"]) <= 1024
    meta = data.get("metadata", {})
    assert all(isinstance(v, str) for v in meta.values()), (
        "metadata values must be strings"
    )


@pytest.mark.parametrize("skill", _SKILLS, ids=lambda p: p.name)
def test_codex_sidecar_keeps_skill_explicit_only(skill):
    sidecar = skill / "agents" / "openai.yaml"
    assert sidecar.is_file()
    data = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    assert data["policy"]["allow_implicit_invocation"] is False


def test_validator_rejects_claude_code_only_key(tmp_path):
    bad = tmp_path / "demo-skill"
    bad.mkdir()
    (bad / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Demo.\ndisable-model-invocation: true\n---\nbody\n",
        encoding="utf-8",
    )
    errors = _packager().validate(bad)
    assert any("unexpected frontmatter keys" in e for e in errors)


def test_validator_rejects_name_folder_mismatch(tmp_path):
    bad = tmp_path / "folder-name"
    bad.mkdir()
    (bad / "SKILL.md").write_text(
        "---\nname: other-name\ndescription: Demo.\n---\nbody\n", encoding="utf-8"
    )
    assert any("!= folder" in e for e in _packager().validate(bad))


@pytest.mark.parametrize("skill", _SKILLS, ids=lambda p: p.name)
def test_committed_zip_matches_source(skill, tmp_path, monkeypatch):
    """releases/<name>.zip is what users upload; it must not lag the source."""
    committed = _DIR / "releases" / f"{skill.name}.zip"
    assert committed.is_file(), "run: python3 portable-skills/package.py"
    pkg = _packager()
    monkeypatch.setattr(pkg, "DIST", tmp_path)
    rebuilt = pkg.package(skill)
    assert rebuilt.read_bytes() == committed.read_bytes(), (
        "stale zip; run: python3 portable-skills/package.py"
    )


@pytest.mark.parametrize("skill", _SKILLS, ids=lambda p: p.name)
def test_zip_is_a_plugin_upload(skill):
    """claude.ai's upload requires .claude-plugin/plugin.json inside the zip,
    at the root or under one top-level folder. Without it the upload fails."""
    import zipfile

    names = zipfile.ZipFile(_DIR / "releases" / f"{skill.name}.zip").namelist()
    assert f"{skill.name}/.claude-plugin/plugin.json" in names
    assert f"{skill.name}/SKILL.md" in names
    assert {n.split("/")[0] for n in names} == {skill.name}, "one top-level folder only"


def test_validator_rejects_missing_manifest(tmp_path):
    bad = tmp_path / "demo-skill"
    bad.mkdir()
    (bad / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Demo.\n---\nbody\n", encoding="utf-8"
    )
    assert any("plugin.json missing" in e for e in _packager().validate(bad))


def test_marketplace_lists_every_portable_skill():
    """A renamed plugin.json with a stale marketplace entry installs nothing,
    while `claude plugin validate` still passes. Pin the two together."""
    market = json.loads(
        (_ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
    )
    entries = {p["name"]: p["source"] for p in market["plugins"]}
    assert set(entries) == {s.name for s in _SKILLS}
    for skill in _SKILLS:
        assert entries[skill.name] == f"./portable-skills/{skill.name}"
        manifest = json.loads(
            (skill / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        assert manifest["name"] == skill.name
