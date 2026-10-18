"""Tests for `superclaude author-check`, the validator the /sc-author skill runs.

Rule table and interface: docs/features/authoring-skill/04a-design-checker.md.
Every rule code has one violating and one passing case (CASES), and
`test_every_rule_has_case` keeps that true when a code is added.
"""

import re
import subprocess
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
    # Load-set documents passed as --with (rel path -> text).
    with_bad: dict = field(default_factory=dict)
    with_good: dict = field(default_factory=dict)


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
    "N1": Case(
        "docs/guide.md",
        "See [setup](setup.md#install) first.\n",
        "See [setup](setup.md#install) first.\n",
        extra_bad={"docs/setup.md": "# Setup\n## Configure\n"},
        extra_good={"docs/setup.md": "# Setup\n## Install\n"},
    ),
    "N2": Case(
        ".claude/agents/a.md",
        _fm(name="reviewer", description="Reviews.", tools="Read, Grep")
        + "Run the suite with `Bash`.\n",
        _fm(name="reviewer", description="Reviews.", tools="Read, Grep, Bash")
        + "Run the suite with `Bash`.\n",
    ),
    "N3": Case(
        "CLAUDE.md",
        "- Always: run the tests\n",
        "- Always: run the tests\n",
        with_bad={".claude/rules/testing.md": "## Never\n- Run the tests.\n"},
    ),
    "N4": Case(
        "CLAUDE.md",
        "Run the full test suite before every commit.\n",
        "Run the full test suite before every commit.\n",
        with_bad={
            ".claude/rules/testing.md": "- run the full test suite before every commit\n"
        },
    ),
}
# Line each violating case reports its code on.
LINES = {
    "F1": 1,
    "F2": 1,
    "F3": 2,
    "F4": 4,
    "F5": 2,
    "F6": 2,
    "F7": 2,
    "R1": 4,
    "R2": 1,
    "R3": 1,
    "S1": 1,
    "S2": 1,
    "X1": 7,
    "X2": 2,
    "X7": 1,
    "N1": 1,
    "N2": 6,
    "N3": 1,
    "N4": 1,
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
    with_docs = case.with_bad if which == "bad" else case.with_good
    with_paths = [_write(root, rel, text) for rel, text in with_docs.items()]
    target = _write(root, case.rel, case.bad if which == "bad" else case.good)
    fmt = _GOOD_FMT.get(code, case.fmt) if which == "good" else case.fmt
    return check(target, type_=case.type_, fmt=fmt, with_paths=with_paths)


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
            ("x/.claude/agents/review/a.md", "agent"),
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


_QUOTED_TAG_ATTRIBUTES = [
    ' note="<tag>"',
    " note='<tag>'",
    ' note="</tag>"',
    " note='</tag>'",
    ' note="a > b"',
    " note='a > b'",
    ' note="it\'s <tag>"',
    " note='say \"<tag>\"'",
    ' empty="" other=\'\' mode=plain note="a <tag>" ',
]


class TestQuotedTagAttributes:
    @pytest.mark.parametrize("fmt", [None, "xml"], ids=["inferred", "explicit-xml"])
    def test_delegation_document_has_no_xml_errors(self, fmt):
        target = (
            Path(__file__).resolve().parents[2]
            / "src/superclaude/core/rules/RULES_DELEGATION.md"
        )
        findings = [f for f in check(target, fmt=fmt) if f.code in ("X1", "X2")]
        assert not findings, [f.render() for f in findings]

    @pytest.mark.parametrize("attrs", _QUOTED_TAG_ATTRIBUTES)
    @pytest.mark.parametrize("selfclose", ["", "/"])
    def test_full_token_and_capture_groups(self, attrs, selfclose):
        token = f"<outer-tag_2{attrs}{selfclose}>"
        match = author_check.TAG_RE.search(token + "</outer-tag_2>")
        assert match is not None
        assert match.group(0) == token
        assert author_check.TAG_RE.groups == 4
        assert match.groups() == ("", "outer-tag_2", attrs, selfclose)
        closing = author_check.TAG_RE.fullmatch("</outer-tag_2>")
        assert closing is not None
        assert closing.groups() == ("/", "outer-tag_2", None, "")

    @pytest.mark.parametrize("attrs", _QUOTED_TAG_ATTRIBUTES)
    def test_single_line_root_infers_xml(self, attrs):
        assert infer_format(f"<guide{attrs}>\nx\n</guide>\n") == "xml"

    @pytest.mark.parametrize("attrs", _QUOTED_TAG_ATTRIBUTES)
    @pytest.mark.parametrize("selfclose", ["", "/"])
    def test_quoted_literals_are_not_structural_tags(self, tmp_path, attrs, selfclose):
        child = f"<step{attrs}{selfclose}>"
        if not selfclose:
            child += "x</step>"
        target = _write(tmp_path, "guide.md", f"<guide>\n{child}\n</guide>\n")
        findings = [f for f in check(target, fmt="xml") if f.code in ("X1", "X2")]
        assert not findings, [f.render() for f in findings]

    def test_multiline_attributes_explicit_xml(self, tmp_path):
        attrs = '\n note="first <tag>\nthen </tag> >"\n other=\'say "hello"\'\n'
        token = f"<step{attrs}/>"
        match = author_check.TAG_RE.fullmatch(token)
        assert match is not None
        assert match.groups() == ("", "step", attrs, "/")
        target = _write(
            tmp_path, "guide.md", f"<guide>\n{token}\n<next>x</next>\n</guide>\n"
        )
        assert not [f for f in check(target, fmt="xml") if f.code in ("X1", "X2")]

    @pytest.mark.parametrize("frontmatter", ["", "---\ntitle: Guide\n---\n"])
    @pytest.mark.parametrize(
        ("tail", "expected"),
        [
            ("</guide>\n", [("`<step>` is never closed", 2)]),
            ("", [("`<guide>` is never closed", 1), ("`<step>` is never closed", 2)]),
            (
                "</missing>\n</step>\n</guide>\n",
                [("`</missing>` has no opening tag", 5)],
            ),
        ],
        ids=["misnested", "unclosed", "unmatched-closing"],
    )
    def test_real_errors_keep_lines_after_multiline_attributes(
        self, tmp_path, frontmatter, tail, expected
    ):
        body = '<guide>\n<step\n note="<literal> </literal> >">\nx\n' + tail
        target = _write(tmp_path, "guide.md", frontmatter + body)
        findings = [f for f in check(target, fmt="xml") if f.code == "X2"]
        offset = frontmatter.count("\n")
        assert [(f.message, f.line) for f in findings] == [
            (message, line + offset) for message, line in expected
        ]

    @pytest.mark.parametrize("attrs", _QUOTED_TAG_ATTRIBUTES)
    def test_n4_strips_entire_single_line_attributed_tag(self, tmp_path, attrs):
        sentence = "Run the full test suite before every commit."
        target = _write(tmp_path, "guide.md", f"<guide{attrs}>{sentence}</guide>\n")
        other = _write(tmp_path, "other.md", sentence + "\n")
        findings = [f for f in check(target, with_paths=[other]) if f.code == "N4"]
        assert [f.line for f in findings] == [1]

    def test_quoted_closing_tag_does_not_disable_html_void(self, tmp_path):
        target = _write(
            tmp_path,
            "guide.md",
            '<guide>\n<step note="</img>">x</step>\n<img src="a.png">\n</guide>\n',
        )
        assert not [f for f in check(target, fmt="xml") if f.code in ("X1", "X2")]

    def test_comments_and_code_keep_quoted_tags_masked(self, tmp_path):
        target = _write(
            tmp_path,
            "guide.md",
            '<guide>\n<!-- <broken note="<tag>"> -->\n'
            '`<broken note="</tag>">`\n```xml\n<broken note="<tag>">\n```\n'
            "Use docs/<slug>/plan.md and the <storage> section.\n</guide>\n",
        )
        assert not [f for f in check(target, fmt="xml") if f.code in ("X1", "X2")]


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
        assert set(CASES) == set(RULES) == set(LINES)

    @pytest.mark.parametrize("code", sorted(CASES))
    def test_bad_line(self, tmp_path, code):
        lines = [f.line for f in _run_case(tmp_path, code, "bad") if f.code == code]
        assert lines[0] == LINES[code], lines

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


class TestLoadSet:
    """N3 and N4 compare the target with its load set; nothing else does."""

    def _pair(self, tmp_path, target_text, other_text):
        target = _write(tmp_path, "CLAUDE.md", target_text)
        other = _write(tmp_path, "other.md", other_text)
        return target, other

    def test_n3_needs_the_other_document_in_with(self, tmp_path):
        target, other = self._pair(
            tmp_path, "- Always: run tests\n", "- Never: run tests\n"
        )
        assert [f for f in check(target, with_paths=[other]) if f.code == "N3"]
        assert not [f for f in check(target) if f.code == "N3"]

    @pytest.mark.parametrize(
        ("allow", "forbid"),
        [
            ("## Always\n- Run **tests**.\n", "## Never\n- run tests\n"),
            ("**Ask First**\n- push to main\n", "- Never: push to main, delete data\n"),
            ("<does>\n- edit config\n</does>\n", "<never>\n- edit config\n</never>\n"),
            ("- Do: open a pull request\n", "## Don't\n- Open a pull request!\n"),
        ],
    )
    def test_n3_slot_shapes(self, tmp_path, allow, forbid):
        target, other = self._pair(tmp_path, allow, forbid)
        assert [f for f in check(target, with_paths=[other]) if f.code == "N3"]

    def test_n3_within_one_document(self, tmp_path):
        text = "- Always: run tests\n- Never: run tests\n"
        target = _write(tmp_path, "CLAUDE.md", text)
        assert [f for f in check(target) if f.code == "N3"]

    def test_n3_same_slot_is_not_a_conflict(self, tmp_path):
        target, other = self._pair(
            tmp_path, "- Never: run tests\n", "- Never: run tests\n"
        )
        assert not [f for f in check(target, with_paths=[other]) if f.code == "N3"]

    def test_n4_short_sentences_and_code_are_ignored(self, tmp_path):
        target, other = self._pair(
            tmp_path,
            "Run the tests now.\n```\nrun the full suite before every commit\n```\n",
            "Run the tests now.\nrun the full suite before every commit\n",
        )
        assert not [f for f in check(target, with_paths=[other]) if f.code == "N4"]

    def test_n4_frontmatter_is_ignored(self, tmp_path):
        target, other = self._pair(
            tmp_path,
            _fm(paths=["src/**"]) + "Body.\n",
            "paths: ['src/**'] and some more words here\n",
        )
        assert not [f for f in check(target, with_paths=[other]) if f.code == "N4"]


class TestDanglingPointers:
    def test_n1_missing_link_target(self, tmp_path):
        target = _write(tmp_path, "docs/guide.md", "See [x](gone.md).\n")
        assert [(f.code, f.severity) for f in check(target)] == [("N1", "error")]

    def test_n1_same_file_anchor(self, tmp_path):
        text = "# Guide\n## Set up\nSee [s](#set-up), [t](#nope).\n"
        target = _write(tmp_path, "docs/guide.md", text)
        assert [f.message for f in check(target) if f.code == "N1"] == [
            "`#nope` has no matching heading"
        ]

    def test_n1_urls_are_not_checked(self, tmp_path):
        target = _write(
            tmp_path, "docs/guide.md", "See [x](https://example.com/a.md).\n"
        )
        assert not check(target)

    def test_n1_memory_import_line(self, tmp_path):
        target = _write(tmp_path, "CLAUDE.md", "@docs/gone.md\n- rule\n")
        found = [(f.code, f.line, f.severity) for f in check(target)]
        assert found == [("N1", 1, "error")]

    def test_n1_skill_links_are_r1_only(self, tmp_path):
        text = _fm(description="Does x.") + "Read [a](references/gone.md)\n"
        target = _write(tmp_path, ".claude/skills/x/SKILL.md", text)
        assert [f.code for f in check(target)] == ["R1"]

    def test_n1_inline_code_path_is_a_warning(self, tmp_path):
        subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
        _write(tmp_path, "src/app/main.py", "")
        target = _write(
            tmp_path,
            "docs/guide.md",
            "Edit `src/app/main.py:3` not `src/app/gone.py`.\n",
        )
        found = [(f.code, f.severity, f.message) for f in check(target)]
        assert found == [
            (
                "N1",
                "warning",
                "`src/app/gone.py` does not exist (from the repository root)",
            )
        ]

    @pytest.mark.parametrize(
        "token",
        ["<name>/x.md", "docs/*.md", "{a}/b.py", "$HOME/x.md", "README", "~/x/y.md"],
    )
    def test_n1_placeholders_are_skipped(self, tmp_path, token):
        target = _write(tmp_path, "docs/guide.md", f"See `{token}`.\n")
        assert not [f for f in check(target) if f.code == "N1"]

    def test_n2_skips_agents_without_tools(self, tmp_path):
        target = _write(tmp_path, ".claude/agents/a.md", _AGENT + "Use `Bash`.\n")
        assert not [f for f in check(target) if f.code == "N2"]

    def test_n2_mcp_tool(self, tmp_path):
        call = "Call `mcp__example__lookup`.\n"
        bad = _fm(name="r", description="Reviews.", tools="Read") + call
        good = (
            _fm(name="r", description="Reviews.", tools="Read, mcp__example__lookup")
            + call
        )
        assert [
            f.code for f in check(_write(tmp_path, "a/.claude/agents/a.md", bad))
        ] == ["N2"]
        assert not check(_write(tmp_path, "b/.claude/agents/a.md", good))

    def test_n2_only_agents(self, tmp_path):
        text = _fm(description="Does x.", **{"allowed-tools": "Read"}) + "Use `Bash`.\n"
        target = _write(tmp_path, ".claude/skills/x/SKILL.md", text)
        assert not [f for f in check(target) if f.code == "N2"]


class TestReviewFixes:
    """Inputs an independent review found misjudged (2026-10-14)."""

    def test_duplicate_heading_suffix(self, tmp_path):
        target = _write(tmp_path, "d.md", "## Dup\n## Dup\n[c](#dup-1) [d](#dup)\n")
        assert not [f for f in check(target) if f.code == "N1"]

    def test_percent_encoded_anchor_and_path(self, tmp_path):
        _write(tmp_path, "docs/my guide.md", "## 설치 방법\n")
        text = "[a](docs/my%20guide.md#%EC%84%A4%EC%B9%98-%EB%B0%A9%EB%B2%95)\n"
        target = _write(tmp_path, "index.md", text)
        assert not [f for f in check(target) if f.code == "N1"]

    def test_root_relative_link(self, tmp_path):
        subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
        _write(tmp_path, "docs/guide.md", "# Guide\n")
        target = _write(tmp_path, "sub/page.md", "[g](/docs/guide.md)\n")
        assert not [f for f in check(target) if f.code == "N1"]

    def test_mention_is_not_an_import(self, tmp_path):
        target = _write(tmp_path, "CLAUDE.md", "Ask @jane.doe for access.\n")
        assert not [f for f in check(target) if f.code == "N1"]

    def test_inline_path_import_is_a_warning(self, tmp_path):
        target = _write(tmp_path, "CLAUDE.md", "See @docs/gone.md for more.\n")
        found = [(f.code, f.severity) for f in check(target)]
        assert found == [("N1", "warning")]

    def test_html_led_markdown_is_md(self, tmp_path):
        text = '<p align="center"><img src="logo.png"></p>\n\n# Project\n'
        target = _write(tmp_path, "README.md", text)
        assert infer_format(text) == "md"
        assert not [f for f in check(target) if f.code.startswith("X")]

    def test_void_elements_close_themselves(self, tmp_path):
        text = '<guide>\n<img src="a.png">\n<br>\n</guide>\n'
        target = _write(tmp_path, "docs/guide.md", text)
        assert not [f for f in check(target, fmt="xml") if f.code in ("X1", "X2")]

    def test_void_name_used_as_element(self, tmp_path):
        text = "<guide>\n<meta>\nx\n</meta>\n</guide>\n"
        target = _write(tmp_path, "docs/guide.md", text)
        assert not [f for f in check(target, fmt="xml") if f.code in ("X1", "X2")]

    def test_uppercase_tags(self, tmp_path):
        target = _write(tmp_path, "docs/guide.md", "<Root>\n<Step>x</Step>\n</Root>\n")
        assert not [f for f in check(target, fmt="xml") if f.code in ("X1", "X2")]

    def test_bom_frontmatter_is_read(self, tmp_path):
        target = tmp_path / ".claude" / "agents" / "a.md"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"\xef\xbb\xbf---\nname: r\n---\nBody\n")
        assert [f.code for f in check(target)] == ["F2"]

    def test_not_utf8_is_an_input_error(self, tmp_path):
        target = tmp_path / "latin1.md"
        target.write_bytes(b"caf\xe9\n")
        with pytest.raises(author_check.NotTextError):
            check(target)
        result = CliRunner().invoke(main, ["author-check", str(target)])
        assert result.exit_code == 2
        assert "not UTF-8 text" in result.output

    def test_r1_ignores_trailing_punctuation(self, tmp_path):
        _write(tmp_path, ".claude/skills/x/references/a.md", "A.\n")
        text = (
            _fm(description="Does x.")
            + "Read ${CLAUDE_SKILL_DIR}/references/a.md, then stop.\n"
        )
        target = _write(tmp_path, ".claude/skills/x/SKILL.md", text)
        assert not [f for f in check(target) if f.code == "R1"]

    def test_r2_reported_once_per_file(self, tmp_path):
        _write(tmp_path, ".claude/skills/x/references/a.md", "See [b](b.md)\n")
        _write(tmp_path, ".claude/skills/x/references/b.md", "B.\n")
        links = "[a](references/a.md) and [a](references/a.md)\n"
        target = _write(
            tmp_path, ".claude/skills/x/SKILL.md", _fm(description="Does x.") + links
        )
        assert len([f for f in check(target) if f.code == "R2"]) == 1

    def test_inline_path_relative_to_document(self, tmp_path):
        _write(tmp_path, "pkg/references/a.md", "A.\n")
        target = _write(tmp_path, "pkg/guide.md", "Read `references/a.md` first.\n")
        assert not [f for f in check(target) if f.code == "N1"]

    def test_repo_root_without_git(self, tmp_path, monkeypatch):
        def no_git(*args, **kwargs):
            raise OSError("git not found")

        author_check._repo_root.cache_clear()
        monkeypatch.setattr(author_check.subprocess, "run", no_git)
        monkeypatch.chdir(tmp_path)
        try:
            assert author_check._repo_root(tmp_path) == Path.cwd()
        finally:
            author_check._repo_root.cache_clear()


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

    def test_missing_with_path_exit_2(self, tmp_path):
        target = _write(tmp_path, "docs/guide.md", "x\n")
        result = self._invoke(str(target), "--with", str(tmp_path / "nope.md"))
        assert result.exit_code == 2

    def test_with_reaches_the_rules(self, tmp_path):
        target = _write(tmp_path, "CLAUDE.md", "- Always: run tests\n")
        other = _write(tmp_path, "other.md", "- Never: run tests\n")
        result = self._invoke(str(target), "--with", str(other))
        assert result.exit_code == 1
        assert " N3 error: " in result.output

    def test_unknown_type_exit_2(self, tmp_path):
        target = _write(tmp_path, "docs/guide.md", "x\n")
        assert self._invoke(str(target), "--type", "mode").exit_code == 2
