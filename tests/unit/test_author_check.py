"""Tests for `superclaude author-check`, the validator the /sc-author skill runs.

Rule table and interface: docs/features/authoring-skill/04a-design-checker.md.
Every rule code has one violating and one passing case (CASES), and
`test_every_rule_has_case` keeps that true when a code is added.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from superclaude.cli import author_check
from superclaude.cli.author_check import (
    RULES,
    check,
    infer_format,
    infer_type,
    mask_code,
)
from superclaude.cli.main import main

_FIELDS = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "superclaude"
    / "skills"
    / "sc-author"
    / "references"
    / "fields.yaml"
)


def _fm(**fields) -> str:
    return "---\n" + yaml.safe_dump(fields, sort_keys=False) + "---\n"


_AGENT = _fm(name="reviewer", description="Reviews SQL migrations.")
_TOC = "## Contents\n- [A](#a)\n- [B](#b)\n- [C](#c)\n"


@dataclass
class Case:
    rel: str
    bad: str
    good: str
    type_: str | None = None
    fmt: str | None = None
    extra_bad: dict = field(default_factory=dict)
    extra_good: dict = field(default_factory=dict)


CASES = {
    "F1": Case(".claude/agents/a.md", "Reviews migrations.\n", _AGENT + "Body.\n"),
    "F2": Case(
        ".claude/agents/a.md", _fm(name="reviewer") + "Body.\n", _AGENT + "Body.\n"
    ),
    "F3": Case(
        ".claude/commands/c.md",
        _fm(name="c", description="Runs c.") + "Body.\n",
        _fm(description="Runs c.") + "Body.\n",
    ),
    "F4": Case(
        ".claude/agents/a.md",
        _fm(name="reviewer", description="Reviews.", colour="red") + "Body.\n",
        _fm(name="reviewer", description="Reviews.", color="red") + "Body.\n",
    ),
    "F5": Case(
        ".claude/skills/x/SKILL.md",
        _fm(name="Bad_Name", description="Does x.") + "Body.\n",
        _fm(name="good-name", description="Does x.") + "Body.\n",
    ),
    "F6": Case(
        ".claude/skills/x/SKILL.md",
        _fm(description="d" * 1000, when_to_use="w" * 537) + "Body.\n",
        _fm(description="d" * 1000, when_to_use="w" * 536) + "Body.\n",
    ),
    "F7": Case(
        ".claude/skills/x/SKILL.md",
        _fm(description="I can review SQL migrations.") + "Body.\n",
        _fm(description="Reviews SQL migrations.") + "Body.\n",
    ),
    "R1": Case(
        ".claude/skills/x/SKILL.md",
        _fm(description="Does x.") + "Read ${CLAUDE_SKILL_DIR}/references/gone.md\n",
        _fm(description="Does x.") + "Read ${CLAUDE_SKILL_DIR}/references/here.md\n",
        extra_good={".claude/skills/x/references/here.md": "Here.\n"},
    ),
    "R2": Case(
        ".claude/skills/x/SKILL.md",
        _fm(description="Does x.") + "Read [a](references/a.md)\n",
        _fm(description="Does x.") + "Read [a](references/a.md)\n",
        extra_bad={
            ".claude/skills/x/references/a.md": "See [b](b.md)\n",
            ".claude/skills/x/references/b.md": "B.\n",
        },
        extra_good={".claude/skills/x/references/a.md": "A.\n"},
    ),
    "R3": Case(
        ".claude/skills/x/SKILL.md",
        _fm(description="Does x.") + "Read [a](references/a.md)\n",
        _fm(description="Does x.") + "Read [a](references/a.md)\n",
        extra_bad={".claude/skills/x/references/a.md": "line\n" * 101},
        extra_good={".claude/skills/x/references/a.md": _TOC + "line\n" * 101},
    ),
    "S1": Case("CLAUDE.md", "- rule\n" * 201, "- rule\n" * 200),
    "S2": Case(
        "docs/guide.md",
        "You MUST do a. ALWAYS do b. NEVER do c.\n",
        "You MUST do a. ALWAYS do b.\n",
    ),
    "X1": Case(
        ".claude/skills/x/SKILL.md",
        _fm(description="Does x.") + "<steps>\nDo x.\n</steps>\nStray text.\n",
        _fm(description="Does x.") + "<steps>\nDo x.\n</steps>\n",
        fmt="xml",
    ),
    "X2": Case(
        "docs/guide.md",
        "<guide>\n<step>\nDo x.\n</guide>\n",
        "<guide>\n<step>\nDo x.\n</step>\n</guide>\n",
        fmt="xml",
    ),
    "X7": Case(
        ".claude/output-styles/s.md",
        "<style>\nBe brief.\n</style>\n",
        "<style>\nBe brief.\n</style>\n",
        fmt="xml",
    ),
}
# X7 passes when the same output style is checked as md.
_GOOD_FMT = {"X7": "md"}


def _write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _run_case(tmp_path: Path, code: str, which: str) -> list:
    case = CASES[code]
    root = tmp_path / which
    extra = case.extra_bad if which == "bad" else case.extra_good
    for rel, text in extra.items():
        _write(root, rel, text)
    target = _write(root, case.rel, case.bad if which == "bad" else case.good)
    fmt = _GOOD_FMT.get(code, case.fmt) if which == "good" else case.fmt
    return check(target, type_=case.type_, fmt=fmt)


class TestFieldsYaml:
    def _load(self) -> dict:
        return yaml.safe_load(_FIELDS.read_text(encoding="utf-8"))

    def test_top_level_keys(self):
        data = self._load()
        assert {"sources", "tool_names", "types"} <= set(data)

    def test_sources_name_url_and_retrieval_date(self):
        sources = self._load()["sources"]
        assert sources
        for source in sources:
            assert source["url"].startswith("https://")
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(source["retrieved"]))

    def test_known_types_and_shape(self):
        types = self._load()["types"]
        assert set(types) == {"skill", "agent", "command", "output-style", "memory"}
        for name, spec in types.items():
            assert spec["frontmatter"] in ("required", "optional"), name
            for key in ("location", "required", "optional", "unsupported"):
                assert isinstance(spec[key], list), (name, key)
            assert isinstance(spec["limits"], dict), name
            accepted = set(spec["required"]) | set(spec["optional"])
            assert not accepted & set(spec["unsupported"]), name

    def test_tool_names(self):
        names = self._load()["tool_names"]
        assert {"Bash", "PowerShell", "Read"} <= set(names)


class TestInferType:
    @pytest.mark.parametrize(
        ("rel", "expected"),
        [
            ("x/.claude/skills/foo/SKILL.md", "skill"),
            ("x/.claude/agents/a.md", "agent"),
            ("x/.claude/commands/g/c.md", "command"),
            ("x/.claude/output-styles/s.md", "output-style"),
            ("CLAUDE.md", "memory"),
            ("x/CLAUDE.local.md", "memory"),
            ("AGENTS.md", "memory"),
            ("x/.claude/rules/r.md", "memory"),
            ("x/.claude/rules/sub/r.md", "memory"),
            ("docs/MODE_X.md", "generic"),
        ],
    )
    def test_from_path(self, rel, expected):
        assert infer_type(Path(rel)) == expected


class TestInferFormat:
    def test_tag_after_preamble_is_xml(self):
        body = "\n<!-- note -->\n@docs/a.md\n\n<root>\nx\n</root>\n"
        assert infer_format(body) == "xml"

    def test_heading_is_md(self):
        assert infer_format("# Title\n\n<root>x</root>\n") == "md"

    def test_prose_angle_bracket_is_md(self):
        assert infer_format("<3 items per page\n") == "md"


class TestTagRecognition:
    @pytest.mark.parametrize("text", ["<3", "<5KB", "<=", "a < b"])
    def test_prose_is_not_a_tag(self, text):
        assert not author_check.TAG_RE.search(text)

    @pytest.mark.parametrize(
        "text", ["<role>", "</role>", "<br/>", '<example kind="x">', "<tool-use>"]
    )
    def test_tags(self, text):
        assert author_check.TAG_RE.search(text)

    def test_code_is_masked_and_lines_kept(self):
        text = "a `<role>` b\n```\n<role>\n```\nc\n"
        masked = mask_code(text)
        assert "<role>" not in masked
        assert masked.count("\n") == text.count("\n")
        assert masked.splitlines()[4] == "c"


class TestRules:
    @pytest.mark.parametrize("code", sorted(CASES))
    def test_bad_fires(self, tmp_path, code):
        findings = _run_case(tmp_path, code, "bad")
        hits = [f for f in findings if f.code == code]
        assert hits, f"{code} did not fire: {findings}"
        assert hits[0].severity == RULES[code]

    @pytest.mark.parametrize("code", sorted(CASES))
    def test_good_silent(self, tmp_path, code):
        findings = _run_case(tmp_path, code, "good")
        assert not [f for f in findings if f.code == code], findings

    def test_every_rule_has_case(self):
        assert set(CASES) == set(RULES)

    def test_yaml_parse_failure_is_f1(self, tmp_path):
        target = _write(tmp_path, ".claude/agents/a.md", "---\nname: [a\n---\nBody\n")
        assert [f.code for f in check(target)] == ["F1"]

    def test_memory_xml_allows_imports_before_root(self, tmp_path):
        text = "@docs/a.md\n<!-- c -->\n<project>\nx\n</project>\n"
        target = _write(tmp_path, "CLAUDE.md", text)
        assert not [f for f in check(target, fmt="xml") if f.code == "X1"]

    def test_skill_xml_bare_import_line_is_x1(self, tmp_path):
        text = _fm(description="Does x.") + "@docs/a.md\n<steps>\nx\n</steps>\n"
        target = _write(tmp_path, ".claude/skills/x/SKILL.md", text)
        assert [f for f in check(target, fmt="xml") if f.code == "X1"]

    def test_x2_ignores_tags_in_code_and_prose(self, tmp_path):
        text = "<guide>\nUse `<open>` and <3 items.\n```\n<unclosed>\n```\n</guide>\n"
        target = _write(tmp_path, "docs/guide.md", text)
        assert not [f for f in check(target, fmt="xml") if f.code in ("X1", "X2")]

    def test_x2_mid_line_placeholders_are_text(self, tmp_path):
        text = (
            "<guide>\nWrite docs/<slug>/plan.md, see the <storage> section.\n"
            "Inline <b>bold</b> stays markup.\n"
            '<handoff next="/review"/>\n</guide>\n'
        )
        target = _write(tmp_path, "docs/guide.md", text)
        assert not [f for f in check(target, fmt="xml") if f.code in ("X1", "X2")]

    def test_x2_unclosed_block_tag_at_line_start(self, tmp_path):
        target = _write(tmp_path, "docs/guide.md", "<guide>\n<step>\nx\n</guide>\n")
        assert [f.line for f in check(target, fmt="xml") if f.code == "X2"] == [2]

    def test_f3_reports_the_field_line(self, tmp_path):
        text = "---\ndescription: Runs c.\npaths: ['*.py']\n---\nBody\n"
        target = _write(tmp_path, ".claude/commands/c.md", text)
        f3 = [f for f in check(target) if f.code == "F3"]
        assert [f.line for f in f3] == [3]

    def test_generic_gets_no_field_rules(self, tmp_path):
        target = _write(tmp_path, "docs/guide.md", _fm(anything="x") + "Body.\n")
        assert not [f for f in check(target) if f.code.startswith("F")]


class TestCli:
    def _invoke(self, *args):
        return CliRunner().invoke(main, ["author-check", *args])

    def test_error_line_summary_and_exit_1(self, tmp_path):
        target = _write(tmp_path, ".claude/agents/a.md", _fm(name="r") + "Body.\n")
        result = self._invoke(str(target))
        assert result.exit_code == 1, result.output
        lines = result.output.strip().splitlines()
        assert re.match(rf"{re.escape(str(target))}:1: F2 error: ", lines[0])
        assert lines[-1] == "1 errors, 0 warnings"

    def test_warnings_only_exit_0(self, tmp_path):
        target = _write(tmp_path, "docs/guide.md", "MUST MUST MUST\n")
        result = self._invoke(str(target))
        assert result.exit_code == 0, result.output
        assert result.output.strip().splitlines()[-1] == "0 errors, 1 warnings"

    def test_clean_exit_0(self, tmp_path):
        target = _write(tmp_path, ".claude/agents/a.md", _AGENT + "Body.\n")
        result = self._invoke(str(target))
        assert result.exit_code == 0, result.output
        assert result.output.strip() == "0 errors, 0 warnings"

    def test_missing_path_exit_2(self, tmp_path):
        assert self._invoke(str(tmp_path / "nope.md")).exit_code == 2

    def test_unknown_type_exit_2(self, tmp_path):
        target = _write(tmp_path, "docs/guide.md", "x\n")
        assert self._invoke(str(target), "--type", "mode").exit_code == 2
