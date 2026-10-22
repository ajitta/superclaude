"""Eval harness over the arms in ARMS (roadmap Phase 1-1) + model-release canary (Phase 1-2).

Runs each task from tasks.yaml in an isolated temp workspace OUTSIDE the repo
(probe-observer-effect: repo context contaminates baselines), once per arm:

  vanilla          bare Claude Code, no SC content
  sc-full          full project-scope install
  sc-core-lite     full install, RULES.md swapped for arms/RULES_KERNEL.md
  sc-candidate     full install, RULES.md swapped for arms/RULES_CANDIDATE.md
                   (the shipped kernel plus one rule under trial, or minus one
                   shipped rule for an ablation; the only difference from
                   sc-full, so sc-full vs sc-candidate measures that rule alone
                   under identical hooks)
  sc-command-only  full install, always-loaded core import stripped

Arm isolation: CLAUDE_CONFIG_DIR points at an empty per-arm dir (keeps the
host machine's real ~/.claude out of every arm), `--setting-sources
project,local` keeps the claude.ai account's synced plugins and skills out of
it, and ENABLE_CLAUDEAI_MCP_SERVERS=false drops the account's connectors; SC
content is delivered via `superclaude install --scope project` into the
workspace's ./.claude/.

Usage:
  uv run python evals/run_eval.py --dry-run              # build+validate, no API calls
  uv run python evals/run_eval.py                        # all arms, all tasks
  uv run python evals/run_eval.py --canary               # canary suite, sc-full arm
  uv run python evals/run_eval.py --arms vanilla,sc-full --task bugfix-scope-creep

Exit codes: 0 every check passed | 1 a soft metric failed | 2 a hard gate failed.
A check marked `gate: true` in tasks.yaml asserts an invariant (a secret stayed
unread, a frozen file stayed unedited, a destructive command never ran). Gate
failures are reported separately and are not offset by soft-metric averages.

Reuse notes: invokes `claude -p ... --output-format json` directly;
auto_improve.eval_runner.run_eval was
evaluated and not imported — its shell→single-jmespath-metric contract doesn't
cover stream-json transcripts or multi-check scoring.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from superclaude.cli.install_settings import remove_claude_md_import
from superclaude.utils import detect_refusal

EVALS_DIR = Path(__file__).resolve().parent
KERNEL_FILE = EVALS_DIR / "arms" / "RULES_KERNEL.md"
CANDIDATE_FILE = EVALS_DIR / "arms" / "RULES_CANDIDATE.md"
IMPORT_LINE = "@.claude/superclaude/CLAUDE_SC.md"
ARMS = (
    "vanilla",
    "sc-full",
    "sc-core-lite",
    "sc-candidate",
    "sc-command-only",
)
# `claude -p --permission-mode` values; None leaves the flag off (CLI default).
PERMISSION_MODES = (  # `claude --help` 2.1.292; omit the flag for the CLI default
    "acceptEdits",
    "auto",
    "bypassPermissions",
    "dontAsk",
    "manual",
    "plan",
)
DEFAULT_TASK_TIMEOUT = 600

# Harness runs via `uv run` (repo venv, has pytest); the workspace PATH python
# is whatever the host resolves and may lack it. Checks and setup steps pin
# this interpreter, and the model subprocess gets its dir prepended to PATH.
PY_BIN = sys.executable

# Runtime artifacts that are neither model edits nor fixture content — SC's
# loop_guard writes state into the project .claude/, memory-bearing subagents
# write .claude/agent-memory*/, and any python execution drops __pycache__. Committed in the baseline so git_diff checks stay clean.
WS_GITIGNORE = (
    "__pycache__/\n*.pyc\n.claude/.superclaude_hooks/\n"
    ".claude/agent-memory/\n.claude/agent-memory-local/\n"
)


@dataclass
class CheckResult:
    tag: str
    type: str
    passed: bool
    detail: str = ""
    gate: bool = False


@dataclass
class TaskResult:
    arm: str
    task_id: str
    checks: list[CheckResult] = field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    num_turns: int = 0
    duration_s: float = 0.0
    permission_denials: int = 0
    sc_activations: int = 0
    # Skill names of the Skill tool calls that ran (non-error tool_result), in
    # order — what skill_called / skill_not_called match. A refused call is
    # left out; sc_activations still counts attempts. A slash command typed at
    # the start of the prompt is expanded, not called, so it never appears.
    skills_called: list[str] = field(default_factory=list)
    error: str = ""
    # stop_details.category when the model refused the turn ("" otherwise).
    # A refusal is also recorded in `error`, so ok/gates_ok stay false.
    refusal_category: str = ""
    # The --permission-mode value the session ran under ("" = flag omitted),
    # so two results.json files from different modes can be told apart.
    permission_mode: str = ""

    @property
    def ok(self) -> bool:
        return not self.error and all(c.passed for c in self.checks)

    @property
    def gates_ok(self) -> bool:
        return not self.error and all(c.passed for c in self.checks if c.gate)


def _run(
    cmd: list[str], cwd: Path, timeout: int = 120, env: dict | None = None
) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
        env=env,
        encoding="utf-8",
        errors="replace",
    )


def _which(name: str) -> str:
    path = shutil.which(name)
    if not path:
        sys.exit(f"error: `{name}` not found on PATH")
    return path


def _pin_python(cmd: list[str]) -> list[str]:
    return [PY_BIN if part == "python" else part for part in cmd]


def _credentials_file() -> Path | None:
    source = Path(os.getenv("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
    creds = source / ".credentials.json"
    return creds if creds.exists() else None


# ── arm construction ─────────────────────────────────────────────────────────


# Environment that stops pytest writing tests/__pycache__/*-pytest-*.pyc:
# no bytecode, bytecode under another root, .pyo names under -O, or
# operator pytest options such as --assert=plain.
BYTECODE_ENV = (
    "PYTHONDONTWRITEBYTECODE",
    "PYTHONPYCACHEPREFIX",
    "PYTHONOPTIMIZE",
    "PYTEST_ADDOPTS",
)

# A fixture is copied without the bytecode and caches a local test run may
# have left in it, so a check that reads what a run writes (pytest's
# assertion-rewrite cache) sees only what the task's own session wrote.
FIXTURE_IGNORE = shutil.ignore_patterns("__pycache__", ".pytest_cache")


def build_workspace(arm: str, task: dict, runs_dir: Path, superclaude_bin: str) -> Path:
    """Copy fixture, apply arm content, run task setup. Order matters: arm
    content lands BEFORE the task's baseline git commit so .claude/ noise
    never pollutes git_diff checks."""
    ws = runs_dir / arm / task["id"]
    shutil.copytree(EVALS_DIR / task["fixture"], ws, ignore=FIXTURE_IGNORE)
    gitignore = ws / ".gitignore"
    existing = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    gitignore.write_text(existing + WS_GITIGNORE, encoding="utf-8")

    if arm != "vanilla":
        proc = _run(
            [superclaude_bin, "install", "--force", "--scope", "project"],
            cwd=ws,
            timeout=180,
        )
        marker = ws / ".claude" / "superclaude" / "core" / "RULES.md"
        # Post core-lite split, sc-full fidelity requires the on-demand rule
        # modules too — a kernel without modules is the sc-core-lite arm.
        module_marker = (
            ws / ".claude" / "superclaude" / "core" / "rules" / "RULES_QUALITY.md"
        )
        if proc.returncode != 0 or not marker.exists() or not module_marker.exists():
            raise RuntimeError(
                f"project-scope install failed in {ws}: rc={proc.returncode}\n{proc.stderr[-800:]}"
            )
        if arm == "sc-core-lite":
            marker.write_text(KERNEL_FILE.read_text(encoding="utf-8"), encoding="utf-8")
        elif arm == "sc-candidate":
            marker.write_text(
                CANDIDATE_FILE.read_text(encoding="utf-8"), encoding="utf-8"
            )
        _set_core_import(ws, enabled=arm != "sc-command-only")

    for step in task.get("setup", []):
        proc = _run(_pin_python(step), cwd=ws)
        if proc.returncode != 0:
            raise RuntimeError(
                f"setup step {step} failed in {ws}: {proc.stderr[-400:]}"
            )
    return ws


def _set_core_import(ws: Path, enabled: bool) -> None:
    """Force the always-loaded core import line present (sc-full/core-lite)
    or absent (sc-command-only) in the workspace CLAUDE.md, regardless of
    what the installer did. The project install also writes its own import
    into `.claude/CLAUDE.md`; sc-command-only removes that one through the
    installer's own uninstall path, or the arm loads the full core."""
    if not enabled:
        ok, msg = remove_claude_md_import(ws / ".claude", scope="project")
        if not ok:
            raise RuntimeError(f"core import removal failed in {ws}: {msg}")
    claude_md = ws / "CLAUDE.md"
    lines = (
        claude_md.read_text(encoding="utf-8").splitlines() if claude_md.exists() else []
    )
    lines = [ln for ln in lines if IMPORT_LINE not in ln]
    if enabled:
        lines += ["", "# superclaude", IMPORT_LINE]
    text = "\n".join(lines).strip()
    if text:
        claude_md.write_text(text + "\n", encoding="utf-8")
    elif claude_md.exists():
        claude_md.unlink()


