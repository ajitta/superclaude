"""Validate a file Claude reads as instructions: the /sc-author Check step.

Claude Code loads a skill, subagent, command, output style or memory file with
a misspelled field, an unparseable frontmatter or a dangling reference without
any error, so these failures stay invisible until something is checked.

Rule codes and their grades are in RULES; the design and the reason for each
rule: docs/features/authoring-skill/04a-design-checker.md. Only rules that give
the same answer for the same input belong here; anything that needs judgment
about what a sentence means stays with the skill's references/quality.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

from .install_paths import _get_package_root

TYPES = ("skill", "agent", "command", "output-style", "memory", "generic")
FORMATS = ("md", "xml")

# Code -> grade. Every code has a violating and a passing case in
# tests/unit/test_author_check.py.
RULES = {
    "F1": "error",  # frontmatter missing where required, or not parseable
    "F2": "error",  # required field missing
    "F3": "error",  # field this type does not support (silently ignored)
    "F4": "warning",  # field not listed for this type
    "F5": "error",  # name rule
    "F6": "error",  # skill description + when_to_use over the listing limit
    "F7": "warning",  # description in first or second person
    "R1": "error",  # SKILL.md links a file that does not exist
    "R2": "warning",  # a reference file links another file (depth > 1)
    "R3": "warning",  # reference file over 100 lines without a table of contents
    "S1": "warning",  # over the size target
    "S2": "warning",  # three or more all-caps emphasis words
    "X1": "error",  # (xml) not exactly one root element, or bare text outside it
    "X2": "error",  # (xml) unbalanced or misnested tags
    "X7": "error",  # (xml) output styles take a plain body
}

# A tag is `<name ...>`, `</name>` or `<name/>`. Prose like `<3`, `<5KB` or `<=`
# is text. Tag names follow the project, so hyphens are allowed.
TAG_RE = re.compile(r"<(/?)([a-z][a-z0-9_-]*)(\s[^<>]*?)?(/?)>")

_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
_INLINE_CODE_RE = re.compile(r"(`+)(.+?)\1")
_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
_IMPORT_LINE_RE = re.compile(r"^\s*@\S+\s*$")
_EMPHASIS_RE = re.compile(r"\b(MUST|ALWAYS|NEVER|CRITICAL|IMPORTANT)\b")
_MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_SKILL_DIR_REF_RE = re.compile(r"\$\{CLAUDE_SKILL_DIR\}/([^\s`)\]\"'<>]+)")
_SKILL_NAME_RE = re.compile(r"^[a-z0-9-]+$")
_PERSON_RE = re.compile(r"^\s*(I|I'm|I'll|We|You)\b|\b(I|You|We) can\b")
_TOC_HEADING_RE = re.compile(r"^#+\s*(table of )?contents\b", re.I | re.M)
_MEMORY_NAMES = ("CLAUDE.md", "CLAUDE.local.md", "AGENTS.md")
_REFERENCE_TOC_LINES = 100


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    code: str
    severity: str
    message: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.code} {self.severity}: {self.message}"


@dataclass
class _Doc:
    """One file split into frontmatter and body, with line bookkeeping."""

    path: Path
    text: str
    has_frontmatter: bool
    frontmatter: dict | None
    frontmatter_error: str | None
    field_lines: dict
    body: str
    body_start: int  # 1-based line number of the first body line


@lru_cache(maxsize=1)
def load_fields() -> dict:
    """The packaged fields.yaml — the same file the skill's references ship."""
    path = _get_package_root() / "skills" / "sc-author" / "references" / "fields.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def infer_type(path: Path) -> str:
    """Document type from its location; anything unrecognised is generic."""
    posix = "/" + path.as_posix().lstrip("/")
    if path.name == "SKILL.md" and "/skills/" in posix:
        return "skill"
    if re.search(r"/agents/[^/]+\.md$", posix):
        return "agent"
    if re.search(r"/commands/.+\.md$", posix):
        return "command"
    if re.search(r"/output-styles/[^/]+\.md$", posix):
        return "output-style"
    if path.name in _MEMORY_NAMES or re.search(r"/rules/.+\.md$", posix):
        return "memory"
    return "generic"


