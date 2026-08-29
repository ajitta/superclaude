"""`superclaude context explain` / `superclaude context reset`.

Both scripts behind these subcommands import ``superclaude.*``, so neither is
runnable as a bare ``python3 ~/.claude/superclaude/scripts/X.py`` — the console
subcommand is the only human path (gotchas/hooks.md ``script-needs-console-entry``).

Every test pins ``CLAUDE_PROJECT_DIR`` as well as the CWD: ``project_root()``
reads the env first, so ``monkeypatch.chdir`` alone would let the resolvers
write into the real repo or the real ``~/.claude``
(gotchas/hooks.md ``test-anchor-env``).

This module lives at ``tests/unit/`` top level on purpose — ``pyproject.toml``
carries ``--ignore=tests/unit/scripts``, so a file placed there is collected by
nothing.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from superclaude.cli.main import main
from superclaude.utils import context_cache_file, hook_state_dir
from tests.unit.prose_guard import prose_units

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONTENT_ROOT = REPO_ROOT / "src" / "superclaude"
LOADER_SCRIPT = CONTENT_ROOT / "scripts" / "context_loader.py"


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A sandboxed project whose hook state cannot escape into the real tree.

    The ``.claude/superclaude`` marker keeps ``claude_base()`` — and therefore
    ``hook_state_dir()`` — inside ``tmp_path``. ``SUPERCLAUDE_PATH`` pins the
    content root to this checkout so what the loader injects does not depend on
    whatever happens to be installed on the machine running the suite. Both are
    the same pins ``tests/unit/test_context_loader.py``'s ``run_loader`` uses.
    """
    (tmp_path / ".claude" / "superclaude").mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.setenv("SUPERCLAUDE_PATH", str(CONTENT_ROOT))
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    return tmp_path