# ── claude invocation ────────────────────────────────────────────────────────


def run_task(
    arm: str,
    task: dict,
    ws: Path,
    config_dir: Path,
    log_dir: Path,
    claude_bin: str,
    model: str,
    defaults: dict,
    effort: str | None = None,
    permission_mode: str | None = None,
) -> TaskResult:
    res = TaskResult(arm=arm, task_id=task["id"], permission_mode=permission_mode or "")
    tools = task.get("allowed_tools", defaults.get("allowed_tools", []))
    cmd = [
        claude_bin,
        "-p",
        "--output-format",
        "stream-json",
        "--verbose",
        "--max-turns",
        str(task.get("max_turns", defaults.get("max_turns", 12))),
        "--model",
        model,
        # Session effort (low|medium|high|xhigh|max); omitted = model default.
        # Lets a probe measure an xhigh-only behavior without changing the
        # canary's default-effort baseline.
        *(["--effort", effort] if effort else []),
        "--allowedTools",
        " ".join(tools),
        # Permission mode; omitted = Claude Code default. `auto` injects an
        # "execute immediately" reminder that can override prose stop rules,
        # so the gated probes are rerun under it to see which survive.
        *(["--permission-mode", permission_mode] if permission_mode else []),
        # User settings stay out: with them on, a claude.ai login syncs the
        # account's plugins and skills into the empty config dir during the
        # first session, and every later session of the arm loads them.
        # The sc-* arms' hooks and permissions are project settings.
        "--setting-sources",
        "project,local",
        # `--` ends option parsing: prompts that legitimately start with an SC
        # flag (e.g. "--introspect ...") were otherwise parsed as CLI options
        # and the session died before any turn ran.
        "--",
        task["prompt"].strip(),
    ]
    env = dict(os.environ)
    env["CLAUDE_CONFIG_DIR"] = str(config_dir)
    env["PATH"] = str(Path(PY_BIN).parent) + os.pathsep + env.get("PATH", "")
    # The sc-* install carries a Stop hook that asks for one `INSIGHT:` line
    # after the first code change; headless, that reply becomes the result
    # event's text and every output_regex check reads it instead of the
    # report (vanilla has no hook). Plumbing, not behavior under measurement —
    # off for every arm through the hook's own knob.
    env["SUPERCLAUDE_INSIGHT_PROMPT"] = "0"
    # The account's claude.ai MCP connectors load in every session whatever
    # the config dir holds; same for every arm, still not the arm's content.
    env["ENABLE_CLAUDEAI_MCP_SERVERS"] = "false"
    # Probes read pytest's bytecode cache to see that tests ran; an operator
    # shell that turns bytecode off, moves it or renames it would fail them
    # every run.
    for name in BYTECODE_ENV:
        env.pop(name, None)

    started = time.monotonic()
    try:
        proc = _run(
            cmd, cwd=ws, timeout=task.get("timeout", DEFAULT_TASK_TIMEOUT), env=env
        )
    except subprocess.TimeoutExpired:
        res.error = "task timeout"
        return res
    res.duration_s = round(time.monotonic() - started, 1)

    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"{task['id']}.stream.jsonl").write_text(proc.stdout, encoding="utf-8")
    result_text, bash_inputs, subtype = _parse_stream(proc.stdout, res)
    if proc.returncode != 0:
        # A non-zero exit with a result event is a session that ran and ended
        # on a terminal condition such as `error_max_turns` (exit 1). The
        # workspace still holds whatever the model produced and the result
        # event still carries usage, so the checks and the cost stay in the
        # record; the error keeps ok/gates_ok false so the run never reads as
        # a clean pass. Without a result event nothing ran: report and stop.
        if subtype is None:
            res.error = f"claude rc={proc.returncode}: {proc.stderr[-400:]}"
            return res
        if not res.refusal_category:
            res.error = f"claude rc={proc.returncode}: {subtype}"
    _run_checks(task, ws, result_text, bash_inputs, res)
    return res


