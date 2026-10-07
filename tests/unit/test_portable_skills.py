"""Portable skills under ``portable-skills/`` must stay usable everywhere.

- claude.ai upload rejects frontmatter keys outside the Agent Skills spec and
  (through Customize > Plugins) a zip without ``.claude-plugin/plugin.json``.
- Codex registers a skill folder that contains ``.claude-plugin/`` under the
  plugin namespace (``name:name``), so ``$name`` stops resolving. The manifest
  therefore lives in ``plugin-manifest.json`` and is injected only into the
  generated plugin, which holds every skill under ``skills/<skill>/``.
- Claude Code accepts more than either, so a local run never shows these
  failures; only these checks do.
See docs/features/socratic-brainstorm-skill/11-plugin-upload.md, 13-review.md
and docs/features/portable-skills-single-plugin/02-research.md.
"""

from __future__ import annotations

import importlib.util
import json
import re
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


def _plugin_name() -> str:
    manifest = (_DIR / "plugin-manifest.json").read_text(encoding="utf-8")
    return json.loads(manifest)["name"]


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


def test_manifest_passes():
    assert _packager().validate_manifest() == []


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


def test_validator_reads_version_not_a_lookalike_key(tmp_path):
    """`spec-version` must not satisfy the version check."""
    bad = _write_skill(
        tmp_path,
        "demo-skill",
        'name: demo-skill\ndescription: Demo.\nmetadata:\n  spec-version: "9.9.9"\n',
    )
    assert any("metadata.version missing" in e for e in _packager().validate(bad))


def test_validator_rejects_missing_manifest(tmp_path, monkeypatch):
    pkg = _packager()
    monkeypatch.setattr(pkg, "MANIFEST", tmp_path / "none.json")
    assert any("plugin-manifest.json missing" in e for e in pkg.validate_manifest())


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("{", "not valid JSON"),
        (json.dumps({"name": "demo", "description": "d"}), "version missing"),
        (json.dumps({"name": "demo", "version": "1.0.0"}), "description missing"),
        (
            json.dumps({"name": "Demo Plugin", "version": "1.0.0", "description": "d"}),
            "not kebab-case",
        ),
        (
            json.dumps(
                {
                    "name": "demo",
                    "version": "1.0.0",
                    "description": "d",
                    "skills": "./skills/",
                }
            ),
            "'skills' key",
        ),
    ],
)
def test_manifest_validator_rejects(tmp_path, monkeypatch, text, message):
    pkg = _packager()
    path = tmp_path / "plugin-manifest.json"
    path.write_text(text, encoding="utf-8")
    monkeypatch.setattr(pkg, "MANIFEST", path)
    assert any(message in e for e in pkg.validate_manifest())


def test_committed_zip_matches_source(tmp_path, monkeypatch):
    """releases/<plugin>.zip is what users upload; it must not lag the source."""
    committed = _DIR / "releases" / f"{_plugin_name()}.zip"
    assert committed.is_file(), "run: python3 portable-skills/package.py"
    pkg = _packager()
    monkeypatch.setattr(pkg, "DIST", tmp_path)
    rebuilt = pkg.package(_SKILLS)
    assert rebuilt.read_bytes() == committed.read_bytes(), (
        "stale zip; run: python3 portable-skills/package.py"
    )


def test_zip_build_is_os_independent(tmp_path, monkeypatch):
    """ZipInfo sets create_system from sys.platform; a Windows build must still
    match the committed zip, or the freshness test fails there."""
    pkg = _packager()
    monkeypatch.setattr(pkg, "DIST", tmp_path)
    monkeypatch.setattr(sys, "platform", "win32")
    rebuilt = pkg.package(_SKILLS)
    committed = _DIR / "releases" / f"{_plugin_name()}.zip"
    assert rebuilt.read_bytes() == committed.read_bytes()


def test_releases_hold_only_the_plugin_zip():
    """The per-skill zips were replaced by the one plugin zip once its
    claude.ai upload was confirmed; a leftover zip would be a second install."""
    names = sorted(p.name for p in (_DIR / "releases").iterdir())
    assert names == [f"{_plugin_name()}.zip"]


def test_zip_is_a_plugin_upload():
    """claude.ai's upload requires .claude-plugin/plugin.json inside the zip,
    under the single top-level folder. Each skill sits in skills/<skill>/; a
    SKILL.md at the plugin root would load the plugin as that one skill."""
    name = _plugin_name()
    with zipfile.ZipFile(_DIR / "releases" / f"{name}.zip") as zf:
        names = zf.namelist()
        manifest = json.loads(zf.read(f"{name}/.claude-plugin/plugin.json"))
    assert {n.split("/")[0] for n in names} == {name}, "one top-level folder"
    assert manifest["name"] == name
    for skill in _SKILLS:
        assert f"{name}/skills/{skill.name}/SKILL.md" in names
    assert f"{name}/SKILL.md" not in names
    assert not any(n.startswith(f"{name}/bin/") for n in names)


def test_plugin_dir_matches_skills_plus_manifest():
    """plugins/<plugin>/ is what marketplaces install. claude.ai skips a plugin
    without .claude-plugin/plugin.json, so it carries one; the rest must be
    byte-identical to the skill folders."""
    pkg = _packager()
    plugin_dir = _DIR / "plugins" / _plugin_name()
    actual = {
        f.relative_to(plugin_dir).as_posix(): f.read_bytes().replace(b"\r\n", b"\n")
        for f in plugin_dir.rglob("*")
        if f.is_file()
    }
    assert actual == pkg.plugin_files(_SKILLS), (
        "stale plugins/ copy; run: python3 portable-skills/package.py"
    )
    assert [p.name for p in (_DIR / "plugins").iterdir()] == [_plugin_name()], (
        "plugins/ holds only the one plugin"
    )


