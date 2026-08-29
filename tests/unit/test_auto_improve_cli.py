"""Duration parsing for `superclaude auto-improve`.

`--budget` and `--cycle-timeout` both go through `_parse_duration`, which is an
argparse `type=` converter: everything it rejects becomes a usage error (exit 2)
with per-argument attribution instead of a traceback or a silently broken run.

Filed at tests/unit/ top level on purpose: pyproject addopts carries
`--ignore=tests/unit/scripts`, so a guard under tests/unit/scripts/ never runs.
"""

import argparse

import pytest
from click.testing import CliRunner

from superclaude.scripts.auto_improve.cli import _build_parser, _parse_duration


def _all_output(result) -> str:
    """stdout + stderr — argparse writes usage errors to stderr."""
    text = result.output or ""
    try:
        text += result.stderr or ""
    except ValueError:  # stderr not captured separately on older Click
        pass
    return text


# Accepted spellings. These are the CONTRACT — the non-positive guard below is
# an input-validation fix, not a format change, so every one of these must keep
# converting to the same integer it did before that guard existed.
@pytest.mark.parametrize(
    ("value", "seconds"),
    [
        ("8h", 28800),
        ("30m", 1800),
        ("120s", 120),
        ("600", 600),
        ("0.5h", 1800),
    ],
)
def test_accepted_durations_convert(value, seconds):
    assert _parse_duration(value) == seconds


# Malformed input. Rejected before the non-positive guard was added and still
# rejected by the same `except (ValueError, OverflowError)` branch: 'infh' and
# '1e400h' overflow int(), 'nanh' is a ValueError out of int(nan).
@pytest.mark.parametrize("value", ["bogus", "", "infh", "nanh", "1e400h", "  "])
def test_malformed_durations_are_usage_errors(value):
    with pytest.raises(argparse.ArgumentTypeError):
        _parse_duration(value)


# The regression this file exists for. Every one of these FLIPPED: before the
# guard they all converted silently (measured: '-5'->-5, '0'->0, '-1'->-1,
# '-0.5h'->-1800, '0h'/'0m'/'0s'/'0.4s'->0, '-3600'->-3600), and a non-positive
# value is not merely odd, it breaks the run at its first guard check:
#   * budget    -> Coordinator.run() sets `deadline = monotonic() + budget`, so
#                  BudgetGuard.check() fails immediately, the loop breaks before
#                  a single cycle, and --status shows a truncated run, no error.
#   * timeout   -> every subprocess.run(timeout=<=0) raises TimeoutExpired at
#                  once, which surfaces as a bogus "baseline failed" instead.
# The accepted/malformed sets above do NOT flip, which is what makes this set
# the discriminator rather than decoration.
@pytest.mark.parametrize(
    "value", ["-5", "0", "-1", "-0.5h", "0h", "0m", "0s", "-3600", "0.4s"]
)
def test_non_positive_durations_are_usage_errors(value):
    with pytest.raises(argparse.ArgumentTypeError, match="positive"):
        _parse_duration(value)


class TestParserWiring:
    """The converter is only useful if the parser actually routes through it."""

    def test_defaults_convert_to_seconds(self):
        args = _build_parser("superclaude auto-improve").parse_args([])

        assert args.budget == 28800
        assert args.cycle_timeout == 600

    @pytest.mark.parametrize(
        ("argv", "flag"),
        [
            (["--budget", "-5"], "--budget"),
            (["--budget", "0"], "--budget"),
            (["--cycle-timeout", "-1"], "--cycle-timeout"),
        ],
    )
    def test_non_positive_flag_exits_2_with_attribution(self, argv, flag, capsys):
        parser = _build_parser("superclaude auto-improve")

        with pytest.raises(SystemExit) as exc:
            parser.parse_args(argv)

        assert exc.value.code == 2
        assert f"argument {flag}:" in capsys.readouterr().err

    def test_non_positive_budget_exits_2_through_console_entry(self, tmp_path):
        # End-to-end through Click: the same shape as every other bad flag on
        # this command, rather than a run that starts and stops doing nothing.
        from superclaude.cli.main import main as cli

        result = CliRunner().invoke(
            cli,
            [
                "auto-improve",
                "--project",
                str(tmp_path),
                "--eval-cmd",
                "true",
                "--metric",
                "passed",
                "--budget",
                "0",
            ],
        )

        assert result.exit_code == 2, _all_output(result)
        assert "argument --budget:" in _all_output(result)
        assert not (tmp_path / ".worktrees").exists()
