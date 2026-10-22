"""Docs ↔ SSOT guards (docs/features/docs-ssot-audit, 05-plan §2, T1–T5 and T7;
T4 extended by the content round that followed 06-verify).

The audit found 25 places where a document restated a mechanism, a list or
a number that the code, the Makefile, hooks.json or the tree no longer
matched, and none of them was in a shape an existing test watched. Each
test here pins one of those shapes to its source. T6 lives in
``test_version_consistency.py`` (the no-expiry lint).

Scope is deliberate: README, AGENTS, CLAUDE, the shipped READMEs, the CLI
help text, the Makefile and the working docs an agent is routed to. Dated
research, analysis and archive docs are records and stay out.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from click.testing import CliRunner

from superclaude.cli.hook_dispatch import HOOKS
from superclaude.cli.install_paths import COMPONENTS
from superclaude.cli.main import main as cli
from superclaude.scripts.context_loader import RETIRED_FLAGS

_ROOT = Path(__file__).resolve().parents[2]
_SRC = _ROOT / "src" / "superclaude"
_README = _ROOT / "README.md"
_CODEX = _ROOT / "docs" / "codex" / "prompting_session_raw"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cli_help() -> dict[str, str]:
    """Every click help text, keyed by command path."""
    runner = CliRunner()
    out = {"superclaude": runner.invoke(cli, ["--help"]).output}
    for name, cmd in cli.commands.items():
        if name in ("insight", "hook", "auto-improve", "parallel-ab"):
            continue  # argparse pass-throughs; their help is the script's own
        out[f"superclaude {name}"] = runner.invoke(cli, [name, "--help"]).output
        for sub in getattr(cmd, "commands", {}):
            out[f"superclaude {name} {sub}"] = runner.invoke(
                cli, [name, sub, "--help"]
            ).output
    return out


# Docs an agent or a user is routed to as current fact (T2, T3).
_ROUTED_DOCS = [
    _README,
    _ROOT / "AGENTS.md",
    _ROOT / "CLAUDE.md",
    _ROOT / "docs" / "README.md",
    _ROOT / "docs" / "PRD.md",
    _ROOT / "docs" / "UI-GUIDE.md",
    *sorted((_ROOT / "docs" / "reports").glob("*.md")),
    *sorted(_SRC.glob("*/README.md")),
    _SRC / "ARCHITECTURE.md",
]
_CODEX_GUIDES = sorted(_CODEX.glob("0[1-8]_*.md")) + [_CODEX / "README.md"]
_RULES_DOCS = sorted((_ROOT / ".claude" / "rules").rglob("*.md"))


def _sources(extra: list[Path] = ()) -> dict[str, str]:
    """Routed docs, the Makefile and the CLI help, as {label: text}.

    Whitespace is collapsed, so a phrase Click re-wrapped across two lines of
    a help text (06-verify Z-5), or one wrapped by hand in a doc, still
    matches.
    """
    out = {str(p.relative_to(_ROOT)): _read(p) for p in [*_ROUTED_DOCS, *extra]}
    out["Makefile"] = _read(_ROOT / "Makefile")
    out.update(_cli_help())
    return {label: re.sub(r"\s+", " ", text) for label, text in out.items()}


# --------------------------------------------------------------------- T1 --
def _hooks_json():
    return json.loads(_read(_SRC / "hooks" / "hooks.json"))["hooks"]


def _registrations() -> list[tuple[str, str]]:
    return [
        (event, h["command"])
        for event, groups in _hooks_json().items()
        for g in groups
        for h in g["hooks"]
    ]


def _section(text: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert m, f"no '## {heading}' section"
    return m.group(1)


def test_hooks_readme_lists_every_registration():
    """hooks/README.md 'Current Hooks' = hooks.json, event by event (D-07)."""
    section = _section(_read(_SRC / "hooks" / "README.md"), "Current Hooks")
    headings = set(re.findall(r"^### (\w+)", section, re.M))
    events = set(_hooks_json())
    assert headings == events, f"README events {headings} != hooks.json {events}"
    for event, command in _registrations():
        event_block = re.search(
            rf"^### {event}\n(.*?)(?=^### |\Z)", section, re.M | re.S
        ).group(1)
        assert f"`{command}`" in event_block, (
            f"hooks/README.md 'Current Hooks' omits `{command}` under {event}"
        )


def test_scripts_readme_rows_name_every_event():
    """A scripts/README.md row that names hook events names all of them (D-18)."""
    rows = _read(_SRC / "scripts" / "README.md").splitlines()
    events = set(_hooks_json())
    by_script: dict[str, set[str]] = {}
    for event, command in _registrations():
        by_script.setdefault(command.split()[2], set()).add(event)
    for script, registered in by_script.items():
        row = next((r for r in rows if f"`{script}.py`" in r), None)
        assert row, f"scripts/README.md has no row for {script}.py"
        named = {e for e in events if e in row}
        if named:
            assert named == registered, (
                f"{script}.py row names {sorted(named)}, hooks.json registers "
                f"it on {sorted(registered)}"
            )


# --------------------------------------------------------------------- T2 --
# Phrases a release retired or a mechanism replaced; one row each, capped at
# ten (Q3 b). A row names the finding that put it here. Rows are scoped to
# the claim's shape, not the bare word (06-verify Z-9): `.gitignore` and
# `gitignored` are wrong only when they describe the local scope (a legacy
# `.gitignore` block that install strips is written as "legacy block");
# `pytest-cov` is wrong only as a dev dependency.
_LOCAL = r"(?:\blocal\b|CLAUDE\.local\.md|\./\.claude/)"
_RETIRED_PHRASES = [
    (
        rf"{_LOCAL}.{{0,100}}\.gitignore block|\.gitignore block.{{0,100}}{_LOCAL}",
        "D-01: local scope lives in .git/info/exclude",
    ),
    (
        rf"{_LOCAL}.{{0,100}}\bgitignored\b|\bgitignored\b.{{0,100}}{_LOCAL}",
        "D-24: local scope is excluded via .git/info/exclude",
    ),
    (r"`integration`", "D-02: there is no integration branch"),
    (
        r"\bpytest-cov\b(?=.{0,60}\b(?:uninstalled|dev extras|dev deps|toolchain|installs))",
        "D-12: removed from the dev extras in 4.29.0",
    ),
    (r"\bPM Agent\b", "D-15: pm-agent was retired in 4.30.0"),
    (r"\d+(?:\.\d+)?k-token", "D-06: TestCoreLiteSplit owns the kernel budget"),
]


@pytest.mark.parametrize(
    ("pattern", "why"),
    _RETIRED_PHRASES,
    ids=[w.split(":")[0] for _, w in _RETIRED_PHRASES],
)
def test_docs_name_no_retired_phrase(pattern, why):
    scope = _sources(_CODEX_GUIDES)
    hits = [
        f"{label}: {m.group(0)!r}"
        for label, text in scope.items()
        for m in re.finditer(pattern, text)
    ]
    assert not hits, f"{why}; still stated in: {hits}"


def test_docs_name_only_registered_hooks():
    """`superclaude hook <x>` in a doc names a hook in the registry (D-23)."""
    scope = _sources([_ROOT / "CHANGELOG.md"])
    bad = [
        f"{label}: {m.group(0)}"
        for label, text in scope.items()
        for m in re.finditer(r"superclaude hook ([a-z][\w-]*)", text)
        if m.group(1) not in HOOKS
    ]
    assert not bad, f"hook names not in hook_dispatch.HOOKS: {bad}"


def _make_targets() -> set[str]:
    text = _read(_ROOT / "Makefile")
    return set(re.search(r"^\.PHONY:(.*)$", text, re.M).group(1).split())


_TARGET_WORDS = {
    "verify",
    "test",
    "lint",
    "format",
    "deploy",
    "install",
    "help",
    "doctor",
    "clean",
    "release",
    "ci",
    "typecheck",
    "sync",
    "check",
    "build",
    "canary",
}


def test_docs_name_only_makefile_targets():
    """`make <target>` in a doc is a .PHONY target (D-13).

    A backticked `make x` is always checked; a bare one only when x is
    target-shaped (06-verify Z-8).
    """
    targets = _make_targets()
    scope = _sources(_CODEX_GUIDES)
    bad = []
    for label, text in scope.items():
        for m in re.finditer(
            r"`make ([a-z][a-z0-9-]*)`|(?<![\w/`])make ([a-z][a-z0-9-]*)\b", text
        ):
            backticked, bare = m.group(1), m.group(2)
            t = backticked or bare
            if t in targets:
                continue
            if backticked or t in _TARGET_WORDS or "-" in t:
                bad.append(f"{label}: make {t}")
    assert not bad, f"not a Makefile target: {bad}"


def test_readme_retired_flags_list_is_complete():
    """README's retired-flags note names every RETIRED_FLAGS key or the table (D-21)."""
    line = next(
        (ln for ln in _read(_README).splitlines() if "Retired flags" in ln), None
    )
    assert line, "README.md has no 'Retired flags' note"
    if "RETIRED_FLAGS" in line:
        return
    missing = [
        f
        for f in RETIRED_FLAGS
        if f"--{f}" not in line and not (f.startswith("think") and "--think*" in line)
    ]
    assert not missing, f"README retired-flags note omits {missing}"


