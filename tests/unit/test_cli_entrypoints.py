"""Console-subcommand entry points for the script subpackages.

`superclaude auto-improve` and `superclaude parallel-ab` exist because the
workers import `superclaude.scripts.<pkg>.*`, which only the installing
interpreter can resolve — a bare `python -m superclaude.scripts.parallel_ab`
outside a checkout raises ModuleNotFoundError. These tests pin the two things
that break silently: that the subcommands are registered under those exact
names, and that argv (including `--help` and unknown options) reaches the
worker's own argparse parser rather than being eaten by Click.

Filed at tests/unit/ top level on purpose: pyproject addopts carries
`--ignore=tests/unit/scripts`, so a guard under tests/unit/scripts/ never runs.
"""

import re
from pathlib import Path

import pytest
from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[2]


def _all_output(result) -> str:
    """stdout + stderr — argparse writes usage errors to stderr."""
    text = result.output or ""
    try:
        text += result.stderr or ""
    except ValueError:  # stderr not captured separately on older Click
        pass
    return text


class TestPassthroughSubcommands:
    """Registration and argv forwarding for the two new console entries."""

    def test_auto_improve_subcommand_registered(self):
        from superclaude.cli.main import main as cli

        assert "auto-improve" in cli.commands

    def test_parallel_ab_subcommand_registered(self):
        from superclaude.cli.main import main as cli

        assert "parallel-ab" in cli.commands

    def test_auto_improve_help_names_console_script(self):
        from superclaude.cli.main import main as cli

        result = CliRunner().invoke(cli, ["auto-improve", "--help"])

        assert result.exit_code == 0, _all_output(result)
        output = _all_output(result)
        assert "usage: superclaude auto-improve" in output, output
        assert "-m superclaude.scripts" not in output, output

    def test_parallel_ab_help_names_console_script(self):
        from superclaude.cli.main import main as cli

        result = CliRunner().invoke(cli, ["parallel-ab", "--help"])

        assert result.exit_code == 0, _all_output(result)
        output = _all_output(result)
        assert "usage: superclaude parallel-ab" in output, output
        assert "-m superclaude.scripts" not in output, output

    def test_auto_improve_status_forwards_argv(self, tmp_path):
        # Multi-token argv has to reach the worker's parser unmangled. tmp_path
        # has no .worktrees/, which coordinator.status_mode answers with this
        # exact string.
        from superclaude.cli.main import main as cli

        result = CliRunner().invoke(
            cli, ["auto-improve", "--project", str(tmp_path), "--status"]
        )

        assert result.exit_code == 0, _all_output(result)
        assert "No prior runs" in _all_output(result)

    def test_auto_improve_missing_required_flags_exits_2(self, tmp_path):
        from superclaude.cli.main import main as cli

        result = CliRunner().invoke(cli, ["auto-improve", "--project", str(tmp_path)])

        assert result.exit_code == 2, _all_output(result)
        assert "--eval-cmd and --metric are required" in _all_output(result)

    def test_parallel_ab_missing_spec_exits_2(self):
        from superclaude.cli.main import main as cli

        result = CliRunner().invoke(cli, ["parallel-ab"])

        assert result.exit_code == 2, _all_output(result)

    def test_parallel_ab_unknown_option_reaches_worker_not_click(self):
        # ignore_unknown_options must route the error to argparse; Click's own
        # "no such option" message would name Click, not the worker.
        from superclaude.cli.main import main as cli

        result = CliRunner().invoke(cli, ["parallel-ab", "--nope"])

        assert result.exit_code == 2, _all_output(result)
        assert "superclaude parallel-ab" in _all_output(result)


