#!/usr/bin/env python3
"""Validate portable skills under portable-skills/ and package them for upload.

Source folders (portable-skills/<name>/) are plain Agent Skills: no
.claude-plugin/ inside. Codex 0.160 registers a skill folder that contains
.claude-plugin/plugin.json under the plugin namespace (<name>:<name>), and Claude
Code loads such a folder in .claude/skills/ as a `skills-dir` plugin. claude.ai,
however, uploads through Customize > Plugins and rejects a zip without
.claude-plugin/plugin.json. So the manifest lives in plugin-manifests/<name>.json
and is injected only into the release zip:

    releases/<name>.zip
      <name>/.claude-plugin/plugin.json   (from plugin-manifests/<name>.json)
      <name>/SKILL.md, references/, agents/openai.yaml

A plugin with SKILL.md at its root and no skills/ directory loads as a single
skill. The zip is byte-reproducible on every OS (fixed timestamps, modes,
create_system, LF line endings for text files).

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
MANIFESTS = ROOT / "plugin-manifests"
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
# skills/ voids the single-skill-at-root rule; claude.ai refuses a plugin with a
# top-level bin/; a manifest dir in the source changes the Codex skill name.
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
    version = meta.get("version")
    if not version:
        errors.append("metadata.version missing")
    errors.extend(_validate_manifest(name, version))
    return [f"{skill_dir.name}: {e}" for e in errors]


def _validate_manifest(name: str, version: str | None) -> list[str]:
    path = MANIFESTS / f"{name}.json"
    if not path.is_file():
        return [f"plugin-manifests/{name}.json missing (claude.ai upload needs it)"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"plugin-manifests/{name}.json is not valid JSON: {e}"]
    errors = []
    if data.get("name") != name:
        errors.append(f"manifest name {data.get('name')!r} != skill name {name!r}")
    if version and data.get("version") != version:
        errors.append(
            f"manifest version {data.get('version')!r} != SKILL.md metadata.version {version!r}"
        )
    if not data.get("description"):
        errors.append("manifest description missing")
    if "skills" in data:
        errors.append("manifest 'skills' key voids the single-skill layout")
    return errors


def _normalized(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    return data


def package(skill_dir: Path) -> Path:
    DIST.mkdir(parents=True, exist_ok=True)
    out = DIST / f"{skill_dir.name}.zip"
    files = {
        f.relative_to(skill_dir.parent).as_posix(): _normalized(f)
        for f in skill_dir.rglob("*")
        if f.is_file() and "__pycache__" not in f.parts and f.name != ".DS_Store"
    }
    files[f"{skill_dir.name}/.claude-plugin/plugin.json"] = _normalized(
        MANIFESTS / f"{skill_dir.name}.json"
    )
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
    errors = [e for s in skills for e in validate(s)]
    for e in errors:
        print("ERROR", e)
    if errors:
        return 1
    for s in skills:
        print("ok", s.name, "" if check_only else f"-> {package(s)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