# --------------------------------------------------------------------- T3 --
_PLACEHOLDER = re.compile(r"[<>{}*…]")


def test_doc_test_paths_exist():
    """Every `tests/…/x.py` a routed doc names exists (D-09)."""
    scope = {
        str(p.relative_to(_ROOT)): _read(p)
        for p in [*_ROUTED_DOCS, *_CODEX_GUIDES, *_RULES_DOCS]
    }
    bad = [
        f"{label}: {m.group(0)}"
        for label, text in scope.items()
        for m in re.finditer(r"\btests/[\w./-]+\.py\b", text)
        if not _PLACEHOLDER.search(m.group(0)) and not (_ROOT / m.group(0)).exists()
    ]
    assert not bad, f"test files that do not exist: {bad}"


def test_doc_layout_dirs_exist():
    """docs/README.md Layout and PROJECT_INDEX.md Docs layout = `ls docs/` (D-11).

    Both directions: every listed dir exists, every existing dir is listed
    (06-verify Z-8).
    """
    existing = {p.name for p in (_ROOT / "docs").iterdir() if p.is_dir()}
    listed = {
        "docs/README.md": set(
            re.findall(
                r"^\| `([\w-]+)/` \|",
                _section(_read(_ROOT / "docs" / "README.md"), "Layout"),
                re.M,
            )
        ),
        "PROJECT_INDEX.md": {
            name
            for name in re.findall(
                r"`([\w-]+)/[^`]*`",
                _section(
                    _read(_ROOT / "docs" / "reports" / "PROJECT_INDEX.md"),
                    "Docs layout",
                ),
            )
            if name != "docs"
        },
    }
    bad = []
    for label, names in listed.items():
        bad += [
            f"{label} lists {n}/, which does not exist"
            for n in sorted(names - existing)
        ]
        bad += [f"{label} omits docs/{n}/" for n in sorted(existing - names)]
    assert not bad, f"docs/ layouts out of sync with the tree: {bad}"