def _mark_refusal(res: TaskResult, category: str) -> None:
    # Never downgrade: the assistant event names the category, the later
    # result event only knows "unknown".
    if category == "unknown" and res.refusal_category:
        return
    res.refusal_category = category
    res.error = f"refusal (category={category})"


def _parse_stream(stream: str, res: TaskResult) -> tuple[str, str, str | None]:
    """Extract final result text, usage metrics, and Bash tool inputs from a
    stream-json transcript. The third value is the result event's `subtype`
    (None when the stream has no result event, i.e. nothing ran)."""
    result_text = ""
    subtype: str | None = None
    bash_inputs: list[str] = []
    # Skill tool_use id -> skill name, until its tool_result arrives. Claude
    # Code answers a call it refuses (disable-model-invocation, unknown skill)
    # with an error result, so only a non-error result counts as a run.
    pending_skills: dict[str, str] = {}
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        etype = event.get("type")
        if etype == "result":
            result_text = event.get("result") or ""
            subtype = str(event.get("subtype") or "result")
            category = detect_refusal(event)
            if category is not None:
                _mark_refusal(res, category)
            # A refusal is the more specific signal; keep it over the generic
            # error text when both are present on the same run.
            if event.get("is_error") and not res.refusal_category:
                res.error = f"claude error result: {result_text[:200]}"
            usage = event.get("usage") or {}
            res.tokens_in = usage.get("input_tokens", 0) + usage.get(
                "cache_read_input_tokens", 0
            )
            res.tokens_out = usage.get("output_tokens", 0)
            res.cost_usd = event.get("total_cost_usd", 0.0)
            res.num_turns = event.get("num_turns", 0)
            res.permission_denials = len(event.get("permission_denials") or [])
        elif etype == "assistant":
            message = event.get("message") or {}
            category = detect_refusal(message)
            if category is not None:
                _mark_refusal(res, category)
            for block in message.get("content", []):
                if block.get("type") != "tool_use":
                    continue
                name = block.get("name", "")
                tool_input = block.get("input") or {}
                # Both shell tools count: Claude Code on Windows offers
                # PowerShell next to Bash, and a destructive command through
                # either must trip the transcript gates.
                if name in ("Bash", "PowerShell"):
                    bash_inputs.append(tool_input.get("command", ""))
                if name == "Skill":
                    skill = str(tool_input.get("skill", ""))
                    pending_skills[block.get("id", "")] = skill
                    if skill.startswith("sc:"):
                        res.sc_activations += 1
        elif etype == "user":
            content = (event.get("message") or {}).get("content")
            for block in content if isinstance(content, list) else []:
                if block.get("type") != "tool_result":
                    continue
                skill = pending_skills.pop(block.get("tool_use_id", ""), None)
                if skill is not None and not block.get("is_error"):
                    res.skills_called.append(skill)
    return result_text, "\n".join(bash_inputs), subtype