def mask_code(text: str, inline: bool = True) -> str:
    """Blank out fenced code (and inline code) keeping every line and column."""
    out = []
    fence = None
    for line in text.split("\n"):
        match = _FENCE_RE.match(line)
        if fence:
            if (
                match
                and match.group(1)[0] == fence[0]
                and len(match.group(1)) >= len(fence)
            ):
                fence = None
            out.append(" " * len(line))
            continue
        if match:
            fence = match.group(1)
            out.append(" " * len(line))
            continue
        if inline:
            line = _INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), line)
        out.append(line)
    return "\n".join(out)


def _mask_comments(text: str) -> str:
    return _COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def infer_format(body: str) -> str:
    """xml when the first line after blank, comment and `@path` lines is a tag."""
    for line in _mask_comments(body).split("\n"):
        stripped = line.strip()
        if not stripped or _IMPORT_LINE_RE.match(line):
            continue
        return "xml" if TAG_RE.match(stripped) else "md"
    return "md"


def _split(path: Path) -> _Doc:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return _Doc(path, text, False, None, None, {}, text, 1)
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return _Doc(
            path, text, True, None, "frontmatter has no closing ---", {}, text, 1
        )
    raw = "\n".join(lines[1:end])
    field_lines = {}
    for offset, line in enumerate(lines[1:end], start=2):
        key = re.match(r"^([A-Za-z0-9_-]+)\s*:", line)
        if key:
            field_lines.setdefault(key.group(1), offset)
    body = "\n".join(lines[end + 1 :])
    try:
        data = yaml.safe_load(raw) if raw.strip() else {}
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" (line {mark.line + 2})" if mark is not None else ""
        return _Doc(
            path, text, True, None, f"YAML does not parse{where}", {}, body, end + 2
        )
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return _Doc(
            path, text, True, None, "frontmatter is not a mapping", {}, body, end + 2
        )
    return _Doc(path, text, True, data, None, field_lines, body, end + 2)


class _Report:
    def __init__(self, path: Path):
        self.path = str(path)
        self.findings: list[Finding] = []

    def add(self, code: str, line: int, message: str, severity: str | None = None):
        self.findings.append(
            Finding(self.path, line, code, severity or RULES[code], message)
        )


def _check_frontmatter(doc: _Doc, type_: str, report: _Report) -> None:
    spec = load_fields()["types"].get(type_)
    if spec is None:
        return
    if doc.frontmatter_error:
        report.add(
            "F1",
            1,
            f"{doc.frontmatter_error} — Claude Code loads the file with no fields",
        )
        return
    if not doc.has_frontmatter:
        if spec["frontmatter"] == "required":
            report.add("F1", 1, f"no frontmatter — a {type_} needs one")
        return
    fields = doc.frontmatter or {}
    for name in spec["required"]:
        if name not in fields:
            report.add("F2", 1, f"required field `{name}` is missing")
    known = set(spec["required"]) | set(spec["optional"])
    for name in fields:
        line = doc.field_lines.get(name, 1)
        if name in spec["unsupported"]:
            report.add(
                "F3", line, f"`{name}` is not supported on a {type_}; it is ignored"
            )
        elif name not in known:
            report.add(
                "F4",
                line,
                f"`{name}` is not a known {type_} field — a typo is ignored silently",
            )
    _check_name(fields, type_, spec, doc, report)
    _check_description(fields, type_, spec, doc, report)