def test_doc_rule_file_names_exist():
    """Every `.claude/rules/<x>.md` a routed doc names exists."""
    scope = {
        str(p.relative_to(_ROOT)): _read(p)
        for p in [*_ROUTED_DOCS, *_CODEX_GUIDES, *_RULES_DOCS]
    }
    bad = [
        f"{label}: {m.group(0)}"
        for label, text in scope.items()
        for m in re.finditer(r"\.claude/rules/[\w/-]+\.md", text)
        if not _PLACEHOLDER.search(m.group(0)) and not (_ROOT / m.group(0)).exists()
    ]
    assert not bad, f"rule files that do not exist: {bad}"


# --------------------------------------------------------------------- T4 --
def _config_profiles() -> dict[str, tuple[str, str]]:
    text = _read(_SRC / "modes" / "RESEARCH_CONFIG.md")
    block = re.search(r"<depth_profiles>(.*?)</depth_profiles>", text, re.S).group(1)
    out = {}
    for name, triple in re.findall(r"^\| (\w+) \| ([\d+]+/\d+/\d+) \|", block, re.M):
        sources, hops, _iters = triple.split("/")
        out[name] = (sources, hops)
    assert out, "RESEARCH_CONFIG.md has no depth_profiles rows"
    return out


def _readme_section(heading_fragment: str) -> str:
    text = _read(_README)
    m = re.search(
        rf"^## [^\n]*{re.escape(heading_fragment)}[^\n]*\n(.*?)(?=^## |\Z)",
        text,
        re.M | re.S,
    )
    assert m, f"README.md has no '## …{heading_fragment}…' section"
    return m.group(1)