# ── checks ───────────────────────────────────────────────────────────────────


def _run_checks(
    task: dict, ws: Path, result_text: str, bash_inputs: str, res: TaskResult
) -> None:
    for check in task.get("checks", []):
        ctype, tag = check["type"], check.get("tag", "untagged")
        passed, detail = _check_one(
            check, ctype, ws, result_text, bash_inputs, res.skills_called
        )
        res.checks.append(
            CheckResult(
                tag=tag,
                type=ctype,
                passed=passed,
                detail=detail,
                gate=bool(check.get("gate", False)),
            )
        )


def _under_claude_home(path: Path) -> bool:
    """True when *path* sits inside the user's ~/.claude directory."""
    claude_home = (Path.home() / ".claude").resolve()
    resolved = path.resolve()
    return resolved == claude_home or claude_home in resolved.parents


def _stashed_files(ws: Path) -> set[str]:
    """Paths (posix, relative) held in any git stash entry, untracked included.

    A stash is the reversible path a model takes when asked to wipe a working
    tree, so a file that moved into one has been preserved, not destroyed.
    """
    listing = _run(["git", "stash", "list", "--format=%gd"], cwd=ws)
    names: set[str] = set()
    for ref in listing.stdout.split():
        show = _run(
            ["git", "stash", "show", "--include-untracked", "--name-only", ref],
            cwd=ws,
        )
        names |= {line.strip() for line in show.stdout.splitlines() if line.strip()}
    return names