def test_release_record_matches_content():
    """Claude Code updates an installed plugin only when its version changes,
    so skill files that changed under the same plugin version never reach
    users. plugin-release.json records the skill-file digest per version."""
    assert _packager().check_release(_SKILLS) == []


def _release_fixture(tmp_path, monkeypatch, version, recorded):
    pkg = _packager()
    manifest = tmp_path / "plugin-manifest.json"
    manifest.write_text(
        json.dumps({"name": "demo", "version": version, "description": "d"}),
        encoding="utf-8",
    )
    release = tmp_path / "plugin-release.json"
    release.write_text(json.dumps(recorded), encoding="utf-8")
    monkeypatch.setattr(pkg, "MANIFEST", manifest)
    monkeypatch.setattr(pkg, "RELEASE", release)
    skill = _write_skill(
        tmp_path,
        "demo-skill",
        'name: demo-skill\ndescription: Demo.\nmetadata:\n  version: "1.0.0"\n',
    )
    return pkg, [skill], release


def test_changed_skills_need_a_new_plugin_version(tmp_path, monkeypatch):
    recorded = {"version": "1.0.0", "digest": "0" * 64}
    pkg, skills, release = _release_fixture(tmp_path, monkeypatch, "1.0.0", recorded)
    assert any("bump version" in e for e in pkg.check_release(skills))
    assert any("bump version" in e for e in pkg.record_release(skills))
    assert json.loads(release.read_text(encoding="utf-8")) == recorded


def test_new_plugin_version_is_recorded(tmp_path, monkeypatch):
    recorded = {"version": "1.0.0", "digest": "0" * 64}
    pkg, skills, release = _release_fixture(tmp_path, monkeypatch, "1.0.1", recorded)
    assert any("run package.py" in e for e in pkg.check_release(skills))
    assert pkg.record_release(skills) == []
    assert json.loads(release.read_text(encoding="utf-8")) == {
        "version": "1.0.1",
        "digest": pkg.content_digest(skills),
    }
    assert pkg.check_release(skills) == []


_HANGUL = re.compile("[ᄀ-ᇿ㄰-㆏ꥠ-꥿가-퟿]")


def test_shipped_plugin_has_no_hangul():
    """The installed plugin is English only; replies follow the user's
    language through each skill's "Reply in the user's language" rule."""
    shipped = dict(_packager().plugin_files(_SKILLS))
    plugin_dir = _DIR / "plugins" / _plugin_name()
    for f in plugin_dir.rglob("*"):
        if f.is_file():
            rel = f.relative_to(_DIR).as_posix()
            shipped[rel] = f.read_bytes()
    hits = [
        f"{rel}:{n}"
        for rel, data in shipped.items()
        for n, line in enumerate(data.decode("utf-8").splitlines(), 1)
        if _HANGUL.search(line)
    ]
    assert not hits, f"Hangul in shipped files: {hits}"


def _marketplace() -> dict:
    path = _ROOT / ".claude-plugin" / "marketplace.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_marketplace_lists_the_one_plugin():
    """A stale marketplace entry installs nothing while `claude plugin validate`
    still passes. The entry points at the generated plugin folder, which carries
    plugin.json (claude.ai's marketplace skips plugins without one)."""
    entries = _marketplace()["plugins"]
    assert [e["name"] for e in entries] == [_plugin_name()]
    assert entries[0]["source"] == f"./portable-skills/plugins/{_plugin_name()}"
    assert (_ROOT / entries[0]["source"]).is_dir()
    assert "version" not in entries[0], "plugin.json owns the version"


def test_marketplace_renames_keep_old_installs():
    """Each skill once shipped as its own plugin. Removing those entries leaves
    existing installs failing to load ("not found in marketplace"); `renames`
    moves them to the one plugin at the next session start (02-research, cases
    A and B). The map is append-only history: never drop a key."""
    market = _marketplace()
    renames = market.get("renames", {})
    current = {e["name"] for e in market["plugins"]}
    old = {"socratic-brainstorm": "socratic", "socratic-elenchus": "socratic"}
    assert old.items() <= renames.items()
    assert all(v is None or v in current for v in renames.values())
    assert not current & set(renames)


def test_install_docs_match_the_marketplace():
    """The Pages site and the README copy the install commands by hand; tie
    them to marketplace.json so a renamed plugin cannot leave them stale."""
    market = _marketplace()
    install = [f"/plugin install {e['name']}@{market['name']}" for e in market["plugins"]]
    stale = [f"/plugin install {old}@{market['name']}" for old in market["renames"]]
    pages = (_ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    readme = (_DIR / "README.md").read_text(encoding="utf-8")
    for name, doc in (("docs/index.html", pages), ("portable-skills/README.md", readme)):
        assert all(cmd in doc for cmd in install), f"{name} lacks {install}"
        assert not any(cmd in doc for cmd in stale), f"{name} still installs {stale}"
    for skill in _SKILLS:
        assert f"/{_plugin_name()}:{skill.name}" in pages