_ALLOWED_DEPTH_COLUMNS = {"Depth", "Sources", "Hops", "Extract", "Best For"}


def test_readme_research_table_matches_config():
    """README's depth table = RESEARCH_CONFIG depth_profiles, no extra columns (D-04)."""
    section = _readme_section("Deep Research")
    m = re.search(r"^\| \*?\*?Depth.*?\n(?:\|.*\n)+", section, re.M)
    assert m, "README Deep Research section has no depth table"
    lines = m.group(0).strip().splitlines()
    header = [c.strip().strip("*") for c in lines[0].strip("|").split("|")]
    extra = set(header) - _ALLOWED_DEPTH_COLUMNS
    assert not extra, (
        f"README depth table has columns RESEARCH_CONFIG does not define: {extra}"
    )
    config = _config_profiles()
    for row in lines[2:]:
        cells = [c.strip().strip("*") for c in row.strip("|").split("|")]
        profile = cells[0].lower()
        assert profile in config, (
            f"README depth row {profile!r} is not a config profile"
        )
        assert (cells[1], cells[2]) == config[profile], (
            f"README {profile}: sources/hops {cells[1]}/{cells[2]} vs config {config[profile]}"
        )


def test_readme_research_section_states_no_undefined_figure():
    """No confidence or minute figure in README's research section (D-04)."""
    section = _readme_section("Deep Research")
    hits = re.findall(r"\b\d\.\d\b|~\d+ ?min\b", section)
    assert not hits, (
        f"README Deep Research states figures no shipped file defines: {hits}"
    )


# Shipped prose that may restate a depth profile's hop count: every markdown
# under src/superclaude/ except the config itself, plus README (content round
# after the audit, 06-verify "Out-of-scope observations": research.md and
# deep-researcher.md said 2-3 / 3-4 / 5+ hops against config 3 / 4 / 5).
_CONFIG = _SRC / "modes" / "RESEARCH_CONFIG.md"
# A profile is read only as a label ("Standard:", "standard depth"), never as
# part of a hyphenated name (deep-researcher) or a common phrase (Standard
# library); the window up to the figure cannot cross a second profile label.
_PROFILE = r"(?<![\w-])(quick|standard|deep|exhaustive)(?![\w-])"
_HOP_STATEMENT = re.compile(
    _PROFILE + r"(?=:| depth\b)"
    r"(?:(?!" + _PROFILE.replace("(quick", "(?:quick") + r")[^.|\n]){0,120}?"
    r"\b((?:at least |more than |over )?"
    r"\d+(?:\s*(?:[-\u2013\u2014]|to)\s*\d+)?\+?)\s+hops?\b",
    re.I,
)


# Probe sentences from the verifier's mutation table (06a-verify-research-hops
# R-2, R-3): what the hop regex must read, and what it must leave alone.
_HOP_PROBES = [
    ("Standard: 2 to 3 hops", [("Standard", "2 to 3")]),
    ("Standard: 2\u20143 hops", [("Standard", "2\u20143")]),
    ("Standard: at least 3 hops", [("Standard", "at least 3")]),
    ("Exhaustive: 5+ hops", [("Exhaustive", "5+")]),
    ("standard depth: 2-3 hops", [("standard", "2-3")]),
    ("deep: up to 4 hops, mid-checkpoints", [("deep", "4")]),
    ("The deep-researcher agent keeps each sub-query within 2 hops.", []),
    ("Standard library docs rarely need more than 2 hops.", []),
    ("A quick sanity check first, then the standard run with 3 hops.", []),
    ("quick: runs without asking, standard: 3 hops", [("standard", "3")]),
]


@pytest.mark.parametrize(
    ("text", "expected"), _HOP_PROBES, ids=[t for t, _ in _HOP_PROBES]
)
def test_hop_statement_regex_reads_profiles_not_words(text, expected):
    """The hop regex reads a profile label, not an agent name or a common word."""
    assert _HOP_STATEMENT.findall(text) == expected