def _check_one(
    check: dict,
    ctype: str,
    ws: Path,
    result_text: str,
    bash_inputs: str,
    skills_called: list[str] | None = None,
) -> tuple[bool, str]:
    if ctype == "cmd_ok":
        proc = _run(_pin_python(check["cmd"]), cwd=ws)
        return proc.returncode == 0, (proc.stdout + proc.stderr)[-200:].strip()
    if ctype == "git_diff_max_files":
        changed = _git_changed(ws)
        return len(changed) <= check["value"], f"changed: {sorted(changed)}"
    if ctype == "git_diff_includes":
        return check["path"] in _git_changed(ws), ""
    if ctype == "git_diff_excludes":
        return check["path"] not in _git_changed(ws), ""
    if ctype == "file_exists_glob":
        # `pattern` may be a list: any match passes. Used where a convention
        # allows more than one correct location for the same deliverable.
        patterns = check["pattern"]
        if isinstance(patterns, str):
            patterns = [patterns]
        hits = [p for p in patterns if any(ws.glob(p))]
        return bool(hits), f"matched: {hits}" if hits else "no match"
    if ctype == "file_preserved_glob":
        # Present in the working tree, or carried into a git stash: both mean
        # the file survived. Only a delete without a recovery path fails.
        if any(ws.glob(check["pattern"])):
            return True, "in working tree"
        stashed = {
            n for n in _stashed_files(ws) if fnmatch.fnmatch(n, check["pattern"])
        }
        return bool(stashed), f"stashed: {sorted(stashed)}" if stashed else "gone"
    if ctype == "file_absent_glob":
        matches = {
            p.relative_to(ws).as_posix()
            for p in ws.glob(check["pattern"])
            if p.is_file()
        }
        if check.get("exclude_baseline"):
            matches -= _git_baseline(ws)
        return not matches, f"unexpected: {sorted(matches)}"
    if ctype == "output_regex":
        return bool(re.search(check["pattern"], result_text)), ""
    if ctype == "output_not_regex":
        return not re.search(check["pattern"], result_text), ""
    if ctype == "transcript_regex":
        return bool(re.search(check["pattern"], bash_inputs)), ""
    if ctype == "transcript_not_regex":
        m = re.search(check["pattern"], bash_inputs)
        return m is None, m.group(0) if m else ""
    if ctype == "skill_called":
        hits = [s for s in skills_called or [] if re.search(check["pattern"], s)]
        ok = bool(hits) and len(hits) <= check.get("max", len(hits))
        return ok, f"called={skills_called or []}"
    if ctype == "skill_not_called":
        hits = [s for s in skills_called or [] if re.search(check["pattern"], s)]
        return not hits, f"called={skills_called or []}"
    if ctype == "citation_lines":
        return _check_citations(check, result_text)
    raise ValueError(f"unknown check type: {ctype}")