def _check_name(fields: dict, type_: str, spec: dict, doc: _Doc, report) -> None:
    name = fields.get("name")
    if name is None:
        return
    name = str(name)
    line = doc.field_lines.get("name", 1)
    limit = spec["limits"].get("name_chars")
    if type_ == "skill":
        if not _SKILL_NAME_RE.match(name) or len(name) > limit:
            report.add(
                "F5",
                line,
                f"skill name `{name}` must be lowercase letters, digits and "
                f"hyphens, at most {limit} characters",
            )
    elif type_ == "agent":
        if ":" in name or name.startswith("-") or len(name) > limit:
            report.add(
                "F5",
                line,
                f"agent name `{name}` must not contain `:` or start with `-`, "
                f"at most {limit} characters",
            )


def _check_description(fields: dict, type_: str, spec: dict, doc, report) -> None:
    description = fields.get("description")
    if description is None:
        return
    description = str(description)
    line = doc.field_lines.get("description", 1)
    limit = spec["limits"].get("listing_chars")
    if limit:
        total = len(description) + len(str(fields.get("when_to_use") or ""))
        if total > limit:
            report.add(
                "F6",
                line,
                f"description + when_to_use is {total} characters; the skill "
                f"listing cuts it at {limit}",
            )
    if type_ in ("skill", "agent", "command") and _PERSON_RE.search(description):
        report.add(
            "F7",
            line,
            "description is in first or second person; write it in third person",
        )


def _links(text: str, start: int) -> list[tuple[str, int]]:
    """Relative link targets and ${CLAUDE_SKILL_DIR} references, with lines."""
    found = []
    for number, line in enumerate(mask_code(text, inline=False).split("\n"), start):
        for match in _MD_LINK_RE.finditer(line):
            target = match.group(1).split("#", 1)[0]
            if target and not re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                found.append((target, number))
        for match in _SKILL_DIR_REF_RE.finditer(line):
            found.append(("${CLAUDE_SKILL_DIR}/" + match.group(1), number))
    return found


def _resolve(target: str, base: Path, skill_dir: Path) -> Path:
    if target.startswith("${CLAUDE_SKILL_DIR}/"):
        return skill_dir / target[len("${CLAUDE_SKILL_DIR}/") :]
    return base / target


def _check_refs(doc: _Doc, report: _Report) -> None:
    skill_dir = doc.path.parent
    for target, line in _links(doc.body, doc.body_start):
        resolved = _resolve(target, skill_dir, skill_dir)
        if not resolved.exists():
            report.add("R1", line, f"`{target}` does not exist")
            continue
        if resolved.suffix != ".md" or resolved == doc.path:
            continue
        _check_reference_file(resolved, skill_dir, report)


def _check_reference_file(path: Path, skill_dir: Path, report: _Report) -> None:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    for target, line in _links(text, 1):
        resolved = _resolve(target, path.parent, skill_dir).resolve()
        if resolved != path.resolve() and resolved.exists():
            report.findings.append(
                Finding(
                    str(path),
                    line,
                    "R2",
                    RULES["R2"],
                    f"links `{target}`; link every file from SKILL.md instead "
                    "(nested references may be read partially)",
                )
            )
    lines = text.split("\n")
    if len(lines) > _REFERENCE_TOC_LINES:
        head = "\n".join(lines[:40])
        if not (_TOC_HEADING_RE.search(head) or head.count("](#") >= 3):
            report.findings.append(
                Finding(
                    str(path),
                    1,
                    "R3",
                    RULES["R3"],
                    f"{len(lines)} lines and no table of contents at the top",
                )
            )


def _check_size(doc: _Doc, type_: str, report: _Report) -> None:
    limits = (load_fields()["types"].get(type_) or {}).get("limits", {})
    if type_ == "skill" and "body_lines" in limits:
        count = len(doc.body.rstrip("\n").split("\n"))
        if count > limits["body_lines"]:
            report.add(
                "S1", 1, f"body is {count} lines; keep it under {limits['body_lines']}"
            )
    if type_ == "memory" and "lines" in limits:
        count = len(doc.text.rstrip("\n").split("\n"))
        if count > limits["lines"]:
            report.add(
                "S1",
                1,
                f"{count} lines; target is {limits['lines']} — longer files reduce "
                "adherence",
            )
    body = mask_code(doc.body)
    hits = 0
    for number, line in enumerate(body.split("\n"), doc.body_start):
        hits += len(_EMPHASIS_RE.findall(line))
        if hits >= 3:
            report.add(
                "S2",
                number,
                "three or more all-caps emphasis words; state the reason instead",
            )
            return


