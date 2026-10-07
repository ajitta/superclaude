#!/usr/bin/env python3
"""Validate the portable skills under portable-skills/ and package them as one plugin.

Source folders (portable-skills/<skill>/) are plain Agent Skills: no
.claude-plugin/ inside. Codex 0.160 registers a skill folder that contains
.claude-plugin/plugin.json under the plugin namespace (<name>:<name>), and Claude
Code loads such a folder in .claude/skills/ as a `skills-dir` plugin. claude.ai,
however, uploads through Customize > Plugins and rejects a zip without
.claude-plugin/plugin.json. So the one manifest lives in plugin-manifest.json and
is injected only into the generated plugin:

    plugins/<plugin>/                     marketplaces (claude.ai and Claude Code)
      .claude-plugin/plugin.json          point here; from plugin-manifest.json
      skills/<skill>/SKILL.md, references/, agents/openai.yaml   one per skill
    releases/<plugin>.zip                 the same under one top-level <plugin>/

Claude Code scans skills/ by default and loads each skill as <plugin>:<skill>, so
the manifest needs no `skills` key. The zip is byte-reproducible on every OS
(fixed timestamps, modes, create_system, LF line endings for text files).

Usage: python3 portable-skills/package.py [--check]   (stdlib only)
"""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "releases"
PLUGINS = ROOT / "plugins"
MANIFEST = ROOT / "plugin-manifest.json"
ALLOWED_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_BODY_LINES = 200
# A source folder stays a plain skill: a manifest dir in it changes the Codex
# skill name and how Claude Code loads it from .claude/skills/; skills/ and bin/
# are plugin-level directories and stay out of a skill folder.
FORBIDDEN_DIRS = ("skills", "bin", ".claude-plugin", ".codex-plugin")
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt"}


def frontmatter(text: str) -> tuple[dict, dict, str]:
    """Return (top-level keys, metadata map, body). Minimal YAML subset:
    `key: value` lines, plus one indented level of `key: value` under metadata."""
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with '---' on line 1")
    end = text.index("\n---\n", 4)
    block, body = text[4:end], text[end + 5 :]
    data: dict = {}
    meta: dict = {}
    current = None
    for line in block.splitlines():
        if not line.strip():
            continue
        if line.startswith((" ", "\t")):
            if current is None:
                raise ValueError(f"indented line before any key: {line!r}")
            if current == "metadata":
                k, _, v = line.strip().partition(":")
                meta[k.strip()] = v.strip().strip('"')
            else:
                data[current] = (data[current] + "\n" + line.strip()).strip()
            continue
        key, _, value = line.partition(":")
        current = key.strip()
        data[current] = value.strip().strip('"')
    return data, meta, body


def validate(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"{skill_dir.name}: SKILL.md missing"]
    try:
        data, meta, body = frontmatter(skill_md.read_text(encoding="utf-8"))
    except ValueError as e:
        return [f"{skill_dir.name}: {e}"]
    extra = set(data) - ALLOWED_KEYS
    if extra:
        errors.append(
            f"unexpected frontmatter keys (upload would fail): {sorted(extra)}"
        )
    name = data.get("name", "")
    if not (1 <= len(name) <= 64 and NAME_RE.match(name)):
        errors.append(f"invalid name {name!r}")
    if name != skill_dir.name:
        errors.append(f"name {name!r} != folder {skill_dir.name!r}")
    desc = data.get("description", "")
    if not 1 <= len(desc) <= 1024:
        errors.append(f"description length {len(desc)} not in 1..1024")
    if "<" in desc or ">" in desc:
        errors.append("description contains angle brackets")
    if len(data.get("compatibility", "")) > 500:
        errors.append("compatibility > 500 chars")
    for d in FORBIDDEN_DIRS:
        if (skill_dir / d).exists():
            errors.append(
                f"{d}/ must not be in the source folder "
                "(changes the Codex skill name or how the plugin loads)"
            )
    n = len(body.splitlines())
    if n > MAX_BODY_LINES:
        errors.append(f"body {n} lines > {MAX_BODY_LINES}")
    for link in re.findall(r"\]\(([^)#]+)\)", body):
        if not link.startswith("http") and not (skill_dir / link).exists():
            errors.append(f"broken relative link {link}")
    if not meta.get("version"):
        errors.append("metadata.version missing")
    return [f"{skill_dir.name}: {e}" for e in errors]


def validate_manifest() -> list[str]:
    """The plugin manifest that claude.ai upload and both marketplaces need."""
    if not MANIFEST.is_file():
        return ["plugin-manifest.json missing (claude.ai upload needs it)"]
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"plugin-manifest.json is not valid JSON: {e}"]
    errors = []
    name = data.get("name", "")
    if not (1 <= len(name) <= 64 and NAME_RE.match(name)):
        errors.append(f"manifest name {name!r} is not kebab-case")
    for key in ("version", "description"):
        if not data.get(key):
            errors.append(f"manifest {key} missing")
    if "skills" in data:
        errors.append("manifest 'skills' key: skills/ is already scanned by default")
    return [f"plugin-manifest.json: {e}" for e in errors]


def plugin_name() -> str:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))["name"]


def _normalized(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    return data


def plugin_files(skills: list[Path]) -> dict:
    """The plugin: the injected manifest plus every skill folder under
    skills/<skill>/. Keys are paths relative to the plugin folder."""
    files = {".claude-plugin/plugin.json": _normalized(MANIFEST)}
    for skill_dir in skills:
        for f in skill_dir.rglob("*"):
            if f.is_file() and "__pycache__" not in f.parts and f.name != ".DS_Store":
                rel = f.relative_to(skill_dir).as_posix()
                files[f"skills/{skill_dir.name}/{rel}"] = _normalized(f)
    return files


def write_plugin_dir(skills: list[Path]) -> Path:
    """Write plugins/<plugin>/ for marketplaces. claude.ai's marketplace skips a
    plugin folder without .claude-plugin/plugin.json, but a skill folder must
    not carry one (Codex renames it). So marketplaces point at this generated
    copy, and tests keep it identical to the skill folders plus the manifest."""
    out = PLUGINS / plugin_name()
    if out.exists():
        for f in sorted(out.rglob("*"), reverse=True):
            f.unlink() if f.is_file() else f.rmdir()
    for rel, data in plugin_files(skills).items():
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    return out


def package(skills: list[Path]) -> Path:
    name = plugin_name()
    DIST.mkdir(parents=True, exist_ok=True)
    out = DIST / f"{name}.zip"
    files = {f"{name}/{rel}": data for rel, data in plugin_files(skills).items()}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for arcname in sorted(files):
            info = zipfile.ZipInfo(arcname, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3  # unix; ZipInfo defaults to 0 on Windows
            info.external_attr = 0o644 << 16
            zf.writestr(info, files[arcname])
    return out


def main() -> int:
    check_only = "--check" in sys.argv
    skills = sorted(p for p in ROOT.iterdir() if (p / "SKILL.md").is_file())
    errors = validate_manifest() + [e for s in skills for e in validate(s)]
    for e in errors:
        print("ERROR", e)
    if errors:
        return 1
    for s in skills:
        print("ok", s.name)
    if not check_only:
        zip_path = package(skills)
        plugin_dir = write_plugin_dir(skills)
        print("->", zip_path.relative_to(ROOT), "+", plugin_dir.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