def _check_citations(check: dict, result_text: str) -> tuple[bool, str]:
    cited = {
        int(m) for m in re.findall(rf"{re.escape(check['file'])}:(\d+)", result_text)
    }
    tol = check.get("tolerance", 0)
    hit = {exp for exp in check["expected"] if any(abs(c - exp) <= tol for c in cited)}
    accuracy = len(hit) / len(check["expected"])
    return accuracy >= check.get(
        "min_accuracy", 1.0
    ), f"cited={sorted(cited)} accuracy={accuracy:.2f}"


def _git_changed(ws: Path) -> set[str]:
    proc = _run(["git", "status", "--porcelain"], cwd=ws)
    return {
        line[3:].split(" -> ")[-1].strip().strip('"')
        for line in proc.stdout.splitlines()
        if line.strip()
    } - FRAMEWORK_STATE_FILES


# Files the installed framework's own hooks write into the workspace during a
# run (insight_writer appends on PostToolUse). They are arm plumbing, not model
# behavior, so diff-size checks must not count them: every sc-full task that
# writes a file otherwise fails `git_diff_max_files` by one.
FRAMEWORK_STATE_FILES = frozenset(
    {".claude/insights.jsonl", ".claude/insights.pending.jsonl"}
)


def _git_baseline(ws: Path) -> set[str]:
    proc = _run(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=ws)
    return set(proc.stdout.splitlines())


# ── reporting ────────────────────────────────────────────────────────────────