@pytest.fixture
def scoped_install(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A project-scope install with ``SUPERCLAUDE_PATH`` deliberately NOT pinned.

    ``_context_content_root`` short-circuits on that variable, so the anchor
    rules underneath it are only reachable with it unset. ``CLAUDE_PROJECT_DIR``
    is still pinned into ``tmp_path`` (gotchas/hooks.md ``test-anchor-env``).

    The CWD is a subdirectory carrying no marker of its own: that is the shape
    where the shell rule and the hook's anchor answer differently, and it means
    the CWD candidate deliberately does NOT stay under ``tmp_path``. ``scoped()``
    finds no ``.claude/superclaude`` under ``tmp_path/sub`` and falls back to the
    real ``~/.claude/superclaude`` — which is the value
    ``test_a_disagreement_between_the_anchors_is_never_silent`` asserts on.

    Safety is therefore NOT "both candidates are inside ``tmp_path``". It is that
    the parent only READS — resolve two paths, ``is_dir()`` them, echo them — and
    that the child gets ``CLAUDE_PROJECT_DIR`` pinned to its own throwaway
    tempdir and ``SUPERCLAUDE_PATH`` pinned to the ANCHOR answer, so every loader
    write lands in that sandbox. Do not add a WRITE-path test under this fixture:
    nothing here confines a writer and the real ``~/.claude`` is one resolver
    call away (``test-anchor-env`` records 19 stray state files and 33 fixture
    lines appended to the real insights.jsonl from exactly that mistake).
    """
    (tmp_path / ".claude" / "superclaude").mkdir(parents=True, exist_ok=True)
    (tmp_path / "sub").mkdir(exist_ok=True)
    monkeypatch.delenv("SUPERCLAUDE_PATH", raising=False)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    monkeypatch.chdir(tmp_path / "sub")
    return tmp_path


def _state_snapshot() -> dict[str, int]:
    """Every file under the active hook state dir, by name and size."""
    state = hook_state_dir()
    if not state.is_dir():
        return {}
    return {
        str(p.relative_to(state)): p.stat().st_size
        for p in state.rglob("*")
        if p.is_file()
    }


def _run_loader_directly(prompt: str, project_dir: Path, session_id: str) -> str:
    """Invoke context_loader.py the way Claude Code does, with no isolation.

    The control for the isolation test: it proves the snapshot above can in fact
    see the loader writing, so an empty diff means isolation and not a blind
    detector.
    """
    import os

    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    env["SUPERCLAUDE_PATH"] = str(CONTENT_ROOT)
    env["CLAUDE_SHOW_SKILLS"] = "0"
    result = subprocess.run(
        [sys.executable, str(LOADER_SCRIPT)],
        input=json.dumps({"prompt": prompt, "session_id": session_id}),
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


class TestContextGroupRegistration:
    def test_group_and_both_verbs_are_registered(self):
        assert "context" in main.commands
        group = main.commands["context"]
        assert set(group.commands) == {"explain", "reset"}


class TestContextExplain:
    def test_it_names_the_file_and_the_trigger_that_fired(self, project: Path):
        result = CliRunner().invoke(
            main, ["context", "explain", "--serena rename this symbol"]
        )

        assert result.exit_code == 0, result.output
        assert "mcp/MCP_Serena.md" in result.output
        assert "--serena" in result.output

    def test_a_prompt_starting_with_a_flag_is_not_read_as_an_option(
        self, project: Path
    ):
        """`--serena` must reach the loader, not Click's option parser."""
        result = CliRunner().invoke(
            main, ["context", "explain", "--serena", "rename", "this"]
        )

        assert result.exit_code == 0, result.output
        assert "no such option" not in result.output
        assert "mcp/MCP_Serena.md" in result.output

    def test_it_reports_token_cost_against_the_loader_budget(self, project: Path):
        result = CliRunner().invoke(main, ["context", "explain", "--brainstorm a CLI"])

        assert result.exit_code == 0, result.output
        assert "modes/MODE_Brainstorming.md" in result.output
        assert "budget:  8000 tokens" in result.output
        # Tier 2 full-.md injection: the loader declares its own count, so the
        # report must carry a non-zero number rather than a placeholder.
        assert "~0 " not in result.output

    def test_it_names_what_the_budget_dropped(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """The budget lives in the env, so the report must read it per run —
        context_loader freezes MAX_TOKENS_ESTIMATE at import."""
        monkeypatch.setenv("CLAUDE_CONTEXT_MAX_TOKENS", "500")

        result = CliRunner().invoke(
            main,
            ["context", "explain", "--frontend-verify --brainstorm /sc:implement x"],
        )

        assert result.exit_code == 0, result.output
        assert "budget:  500 tokens" in result.output
        assert "dropped by the token budget:" in result.output
        assert "core/rules/RULES_QUALITY.md" in result.output

    def test_an_untriggering_prompt_injects_nothing(self, project: Path):
        result = CliRunner().invoke(
            main, ["context", "explain", "please rename the local variable"]
        )

        assert result.exit_code == 0, result.output
        assert "would inject no context files." in result.output

    def test_execution_directives_are_reported(self, project: Path):
        result = CliRunner().invoke(
            main, ["context", "explain", "--loop fix the tests"]
        )

        assert result.exit_code == 0, result.output
        assert "execution directives" in result.output
        assert "--loop" in result.output

    def test_an_empty_prompt_is_a_usage_error(self, project: Path):
        result = CliRunner().invoke(main, ["context", "explain"])

        assert result.exit_code != 0
        assert "PROMPT is required" in result.output

    def test_it_writes_nothing_into_the_real_hook_state(self, project: Path):
        """The correctness bar: a dry run must not poison the next real prompt.

        Both writers are covered — the session dedup cache
        (``claude_context_*.txt``) and the MCP fallback ledger
        (``mcp_fallbacks.json``), which hooks/mcp_fallback.py writes on a
        server's first reference in a session.
        """
        before = _state_snapshot()

        result = CliRunner().invoke(
            main, ["context", "explain", "--serena --play /sc:implement x"]
        )
        assert result.exit_code == 0, result.output

        assert _state_snapshot() == before
        assert not list(project.rglob("claude_context_*.txt"))
        assert not list(project.rglob("mcp_fallbacks.json"))

    def test_the_isolation_check_can_actually_see_a_write(self, project: Path):
        """Control for the test above: the unsandboxed loader DOES write."""
        before = _state_snapshot()

        _run_loader_directly("--serena --play /sc:implement x", project, "control")

        after = _state_snapshot()
        assert after != before
        assert any(name.startswith("claude_context_") for name in after)

    def test_it_names_the_loader_copy_that_actually_ran(self, project: Path):
        """The hook runs the INSTALLED loader ({{SCRIPTS_PATH}}/context_loader.py);
        explain runs this package's copy. Claiming to run "the UserPromptSubmit
        hook" without naming the file lets a user on a drifted install chase a
        phantom — explain describing the new loader, the hook running the old."""
        result = CliRunner().invoke(main, ["context", "explain", "--serena rename x"])

        assert result.exit_code == 0, result.output
        assert f"loader:  {LOADER_SCRIPT}" in result.output

    def test_a_drifted_installed_copy_is_flagged(
        self, project: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Naming the two paths is not enough on its own: a healthy install also
        has two different paths. Only a byte difference distinguishes drift."""
        stale = tmp_path / "installed-content"
        (stale / "scripts").mkdir(parents=True)
        (stale / "scripts" / "context_loader.py").write_text(
            "# an older context_loader\n", encoding="utf-8"
        )
        monkeypatch.setenv("SUPERCLAUDE_PATH", str(stale))

        result = CliRunner().invoke(main, ["context", "explain", "--serena rename x"])

        assert result.exit_code == 0, result.output
        assert "bytes differ" in result.output
        assert str(stale / "scripts" / "context_loader.py") in result.output

    def test_a_byte_identical_installed_copy_is_not_flagged(self, project: Path):
        """Control for the above: the fixture points SUPERCLAUDE_PATH at this
        checkout, so the copy the hook would run IS the copy that ran."""
        result = CliRunner().invoke(main, ["context", "explain", "--serena rename x"])

        assert result.exit_code == 0, result.output
        assert "bytes differ" not in result.output

    def test_the_suppressed_skills_banner_is_disclosed(self, project: Path):
        """explain forces CLAUDE_SHOW_SKILLS=0, so the once-per-session
        "N skills installed" banner a real first prompt receives never appears.
        Suppressing it is defensible; suppressing it silently is not."""
        result = CliRunner().invoke(main, ["context", "explain", "--serena rename x"])

        assert result.exit_code == 0, result.output
        assert "skills installed" not in result.output, "banner really is suppressed"
        assert "banner suppressed" in result.output


class TestContextContentRoot:
    """The content root explain pins into the child must be the hook's.

    ``_run_loader_isolated`` passes ``SUPERCLAUDE_PATH`` down, so the CLI's
    answer overrides the loader's own resolution. Resolved from the CWD alone,
    an explain run from a subdirectory of a project-scope install reported the
    user-scope content set — files and costs the hook would never inject.
    """

    def test_the_project_anchor_beats_the_cwd(self, scoped_install: Path):
        result = CliRunner().invoke(main, ["context", "explain", "--serena rename x"])

        assert result.exit_code == 0, result.output
        expected = scoped_install / ".claude" / "superclaude"
        assert f"content: {expected}" in result.output

    def test_a_disagreement_between_the_anchors_is_never_silent(
        self, scoped_install: Path
    ):
        result = CliRunner().invoke(main, ["context", "explain", "--serena rename x"])

        assert result.exit_code == 0, result.output
        assert f"$CLAUDE_PROJECT_DIR={scoped_install}" in result.output
        assert str(Path.home() / ".claude" / "superclaude") in result.output

    def test_outside_a_session_the_cwd_still_decides(
        self, scoped_install: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """$CLAUDE_PROJECT_DIR exists only inside Claude Code. Unset, the shell
        rule is the whole answer — and with no second opinion, no note."""
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
        monkeypatch.chdir(scoped_install)

        result = CliRunner().invoke(main, ["context", "explain", "--serena rename x"])

        assert result.exit_code == 0, result.output
        expected = scoped_install / ".claude" / "superclaude"
        assert f"content: {expected}" in result.output
        assert "$CLAUDE_PROJECT_DIR=" not in result.output

    def test_superclaude_path_overrides_both_anchors(
        self, scoped_install: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """It is the loader's own first priority, so it stays the CLI's too."""
        monkeypatch.setenv("SUPERCLAUDE_PATH", str(CONTENT_ROOT))

        result = CliRunner().invoke(main, ["context", "explain", "--serena rename x"])

        assert result.exit_code == 0, result.output
        assert f"content: {CONTENT_ROOT}" in result.output
        assert "$CLAUDE_PROJECT_DIR=" not in result.output


class TestContextReset:
    def test_it_removes_the_session_cache_named_by_the_env_var(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "s1")
        cache = context_cache_file("s1")
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text("mcp/MCP_Serena.md", encoding="utf-8")

        result = CliRunner().invoke(main, ["context", "reset"])

        assert result.exit_code == 0, result.output
        assert not cache.exists()
        assert str(cache) in result.output
        assert "reset 1 cache file(s)" in result.output

    def test_an_explicit_session_beats_the_env_var(
        self, project: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "from-env")
        chosen = context_cache_file("chosen")
        other = context_cache_file("from-env")
        chosen.parent.mkdir(parents=True, exist_ok=True)
        chosen.write_text("x", encoding="utf-8")
        other.write_text("x", encoding="utf-8")

        result = CliRunner().invoke(main, ["context", "reset", "--session", "chosen"])

        assert result.exit_code == 0, result.output
        assert not chosen.exists()
        assert other.exists(), "the env var's session must not be touched"

    def test_with_no_session_it_falls_back_to_the_project_only_cache(
        self, project: Path
    ):
        """CLAUDE_CODE_SESSION_ID is not set in every environment."""
        cache = context_cache_file()
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text("modes/MODE_Brainstorming.md", encoding="utf-8")

        result = CliRunner().invoke(main, ["context", "reset"])

        assert result.exit_code == 0, result.output
        assert not cache.exists()
        assert "project-only fallback" in result.output

    def test_zero_matches_is_never_silent(self, project: Path):
        """The measured trap: with no session id the project-only name often
        does not exist, and the user believes the reset worked."""
        result = CliRunner().invoke(main, ["context", "reset"])

        assert result.exit_code == 0, result.output
        assert "nothing to reset (looked at " in result.output
        assert str(context_cache_file()) in result.output

    def test_the_resolved_path_is_always_printed(self, project: Path):
        result = CliRunner().invoke(main, ["context", "reset", "--session", "abc"])

        assert result.exit_code == 0, result.output
        assert f"cache:   {context_cache_file('abc')}" in result.output

    def test_a_session_id_that_sanitizes_to_empty_is_not_counted_twice(
        self, project: Path
    ):
        """``session_slug()`` strips an id to [A-Za-z0-9_-], so ``--session '///'``
        resolves to the same file as the project-only fallback. Undeduplicated,
        one file was listed twice and reported as "reset 2 cache file(s)"."""
        assert context_cache_file("///") == context_cache_file(), (
            "precondition: the sanitizer must still collapse this id to empty"
        )
        cache = context_cache_file()
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text("mcp/MCP_Serena.md", encoding="utf-8")

        result = CliRunner().invoke(main, ["context", "reset", "--session", "///"])

        assert result.exit_code == 0, result.output
        assert not cache.exists()
        assert result.output.count(f"cache:   {cache}") == 1
        assert "reset 1 cache file(s)" in result.output

    def test_a_distinct_session_still_lists_the_project_only_fallback(
        self, project: Path
    ):
        """Control: the de-duplication must collapse only genuine duplicates."""
        result = CliRunner().invoke(main, ["context", "reset", "--session", "abc"])

        assert result.exit_code == 0, result.output
        assert f"cache:   {context_cache_file('abc')}" in result.output
        assert f"cache:   {context_cache_file()}" in result.output


# Neither script is runnable as `python <path>/context_loader.py`: both import
# `superclaude.*`, which only the installing interpreter resolves (gotcha
# `script-needs-console-entry`). The README may name the scripts all it likes —
# it must never hand a reader a python invocation OF one. `uv run python` is the
# legitimate dev-checkout spelling and is exempt.
#
# The unit is a flattened sentence, not a line, and the match is ADJACENCY over
# `python <token ending in the script name>` rather than co-occurrence anywhere
# on the line. Both corrections are measured against the per-line predicate this
# replaces (`"python" in line and "uv run" not in line`), which failed in both
# directions and, on today's README, could not fire at all: zero lines carry a
# script name and the token `python` together, so it was vacuous-but-passing.
# Sharing `prose_units` with the guard in test_cli_entrypoints.py rather than
# re-deriving the unit here is deliberate — one definition site is what this
# whole class of drift was missing (tests/unit/prose_guard.py).
# Adjacency tolerates a versioned interpreter and interpreter flags between
# `python` and the path — `python3.13 -u .../context_loader.py` is the same bug.
# The intervening tokens are restricted to flags (`-...`) on purpose: allowing
# any token would match prose like "the python implementation of
# context_loader.py", which is not a prescription.
_BARE_SCRIPT_INVOCATION = re.compile(
    r"(?<!uv run )python3?(?:\.\d+)*\s+(?:-\S+\s+)*\S*(?:context_loader|context_reset)\.py"
)


def _bare_script_prescriptions(text: str) -> list[str]:
    """Sentences handing the reader a bare `python <path>/context_{loader,reset}.py`."""
    return [unit for unit in prose_units(text) if _BARE_SCRIPT_INVOCATION.search(unit)]


class TestScriptsReadmeDocumentsTheConsoleEntries:
    """Both scripts import superclaude.* — documenting a file path is the bug."""

    def _readme(self) -> str:
        return (CONTENT_ROOT / "scripts" / "README.md").read_text(encoding="utf-8")

    def test_both_subcommands_are_named(self):
        text = self._readme()

        assert "superclaude context explain" in text
        assert "superclaude context reset" in text

    def test_no_bare_python_invocation_is_prescribed_for_either_script(self):
        text = self._readme()

        offenders = _bare_script_prescriptions(text)
        assert offenders == [], offenders


# The sweep above passes just as happily on a predicate that matches nothing —
# which is what the per-line form did on this README. These pin what the
# predicate must catch and what it must leave alone. Four of the six flip against
# the per-line form, all toward the correct answer: two prescriptions it
# laundered are now caught, two false alarms it raised are now clear. The other
# two are shared HIT/MISS anchors, so the set cannot pass against both forms.
@pytest.mark.parametrize(
    ("passage", "is_prescription"),
    [
        ("Manual: `python3 ~/.claude/superclaude/scripts/context_loader.py`.", True),
        (
            "Dry run: `python3 ~/.claude/superclaude/scripts/context_reset.py`"
            " (the suite drives it with uv run pytest).",
            True,
        ),
        (
            "Run it with python3\n~/.claude/superclaude/scripts/context_loader.py"
            " directly.",
            True,
        ),
        (
            "Inside a dev checkout `uv run\npython scripts/context_reset.py`"
            " is equivalent.",
            False,
        ),
        ("The python implementation of context_loader.py lives here.", False),
        (
            '| `context_loader.py` | Dry run: `superclaude context explain "<p>"` |',
            False,
        ),
        (
            "Manual: `python3.13 -u ~/.claude/superclaude/scripts/context_loader.py`.",
            True,
        ),
    ],
    ids=[
        "bare-script-prescription",
        "bare-prescription-beside-an-unrelated-uv-run",
        "bare-prescription-wrapped-mid-command",
        "uv-run-dev-form-wrapped-mid-command",
        "prose-naming-the-script-beside-the-word-python",
        "console-subcommand",
        "versioned-interpreter-with-a-flag",
    ],
)
def test_bare_script_prescription_discriminates(passage, is_prescription):
    assert bool(_bare_script_prescriptions(passage)) is is_prescription