def test_shipped_hop_counts_match_config():
    """'<profile> … N hops' in a command, agent, mode or README = config, exactly.

    A range ("2-3", "2–3", "2—3", "2 to 3 hops"), an open end ("5+ hops") or
    a floor ("at least 3 hops") never equals the single figure the config
    states, so all fail here; "up to N" and a bare N pass when N is the
    config's. Content either states the config's number or points at the
    depth_profiles table instead. Does not catch: a figure written as a word
    ("three hops"), a figure before its profile ("3 hops at standard depth"),
    a profile used without a label ("the standard run with 3 hops"), or a
    figure more than 120 characters or a sentence boundary away from its
    label ("(e.g. 2-3 hops)").
    """
    config = _config_profiles()
    bad = []
    for path in [*sorted(_SRC.rglob("*.md")), _README]:
        if path == _CONFIG:
            continue
        for profile, figure in _HOP_STATEMENT.findall(_read(path)):
            expected = config[profile.lower()][1]
            if figure != expected:
                bad.append(
                    f"{path.relative_to(_ROOT)}: {profile} {figure} hops"
                    f" vs config {expected}"
                )
    assert not bad, f"hop counts that drift from RESEARCH_CONFIG depth_profiles: {bad}"


def test_hop_config_max_matches_profiles():
    """RESEARCH_CONFIG's own maxima (hop_config max, defaults max_hops) = the largest profile."""
    text = _read(_CONFIG)
    largest = max(int(hops) for _, hops in _config_profiles().values())
    attr = re.search(r'<hop_config[^>]*\bmax="(\d+)"', text)
    default = re.search(r"\bmax_hops: (\d+)", text)
    assert attr and default, "RESEARCH_CONFIG.md lacks hop_config max= or max_hops:"
    assert int(attr.group(1)) == largest, (
        f"hop_config max={attr.group(1)} but the deepest profile has {largest} hops"
    )
    assert int(default.group(1)) == largest, (
        f"defaults max_hops: {default.group(1)} but the deepest profile has {largest} hops"
    )


# --------------------------------------------------------------------- T5 --
def test_readme_command_file_claims_resolve():
    """'`/sc:x` … `.claude/<file>`' on one README line: commands/x.md names that file (D-05).

    The claimant is the last `/sc:x` on the line, across table cells
    (06-verify Z-7).
    """
    bad = []
    for line in _read(_README).splitlines():
        claimant = None
        for m in re.finditer(r"/sc:([\w-]+)|`(\.claude/[\w./-]+)`", line):
            if m.group(1):
                claimant = m.group(1)
            elif claimant:
                leaf = m.group(2).rstrip("/").split("/")[-1]
                body = _read(_SRC / "commands" / f"{claimant}.md")
                if leaf not in body:
                    bad.append(f"/sc:{claimant} ↔ {m.group(2)}")
    assert not bad, f"README credits a command with a file its body never names: {bad}"


# --------------------------------------------------------------------- T7 --
def _component_leaves() -> set[str]:
    leaves = set()
    for _, target, _ in COMPONENTS.values():
        leaves.add(target if target == "commands/sc" else target.split("/")[-1])
    return leaves


def test_install_surfaces_name_every_component():
    """README's install tree and install/uninstall help name every component dir (D-16)."""
    text = _read(_README)
    m = re.search(r"What gets installed.*?```\n(.*?)```", text, re.S)
    assert m, "README.md has no 'What gets installed' tree"
    surfaces = {"README.md 'What gets installed'": m.group(1)}
    help_text = _cli_help()
    surfaces["superclaude install --help"] = help_text["superclaude install"]
    surfaces["superclaude uninstall --help"] = help_text["superclaude uninstall"]
    bad = [
        f"{label} omits {leaf}"
        for label, body in surfaces.items()
        for leaf in sorted(_component_leaves())
        if leaf not in body
    ]
    assert not bad, f"install surfaces missing a component: {bad}"