def write_report(
    results: list[TaskResult], runs_dir: Path, permission_mode: str | None = None
) -> str:
    payload = [
        {**vars(r), "checks": [vars(c) for c in r.checks], "ok": r.ok} for r in results
    ]
    (runs_dir / "results.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    arms = sorted({r.arm for r in results})
    tasks = sorted({r.task_id for r in results})
    mode = f"`{permission_mode}`" if permission_mode else "default (flag omitted)"
    lines = [
        "# Eval report",
        "",
        f"Permission mode: {mode}",
        "",
        "| task | " + " | ".join(arms) + " |",
        "|---|" + "---|" * len(arms),
    ]
    for tid in tasks:
        row = [tid]
        for arm in arms:
            r = next((x for x in results if x.arm == arm and x.task_id == tid), None)
            if r is None:
                row.append("—")
            elif r.refusal_category:
                row.append("REFUSED")
            elif r.error:
                row.append("ERR")
            else:
                row.append(f"{sum(c.passed for c in r.checks)}/{len(r.checks)}")
        lines.append("| " + " | ".join(row) + " |")

    failed_gates = [
        (r.arm, r.task_id, c)
        for r in results
        for c in r.checks
        if c.gate and not c.passed
    ]
    lines += ["", "## Hard gates", ""]
    if failed_gates:
        lines += ["| arm | task | check | detail |", "|---|---|---|---|"]
        lines += [
            f"| {arm} | {tid} | {c.type} ({c.tag}) | {c.detail or '—'} |"
            for arm, tid, c in failed_gates
        ]
        lines += [
            "",
            "A failed hard gate is an invariant violation. Soft-metric averages "
            "do not offset it.",
        ]
    else:
        total = sum(1 for r in results for c in r.checks if c.gate)
        lines.append(f"All {total} hard-gate checks passed.")

    refusals = [r for r in results if r.refusal_category]
    lines += ["", "## Refusals", ""]
    if refusals:
        lines += ["| arm | task | category |", "|---|---|---|"]
        lines += [f"| {r.arm} | {r.task_id} | {r.refusal_category} |" for r in refusals]
        lines += [
            "",
            "A refusal is the model declining the turn, not a harness error. On a "
            "model-release canary it names the prose rule or task wording that "
            "trips the new model's classifiers.",
        ]
    else:
        lines.append("No refusals.")

    lines += ["", "## Metric-tag pass rates (per arm)", ""]
    tags = sorted({c.tag for r in results for c in r.checks})
    lines += ["| tag | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    for tag in tags:
        row = [tag]
        for arm in arms:
            hits = [
                c.passed
                for r in results
                if r.arm == arm
                for c in r.checks
                if c.tag == tag
            ]
            row.append(f"{sum(hits)}/{len(hits)}" if hits else "—")
        lines.append("| " + " | ".join(row) + " |")

    lines += [
        "",
        "## Cost / footprint",
        "",
        "| arm | tokens_in | tokens_out | cost_usd | denials | sc_activations |",
        "|---|---|---|---|---|---|",
    ]
    for arm in arms:
        rs = [r for r in results if r.arm == arm]
        lines.append(
            f"| {arm} | {sum(r.tokens_in for r in rs)} | {sum(r.tokens_out for r in rs)} "
            f"| {sum(r.cost_usd for r in rs):.4f} | {sum(r.permission_denials for r in rs)} "
            f"| {sum(r.sc_activations for r in rs)} |"
        )
    report = "\n".join(lines) + "\n"
    (runs_dir / "report.md").write_text(report, encoding="utf-8")
    return report


# ── main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    # python -OO (PYTHONOPTIMIZE=2) strips the module docstring.
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0] if __doc__ else None
    )
    ap.add_argument(
        "--arms", default=",".join(ARMS), help=f"comma-separated subset of {ARMS}"
    )
    ap.add_argument(
        "--task", action="append", default=None, help="task id filter (repeatable)"
    )
    ap.add_argument(
        "--canary",
        action="store_true",
        help="canary suite: canary-flagged tasks, sc-full arm only (unless --arms given)",
    )
    ap.add_argument("--model", default="sonnet")
    ap.add_argument(
        "--effort",
        default=None,
        help="session effort passed to claude -p (low|medium|high|xhigh|max); "
        "omit for the model default",
    )
    ap.add_argument(
        "--permission-mode",
        default=None,
        choices=PERMISSION_MODES,
        help="permission mode passed to claude -p; omit to leave the flag off",
    )
    ap.add_argument(
        "--runs-dir",
        default=None,
        help="output dir (default: <system temp>/superclaude-evals/<timestamp>)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="build arms + workspaces + setups + validate config; no API calls",
    )
    args = ap.parse_args()

    spec = yaml.safe_load((EVALS_DIR / "tasks.yaml").read_text(encoding="utf-8"))
    defaults = spec.get("defaults", {})
    tasks = spec["tasks"]
    if args.canary:
        tasks = [t for t in tasks if t.get("canary")]
        if args.arms == ",".join(ARMS):
            args.arms = "sc-full"
    else:
        tasks = [t for t in tasks if not t.get("canary_only")]
    if args.task:
        tasks = [t for t in tasks if t["id"] in set(args.task)]
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    unknown = [a for a in arms if a not in ARMS]
    if unknown or not tasks:
        sys.exit(f"error: unknown arms {unknown} or no tasks selected")

    runs_dir = (
        Path(args.runs_dir)
        if args.runs_dir
        else (
            Path(tempfile.gettempdir())
            / "superclaude-evals"
            / time.strftime("%Y%m%d-%H%M%S")
        )
    )
    if (
        EVALS_DIR.resolve() in runs_dir.resolve().parents
        or runs_dir.resolve() == EVALS_DIR.resolve()
    ):
        sys.exit("error: runs dir must be outside the repo (probe-observer-effect)")
    if _under_claude_home(runs_dir):
        # Claude Code treats everything under ~/.claude as sensitive and denies
        # Edit/Write there in headless mode, so every task that edits a file
        # fails on permissions rather than on behavior. A Claude Code session
        # sets TEMP to ~/.claude/tmp, which is how the default lands here.
        sys.exit(
            f"error: runs dir {runs_dir} is under ~/.claude, where Claude Code "
            "denies file edits as sensitive; pass --runs-dir outside it "
            "(e.g. C:/tmp/superclaude-evals or /tmp/superclaude-evals)"
        )
    runs_dir.mkdir(parents=True, exist_ok=True)

    claude_bin = _which("claude")
    superclaude_bin = _which("superclaude")
    env_auth = bool(
        os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_CODE_OAUTH_TOKEN")
    )
    creds = (
        None if env_auth else _credentials_file()
    )  # env auth flows through on its own
    if not env_auth and creds is None and not args.dry_run:
        sys.exit(
            "error: no auth found — need ~/.claude/.credentials.json (run `claude` once "
            "to log in) or ANTHROPIC_API_KEY/CLAUDE_CODE_OAUTH_TOKEN in the environment"
        )
    print(f"runs dir: {runs_dir}\narms: {arms}\ntasks: {[t['id'] for t in tasks]}")

    results: list[TaskResult] = []
    # The per-arm credential copies are live OAuth tokens; they must not outlive
    # the run (the runs dir defaults to the system temp dir).
    try:
        for arm in arms:
            config_dir = runs_dir / "config" / arm
            config_dir.mkdir(parents=True, exist_ok=True)
            if creds is not None:
                # Auth is CLAUDE_CONFIG_DIR-scoped; credentials only — settings.json
                # or CLAUDE.md from the real config dir would contaminate the arm.
                shutil.copy2(creds, config_dir / creds.name)
            for task in tasks:
                label = f"[{arm}/{task['id']}]"
                try:
                    ws = build_workspace(arm, task, runs_dir, superclaude_bin)
                except (RuntimeError, subprocess.TimeoutExpired) as exc:
                    print(f"{label} BUILD FAIL: {exc}")
                    results.append(
                        TaskResult(
                            arm=arm,
                            task_id=task["id"],
                            error=f"build: {exc}",
                            permission_mode=args.permission_mode or "",
                        )
                    )
                    continue
                if args.dry_run:
                    print(f"{label} build ok: {ws}")
                    continue
                res = run_task(
                    arm,
                    task,
                    ws,
                    config_dir,
                    runs_dir / arm / "logs",
                    claude_bin,
                    args.model,
                    defaults,
                    args.effort,
                    args.permission_mode,
                )
                results.append(res)
                status = "ok" if res.ok else (res.error or "checks failed")
                print(
                    f"{label} {status} ({res.duration_s}s, {res.tokens_out} out-tokens)"
                )
    finally:
        shutil.rmtree(runs_dir / "config", ignore_errors=True)

    if args.dry_run:
        print("dry run complete — workspaces built, no API calls made")
        return 0
    print("\n" + write_report(results, runs_dir, args.permission_mode))
    if any(not r.gates_ok for r in results):
        return 2
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
