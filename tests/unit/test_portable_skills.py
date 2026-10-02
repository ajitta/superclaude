"""Portable skills under ``portable-skills/`` must stay usable everywhere.

- claude.ai upload rejects frontmatter keys outside the Agent Skills spec and
  (through Customize > Plugins) a zip without ``.claude-plugin/plugin.json``.
- Codex registers a skill folder that contains ``.claude-plugin/`` under the
  plugin namespace (``name:name``), so ``$name`` stops resolving. The manifest
  therefore lives in ``plugin-manifests/`` and is injected only into the zip.
- Claude Code accepts more than either, so a local run never shows these
  failures; only these checks do.
See docs/features/socratic-brainstorm-skill/11-plugin-upload.md and 13-review.md.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import zipfile
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


def _skill_version(skill: Path) -> str:
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---\n")[1])["metadata"]["version"]


def _write_skill(root: Path, name: str, front: str) -> Path:
    d = root / name
    d.mkdir()
    (d / "SKILL.md").write_text(f"---\n{front}---\nbody\n", encoding="utf-8")
    return d


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
def test_codex_invocation_name_is_the_folder_name(skill):
    """Codex resolves `$name` only when the source folder has no plugin
    manifest (with one, it registers `name:name`). The sidecar keeps the skill
    explicit-only and its default prompt must use the same `$name`."""
    assert not (skill / ".claude-plugin").exists()
    assert not (skill / ".codex-plugin").exists()
    data = yaml.safe_load((skill / "agents" / "openai.yaml").read_text("utf-8"))
    assert data["policy"]["allow_implicit_invocation"] is False
    assert f"${skill.name} " in data["interface"]["default_prompt"]


def test_validator_rejects_claude_code_only_key(tmp_path):
    bad = _write_skill(
        tmp_path,
        "demo-skill",
        "name: demo-skill\ndescription: Demo.\ndisable-model-invocation: true\n",
    )
    assert any("unexpected frontmatter keys" in e for e in _packager().validate(bad))


def test_validator_rejects_name_folder_mismatch(tmp_path):
    bad = _write_skill(
        tmp_path, "folder-name", "name: other-name\ndescription: Demo.\n"
    )
    assert any("!= folder" in e for e in _packager().validate(bad))


@pytest.mark.parametrize("subdir", ["skills", "bin", ".claude-plugin"])
def test_validator_rejects_layout_breaking_dirs(tmp_path, subdir):
    bad = _write_skill(
        tmp_path,
        "demo-skill",
        'name: demo-skill\ndescription: Demo.\nmetadata:\n  version: "1.0.0"\n',
    )
    (bad / subdir).mkdir()
    assert any(f"{subdir}/ must not be" in e for e in _packager().validate(bad))


def test_validator_requires_metadata_version(tmp_path):
    bad = _write_skill(tmp_path, "demo-skill", "name: demo-skill\ndescription: Demo.\n")
    assert any("metadata.version missing" in e for e in _packager().validate(bad))


def test_validator_reads_version_not_a_lookalike_key(tmp_path, monkeypatch):
    """`spec-version` must not satisfy the version check."""
    pkg = _packager()
    man = tmp_path / "manifests"
    man.mkdir()
    (man / "demo-skill.json").write_text(
        json.dumps({"name": "demo-skill", "version": "9.9.9", "description": "d"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(pkg, "MANIFESTS", man)
    bad = _write_skill(
        tmp_path,
        "demo-skill",
        'name: demo-skill\ndescription: Demo.\nmetadata:\n  spec-version: "9.9.9"\n'
        '  version: "1.1.0"\n',
    )
    assert any("manifest version '9.9.9'" in e for e in pkg.validate(bad))


def test_validator_rejects_missing_manifest(tmp_path, monkeypatch):
    pkg = _packager()
    monkeypatch.setattr(pkg, "MANIFESTS", tmp_path / "none")
    bad = _write_skill(
        tmp_path,
        "demo-skill",
        'name: demo-skill\ndescription: Demo.\nmetadata:\n  version: "1.0.0"\n',
    )
    assert any("demo-skill.json missing" in e for e in pkg.validate(bad))


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


def test_zip_build_is_os_independent(tmp_path, monkeypatch):
    """ZipInfo sets create_system from sys.platform; a Windows build must still
    match the committed zip, or the freshness test fails there."""
    skill = _SKILLS[0]
    pkg = _packager()
    monkeypatch.setattr(pkg, "DIST", tmp_path)
    monkeypatch.setattr(sys, "platform", "win32")
    rebuilt = pkg.package(skill)
    assert (
        rebuilt.read_bytes() == (_DIR / "releases" / f"{skill.name}.zip").read_bytes()
    )


@pytest.mark.parametrize("skill", _SKILLS, ids=lambda p: p.name)
def test_zip_is_a_plugin_upload(skill):
    """claude.ai's upload requires .claude-plugin/plugin.json inside the zip,
    under the single top-level folder; the manifest must match the skill."""
    zf = zipfile.ZipFile(_DIR / "releases" / f"{skill.name}.zip")
    names = zf.namelist()
    assert f"{skill.name}/SKILL.md" in names
    assert {n.split("/")[0] for n in names} == {skill.name}, "one top-level folder"
    manifest = json.loads(zf.read(f"{skill.name}/.claude-plugin/plugin.json"))
    assert manifest["name"] == skill.name
    assert manifest["version"] == _skill_version(skill)
    assert not any(n.startswith(f"{skill.name}/skills/") for n in names)
    assert not any(n.startswith(f"{skill.name}/bin/") for n in names)


@pytest.mark.parametrize("skill", _SKILLS, ids=lambda p: p.name)
def test_plugin_dir_matches_skill_plus_manifest(skill):
    """plugins/<name>/ is what marketplaces install. claude.ai skips a plugin
    without .claude-plugin/plugin.json, so it carries one; it must otherwise be
    byte-identical to the skill folder."""
    pkg = _packager()
    expected = pkg.plugin_files(skill)
    plugin_dir = _DIR / "plugins" / skill.name
    actual = {
        f.relative_to(plugin_dir).as_posix(): f.read_bytes().replace(b"\r\n", b"\n")
        for f in plugin_dir.rglob("*")
        if f.is_file()
    }
    assert actual == expected, (
        "stale plugins/ copy; run: python3 portable-skills/package.py"
    )
    manifest = json.loads(actual[".claude-plugin/plugin.json"])
    assert manifest["name"] == skill.name
    assert manifest["version"] == _skill_version(skill)


def test_marketplace_lists_every_portable_skill():
    """A stale marketplace entry installs nothing while `claude plugin validate`
    still passes. Entries point at the generated plugin folders, which carry
    plugin.json (claude.ai's marketplace skips plugins without one)."""
    market = json.loads(
        (_ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
    )
    entries = {p["name"]: p for p in market["plugins"]}
    assert set(entries) == {s.name for s in _SKILLS}
    for skill in _SKILLS:
        assert (
            entries[skill.name]["source"] == f"./portable-skills/plugins/{skill.name}"
        )
        assert "version" not in entries[skill.name], "plugin.json owns the version"