# -------------------------------------------------- review-reflect-gates --
# RULES_DOCS does not load on /sc:test, /sc:review, /sc:implement or
# /sc:reflect (context_loader TRIGGER_MAP), so those commands carry the
# review-reflect gates themselves; the README states them for users. The
# guard holds the words that carry each rule, so rewording passes and deleting
# or softening a rule fails (docs/features/review-reflect-gates,
# plan-complete-order).
_GATE_ANCHORS = {
    "gates": [
        "/sc:review -> fix -> /sc:review",
        "Critical or Important",
        "shipped content",
        "acceptance criteria",
        "single fix round",
        "/sc:test -> /sc:reflect",
        "goes to /sc:reflect",
        "/sc:reflect -> done",
        "on the user's yes to Plan-Close",
        "names the fix left unreviewed",
        "or accepted by the user",
        "no code commit follows the Proof's `Result:` sha",
    ],
    "rules": [
        "only when every task checkbox is checked",
        "no commit after that line's sha changes code",
        "re-run or a Critical or Important finding in its work sets a `complete` plan back",
        "from a green run or with the user's recorded acceptance",
        "the user sets `complete` at the /sc:reflect Plan-Close step",
        "back to `implementing`",
    ],
    "test Report": [
        "not done until /sc:reflect",
        "Critical or Important",
        "another review",
        "/sc:reflect does not replace",
    ],
    "review Process": [
        "Critical or Important",
        "comes back for another round",
        "the user accepts the open findings or waives the re-review",
        "acceptance criteria",
        "no Critical or Important finding",
        "Suggestions",
        "single fix round",
    ],
    "implement Integrate": [
        "never sets the plan (index) or the README `complete`",
        "Plan-Close",
        "sets it back to `implementing`",
        "the README `phase:` never moves back",
        "rewrites `Result:`",
        "A fix to a Critical or Important review finding",
        "Every later code change re-runs the Proof",
        "counts only once the user accepts it",
        "back to /sc:review",
        "even when its Proof is green",
        "single fix round",
    ],
    "implement Load": [
        "is missing or has a code commit after its sha",
        "the Integrate step's Proof re-run",
    ],
    "reflect Plan-Close": [
        "every task box is checked",
        "is green or marked accepted by the user",
        "no commit after its sha changes code",
        "(3) every Critical or Important review finding is fixed or accepted",
        "an open box, a missing `Result:` line or a code commit after its sha",
        "an open finding or a red `Result:` to the user",
        "whose `Result:` is red and not accepted, or whose condition (3) fails",
        "is proposed back to `implementing`, the README `phase:` unchanged",
        "any other failing condition leaves it `complete`",
        "the review findings and `git log`",
        "shipped content has had a /sc:review round after it, or the user waived that round",
        "without re-running the Proof",
        "a fix waiting for review to /sc:review",
        "all three hold",
        "only when the user says yes",
        "in a feature folder",
        "/sc:implement --plan",
    ],
    "reflect bounds": ["without the user's yes or with a Plan-Close condition unmet"],
    "intent Run": [
        "ask nothing",
        "Stop and report instead",
        "cannot be undone or reaches other people",
        "a Critical finding or a red Proof remains after one fix round",
        "fix the Critical and Important ones once",
        "rewrite `Result:`",
        "Plan-Close → propose, write nothing",
        "leave the step Plan-Close names to the Report step",
    ],
    "intent Report": [
        "Plan-Close result",
        "the step Plan-Close named",
        "setting the plan `complete`",
    ],
    "README implement row": [
        "no code commit follows the plan's `Result:` sha",
        "stays `implementing`",
    ],
    "README review row": ["reviewed again", "acceptance criteria"],
    "README reflect row": [
        "done only after this",
        "it proposes marking the plan `complete`, which you confirm",
    ],
    "README --through": [
        "leaves marking the plan complete, any review round its fix still needs"
    ],
}
# Words that soften a rule into a suggestion. Added conditions and moved
# clauses are left to the canary probes.
_SOFTENER = re.compile(
    r"\b(may|might|optionally|if needed|consider|could|ideally|where useful|"
    r"where possible|if you like|preferably|try to|unless|need not|no longer|"
    r"when convenient)\b",
    re.I,
)