def _check_xml(doc: _Doc, type_: str, report: _Report) -> None:
    if type_ == "output-style":
        report.add("X7", doc.body_start, "output styles take a plain body, not XML")
        return
    body = _mask_comments(mask_code(doc.body))
    lines = body.split("\n")
    offsets = []
    position = 0
    for line in lines:
        offsets.append(position)
        position += len(line) + 1

    def line_of(index: int) -> int:
        low, high = 0, len(offsets) - 1
        while low < high:
            mid = (low + high + 1) // 2
            if offsets[mid] <= index:
                low = mid
            else:
                high = mid - 1
        return low + doc.body_start

    # `docs/<slug>/`, `--scope <glob>` or "see the <storage> section" is text, not
    # markup: an opening tag in the middle of a line is an element only when it
    # closes on that same line. Block elements open at the start of a line.
    def is_placeholder(match: re.Match) -> bool:
        if match.group(1) or match.group(4):
            return False
        line_start = body.rfind("\n", 0, match.start()) + 1
        if not body[line_start : match.start()].strip():
            return False
        line_end = body.find("\n", match.end())
        rest = body[match.end() : line_end if line_end != -1 else len(body)]
        return f"</{match.group(2)}>" not in rest

    stack: list[tuple[str, int]] = []
    roots: list[int] = []
    outside: list[tuple[int, int]] = []
    cursor = 0
    for match in TAG_RE.finditer(body):
        if is_placeholder(match):
            continue
        if not stack:
            outside.append((cursor, match.start()))
        closing, name, selfclose = match.group(1), match.group(2), match.group(4)
        line = line_of(match.start())
        if closing:
            if stack and stack[-1][0] == name:
                stack.pop()
            elif any(open_name == name for open_name, _ in stack):
                while stack and stack[-1][0] != name:
                    open_name, open_line = stack.pop()
                    report.add("X2", open_line, f"`<{open_name}>` is never closed")
                stack.pop()
            else:
                report.add("X2", line, f"`</{name}>` has no opening tag")
        else:
            if not stack:
                roots.append(line)
            if not selfclose:
                stack.append((name, line))
        cursor = match.end()
    if not stack:
        outside.append((cursor, len(body)))
    for open_name, open_line in stack:
        report.add("X2", open_line, f"`<{open_name}>` is never closed")

    allow_imports = type_ == "memory"
    for start, end in outside:
        for offset, text in enumerate(body[start:end].split("\n")):
            if not text.strip():
                continue
            before_root = not roots or line_of(start) < roots[0]
            if allow_imports and before_root and _IMPORT_LINE_RE.match(text):
                continue
            report.add(
                "X1",
                line_of(start) + offset,
                "text outside the root element",
            )
            break
    if len(roots) != 1:
        where = roots[1] if len(roots) > 1 else doc.body_start
        report.add("X1", where, f"{len(roots)} root elements; an XML body has one")


def check(
    path: Path, type_: str | None = None, fmt: str | None = None
) -> list[Finding]:
    """Run every rule that applies to `path` and return the findings in order."""
    path = Path(path)
    type_ = type_ or infer_type(path)
    doc = _split(path)
    report = _Report(path)
    _check_frontmatter(doc, type_, report)
    if type_ == "skill":
        _check_refs(doc, report)
    _check_size(doc, type_, report)
    fmt = fmt or infer_format(doc.body)
    if fmt == "xml":
        _check_xml(doc, type_, report)
    return report.findings


def summary(findings: list[Finding]) -> str:
    errors = sum(1 for f in findings if f.severity == "error")
    warnings = len(findings) - errors
    return f"{errors} errors, {warnings} warnings"
