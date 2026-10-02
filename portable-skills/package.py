#!/usr/bin/env python3
"""Validate portable skills under portable-skills/ and package them for upload.

Checks each skill against the Agent Skills spec subset that every target
accepts (claude.ai upload / Skills API reject any other frontmatter key),
then writes portable-skills/releases/<name>.zip (committed) with the skill folder at the zip root.

Usage: python3 portable-skills/package.py [--check]   (stdlib only)
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "releases"
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


def frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with '---' on line 1")
    end = text.index("\n---\n", 4)
    block, body = text[4:end], text[end + 5 :]
    data: dict = {}
    current = None
    for line in block.splitlines():
        if not line.strip():
            continue
        if line.startswith((" ", "\t")):
            if current is None:
                raise ValueError(f"indented line before any key: {line!r}")
            data[current] = (data[current] + "\n" + line.strip()).strip()
            continue
        key, _, value = line.partition(":")
        current = key.strip()
        data[current] = value.strip().strip('"')
    return data, body


def validate(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"{skill_dir.name}: SKILL.md missing"]
    try:
        data, body = frontmatter(skill_md.read_text(encoding="utf-8"))
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
    n = len(body.splitlines())
    if n > MAX_BODY_LINES:
        errors.append(f"body {n} lines > {MAX_BODY_LINES}")
    for link in re.findall(r"\]\(([^)#]+)\)", body):
        if not link.startswith("http") and not (skill_dir / link).exists():
            errors.append(f"broken relative link {link}")
    return [f"{skill_dir.name}: {e}" for e in errors]


def package(skill_dir: Path) -> Path:
    DIST.mkdir(parents=True, exist_ok=True)
    out = DIST / f"{skill_dir.name}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(skill_dir.rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts and f.name != ".DS_Store":
                info = zipfile.ZipInfo(
                    f.relative_to(skill_dir.parent).as_posix(), (1980, 1, 1, 0, 0, 0)
                )
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                zf.writestr(info, f.read_bytes())
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