# The README must never hand a reader a bare `python -m superclaude.scripts.<pkg>`
# to run: the install tree ships content, not the package, so that form resolves
# only under the installing interpreter (gotcha `script-needs-console-entry`).
# `uv run python -m ...` is the legitimate dev-checkout spelling.
#
# Four properties, the first three fixing a measured defect in the earlier
# per-line form and the fourth a measured defect the sentence rewrite introduced:
#  * whitespace is flattened first — a wrap landing mid-command used to break the
#    literal being searched for, leaving the guard matching NOTHING anywhere
#    (measured: 6 of 17 textwrap widths in 60..140);
#  * the unit is the SENTENCE, not the line — the Subpackages paragraph carries
#    the legitimate and the illegitimate mention in one line today, so any
#    re-wrap split them apart and turned the guard red for no defect (measured:
#    9 of those 17 widths, and the one-sentence-per-line style);
#  * the `uv run` exemption is ADJACENCY-scoped — as a substring test over the
#    whole line it laundered a real bare prescription that merely shared a line
#    with the words (measured: such a line passed the old form silently);
#  * the counter-example exemption is SHAPE-anchored, not marker-anywhere — the
#    split unit is a sentence only where terminal punctuation exists, so a
#    markdown table collapses into ONE unit and a row could then borrow the word
#    ModuleNotFoundError from a neighboring row (measured: such a table is caught
#    by the per-line form and was MISSED by a marker-anywhere exemption; the
#    README's longest flattened unit is 691 chars, so that laundering surface was
#    wide).
# The README may still NAME the bare form in order to say it fails; that one
# sentence is exempt because it OPENS with the counter-example frame and names
# the failure — not because the word turns up somewhere in the same unit.
# A proximity window ("marker within N chars of the match") was the alternative
# and is not viable: measured forward distances are 33 chars for the legitimate
# sentence and 42 for the adversarial table, while ordinary rewordings of the
# legitimate sentence already reach 45 — no N separates them.
_BARE_MODULE_INVOCATION = re.compile(r"(?<!uv run )python -m superclaude\.scripts\.")
_COUNTEREXAMPLE_MARKER = "ModuleNotFoundError"
_COUNTEREXAMPLE_SENTENCE = re.compile(rf"^A bare\b.*\b{_COUNTEREXAMPLE_MARKER}\b")


def _bare_module_prescriptions(text: str) -> list[str]:
    """Sentences handing the reader a bare `python -m superclaude.scripts.<pkg>`."""
    flattened = re.sub(r"\s+", " ", text)
    return [
        sentence
        for sentence in re.split(r"(?<=[.!?])\s+", flattened)
        if _BARE_MODULE_INVOCATION.search(sentence)
        and not _COUNTEREXAMPLE_SENTENCE.search(sentence)
    ]


class TestScriptsReadmeDocumentsConsoleEntries:
    """The README row for parallel_ab is its only documented entry point."""

    def test_readme_names_console_entries(self):
        text = (REPO_ROOT / "src" / "superclaude" / "scripts" / "README.md").read_text(
            encoding="utf-8"
        )

        assert "superclaude auto-improve" in text
        assert "superclaude parallel-ab" in text

    def test_readme_never_prescribes_bare_module_invocation(self):
        text = (REPO_ROOT / "src" / "superclaude" / "scripts" / "README.md").read_text(
            encoding="utf-8"
        )

        offenders = _bare_module_prescriptions(text)
        assert offenders == [], offenders


# A guard nobody probes is a guard nobody knows is inverted: the sweep above
# passes just as happily on a predicate that matches nothing — which is what the
# per-line form did under half the re-wraps tried. These pin what the predicate
# must catch and what it must leave alone.
# Four of these flip against the per-line form (beside-an-unrelated-uv-run,
# wrapped-mid-command, counterexample, uv-run-wrapped); the last one flips
# against the marker-anywhere exemption instead — the per-line form caught that
# table, so it pins a regression the sentence rewrite introduced rather than one
# the sentence rewrite fixed.
@pytest.mark.parametrize(
    ("passage", "is_prescription"),
    [
        (
            "Start it with `python -m superclaude.scripts.auto_improve --project .`.",
            True,
        ),
        (
            "To start a run: `python -m superclaude.scripts.auto_improve`"
            " (in a dev checkout, `uv run` it instead).",
            True,
        ),
        ("Run\n`python -m\nsuperclaude.scripts.auto_improve`\nnow.", True),
        (
            "Subpackages import `superclaude.*`.\nA bare\n"
            "`python -m superclaude.scripts.<pkg>` outside a checkout raises\n"
            "ModuleNotFoundError.",
            False,
        ),
        (
            "Inside a dev checkout"
            " `uv run python -m superclaude.scripts.<pkg>` is equivalent.",
            False,
        ),
        (
            "Inside a dev checkout"
            " `uv run\npython -m superclaude.scripts.<pkg>` is equivalent.",
            False,
        ),
        ("Entry: `superclaude parallel-ab <variants.yaml>`.", False),
        (
            "| `auto_improve/` | Entry:"
            " `python -m superclaude.scripts.auto_improve` |\n"
            "| `parallel_ab/` | raises ModuleNotFoundError |",
            True,
        ),
    ],
    ids=[
        "bare-module-prescription",
        "bare-prescription-beside-an-unrelated-uv-run",
        "bare-prescription-wrapped-mid-command",
        "counterexample-naming-its-own-failure",
        "uv-run-dev-form",
        "uv-run-dev-form-wrapped-mid-command",
        "console-subcommand",
        "table-row-borrowing-a-neighbor-rows-marker",
    ],
)
def test_bare_module_prescription_discriminates(passage, is_prescription):
    assert bool(_bare_module_prescriptions(passage)) is is_prescription