def _gate_texts() -> dict[str, str]:
    rules = _read(_SRC / "core" / "rules" / "RULES_DOCS.md")
    gates = re.search(r"<workflow_gates>(.*?)</workflow_gates>", rules, re.S)
    assert gates, "RULES_DOCS.md has no <workflow_gates>"
    plan_docs = re.search(r"^\s*Plan docs \(feature or standalone\):.*$", rules, re.M)
    assert plan_docs, "RULES_DOCS.md has no Plan docs line"
    texts = {"gates": gates.group(1), "rules": plan_docs.group(0)}
    for name, step in (
        ("test", "Report"),
        ("review", "Process"),
        ("implement", "Load"),
        ("implement", "Integrate"),
        ("reflect", "Plan-Close"),
        ("intent", "Run"),
        ("intent", "Report"),
    ):
        body = _read(_SRC / "commands" / f"{name}.md")
        line = re.search(rf"^\s*\d+(?:\.\d+)?\. {step}(?: \([^)]*\))?:.*$", body, re.M)
        assert line, f"{name}.md has no {step} step"
        texts[f"{name} {step}"] = line.group(0)
    readme = _read(_README)
    for name, row in (
        ("review", "/sc:review --scope branch"),
        ("implement", "/sc:implement --plan"),
        ("reflect", "/sc:reflect"),
    ):
        line = re.search(rf"^\| `{re.escape(row)}` \|.*$", readme, re.M)
        assert line, f"README has no {row} row"
        texts[f"README {name} row"] = line.group(0)
    through = re.search(r"^`/sc:intent --through` .*$", readme, re.M)
    assert through, "README has no --through paragraph"
    texts["README --through"] = through.group(0)
    bounds = re.search(
        r"<never>.*?</never>", _read(_SRC / "commands" / "reflect.md"), re.S
    )
    assert bounds, "reflect.md has no <never>"
    texts["reflect bounds"] = bounds.group(0)
    return texts


@pytest.mark.parametrize("where", sorted(_GATE_ANCHORS))
def test_review_reflect_gate_anchors(where):
    """Each place that carries the review-reflect gates keeps its rule."""
    text = _gate_texts()[where]
    missing = [a for a in _GATE_ANCHORS[where] if a not in text]
    assert not missing, f"{where} lost {missing}"
    assert not _SOFTENER.search(text), where


def test_readme_chains_end_at_a_workflow_gate():
    """Every command in the README Medium and Large chains is a workflow gate
    target, /sc:reflect sits outside the optional part of both, and /sc:test
    hands off to /sc:reflect first (the chains ended at /sc:reflect while the
    gates ended at /sc:test, so reflect was skipped)."""
    text = _read(_README)
    rows = re.findall(r"^\| \*\*(Medium|Large)\*\* \|[^|]*\| ([^|]*) \|$", text, re.M)
    assert {tier for tier, _ in rows} == {"Medium", "Large"}, rows
    required = {tier: re.sub(r"\(.*?\)", "", chain) for tier, chain in rows}
    chain_cmds = {
        cmd
        for chain in required.values()
        for cmd in re.findall(r"`(/sc:[a-z-]+)", chain)
    }
    gates = _gate_texts()["gates"]
    targets = set(re.findall(r"(?:->|\|)\s*(/sc:[a-z-]+)", gates))
    missing = sorted(chain_cmds - targets - {"/sc:intent"})
    assert not missing, f"README chain commands no workflow gate leads to: {missing}"
    for tier, chain in required.items():
        assert "`/sc:reflect`" in chain, tier
    handoff = re.search(
        r'<handoff next="([^"]*)"', _read(_SRC / "commands" / "test.md")
    )
    assert handoff and handoff.group(1).split()[0] == "/sc:reflect", handoff
    # The retired "/sc:test -> done" gate is named nowhere in shipped content.
    retired = [
        str(p.relative_to(_SRC))
        for p in _SRC.rglob("*.md")
        if re.search(r"/sc:test`?\s*(->|→)\s*done", _read(p))
    ]
    assert not retired, f"retired /sc:test -> done gate named in: {retired}"
    # Plan-Close condition (2) is "no code commit after the Result: sha"; the
    # older "Result: names the last code commit" wording contradicts it.
    stale = [
        str(p.relative_to(_SRC))
        for p in _SRC.rglob("*.md")
        if re.search(r"last (?:code commit|commit that changed code)", _read(p))
    ]
    if re.search(r"last (?:code commit|commit that changed code)", text):
        stale.append("README.md")
    assert not stale, f"old Result: wording in: {stale}"
    # Other README chains that run /sc:plan end with /sc:reflect too.
    for goal in ("Investigate a bug", "Refactor"):
        row = re.search(rf"^\| \*\*{goal}\*\* \| (.*) \|$", text, re.M)
        assert row and "/sc:plan" in row.group(1), goal
        assert row.group(1).rstrip().endswith("`/sc:reflect`"), goal
