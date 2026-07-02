"""4-arm eval harness (roadmap Phase 1-1) + model-release canary (Phase 1-2).

Runs each task from tasks.yaml in an isolated temp workspace OUTSIDE the repo
(probe-observer-effect: repo context contaminates baselines), once per arm:

  vanilla          bare Claude Code, no SC content
  sc-full          full project-scope install
  sc-core-lite     full install, RULES.md swapped for arms/RULES_KERNEL.md
  sc-command-only  full install, always-loaded core import stripped

Arm isolation: CLAUDE_CONFIG_DIR points at an empty per-arm dir (keeps the
host machine's real ~/.claude out of every arm); SC content is delivered via
`superclaude install --scope project` into the workspace's ./.claude/.

Usage:
  uv run python evals/run_eval.py --dry-run              # build+validate, no API calls
  uv run python evals/run_eval.py                        # all arms, all tasks
  uv run python evals/run_eval.py --canary               # canary suite, sc-full arm
  uv run python evals/run_eval.py --arms vanilla,sc-full --task bugfix-scope-creep

Reuse notes: invocation pattern mirrors tests/integration/test_skill_canary.py
(`claude -p ... --output-format json`); auto_improve.eval_runner.run_eval was
evaluated and not imported — its shell→single-jmespath-metric contract doesn't
cover stream-json transcripts or multi-check scoring.
"""

from __future__ import annotations

import argparse
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

EVALS_DIR = Path(__file__).resolve().parent
KERNEL_FILE = EVALS_DIR / "arms" / "RULES_KERNEL.md"
IMPORT_LINE = "@.claude/superclaude/CLAUDE_SC.md"
ARMS = ("vanilla", "sc-full", "sc-core-lite", "sc-command-only")
DEFAULT_TASK_TIMEOUT = 600


@dataclass
class CheckResult:
    tag: str
    type: str
    passed: bool
    detail: str = ""


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
    error: str = ""

    @property
    def ok(self) -> bool:
        return not self.error and all(c.passed for c in self.checks)


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


def _credentials_file() -> Path | None:
    source = Path(os.getenv("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
    creds = source / ".credentials.json"
    return creds if creds.exists() else None


# ── arm construction ─────────────────────────────────────────────────────────


def build_workspace(arm: str, task: dict, runs_dir: Path, superclaude_bin: str) -> Path:
    """Copy fixture, apply arm content, run task setup. Order matters: arm
    content lands BEFORE the task's baseline git commit so .claude/ noise
    never pollutes git_diff checks."""
    ws = runs_dir / arm / task["id"]
    shutil.copytree(EVALS_DIR / task["fixture"], ws)

    if arm != "vanilla":
        proc = _run(
            [superclaude_bin, "install", "--force", "--scope", "project"],
            cwd=ws,
            timeout=180,
        )
        marker = ws / ".claude" / "superclaude" / "core" / "RULES.md"
        if proc.returncode != 0 or not marker.exists():
            raise RuntimeError(
                f"project-scope install failed in {ws}: rc={proc.returncode}\n{proc.stderr[-800:]}"
            )
        if arm == "sc-core-lite":
            marker.write_text(KERNEL_FILE.read_text(encoding="utf-8"), encoding="utf-8")
        _set_core_import(ws, enabled=arm != "sc-command-only")

    for step in task.get("setup", []):
        proc = _run(list(step), cwd=ws)
        if proc.returncode != 0:
            raise RuntimeError(
                f"setup step {step} failed in {ws}: {proc.stderr[-400:]}"
            )
    return ws


def _set_core_import(ws: Path, enabled: bool) -> None:
    """Force the always-loaded core import line present (sc-full/core-lite)
    or absent (sc-command-only) in the workspace CLAUDE.md, regardless of
    what the installer did."""
    claude_md = ws / "CLAUDE.md"
    lines = (
        claude_md.read_text(encoding="utf-8").splitlines() if claude_md.exists() else []
    )
    lines = [ln for ln in lines if IMPORT_LINE not in ln]
    if enabled:
        lines += ["", "# SuperClaude Framework", IMPORT_LINE]
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
) -> TaskResult:
    res = TaskResult(arm=arm, task_id=task["id"])
    tools = task.get("allowed_tools", defaults.get("allowed_tools", []))
    cmd = [
        claude_bin,
        "-p",
        task["prompt"].strip(),
        "--output-format",
        "stream-json",
        "--verbose",
        "--max-turns",
        str(task.get("max_turns", defaults.get("max_turns", 12))),
        "--model",
        model,
        "--allowedTools",
        " ".join(tools),
    ]
    env = dict(os.environ)
    env["CLAUDE_CONFIG_DIR"] = str(config_dir)

    started = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ws),
            capture_output=True,
            text=True,
            check=False,
            timeout=task.get("timeout", DEFAULT_TASK_TIMEOUT),
            env=env,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        res.error = "task timeout"
        return res
    res.duration_s = round(time.monotonic() - started, 1)

    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"{task['id']}.stream.jsonl").write_text(proc.stdout, encoding="utf-8")
    if proc.returncode != 0:
        res.error = f"claude rc={proc.returncode}: {proc.stderr[-400:]}"
        return res

    result_text, bash_inputs = _parse_stream(proc.stdout, res)
    _run_checks(task, ws, result_text, bash_inputs, res)
    return res


def _parse_stream(stream: str, res: TaskResult) -> tuple[str, str]:
    """Extract final result text, usage metrics, and Bash tool inputs from a
    stream-json transcript."""
    result_text = ""
    bash_inputs: list[str] = []
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        etype = event.get("type")
        if etype == "result":
            result_text = event.get("result") or ""
            if event.get("is_error"):
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
            for block in (event.get("message") or {}).get("content", []):
                if block.get("type") != "tool_use":
                    continue
                name = block.get("name", "")
                tool_input = block.get("input") or {}
                if name == "Bash":
                    bash_inputs.append(tool_input.get("command", ""))
                if name == "Skill" and str(tool_input.get("skill", "")).startswith(
                    "sc:"
                ):
                    res.sc_activations += 1
    return result_text, "\n".join(bash_inputs)


# ── checks ───────────────────────────────────────────────────────────────────


def _run_checks(
    task: dict, ws: Path, result_text: str, bash_inputs: str, res: TaskResult
) -> None:
    for check in task.get("checks", []):
        ctype, tag = check["type"], check.get("tag", "untagged")
        passed, detail = _check_one(check, ctype, ws, result_text, bash_inputs)
        res.checks.append(
            CheckResult(tag=tag, type=ctype, passed=passed, detail=detail)
        )


def _check_one(
    check: dict, ctype: str, ws: Path, result_text: str, bash_inputs: str
) -> tuple[bool, str]:
    if ctype == "cmd_ok":
        proc = _run(list(check["cmd"]), cwd=ws)
        return proc.returncode == 0, proc.stdout[-200:].strip()
    if ctype == "git_diff_max_files":
        changed = _git_changed(ws)
        return len(changed) <= check["value"], f"changed: {sorted(changed)}"
    if ctype == "git_diff_includes":
        return check["path"] in _git_changed(ws), ""
    if ctype == "git_diff_excludes":
        return check["path"] not in _git_changed(ws), ""
    if ctype == "file_exists_glob":
        return any(ws.glob(check["pattern"])), ""
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
    }


def _git_baseline(ws: Path) -> set[str]:
    proc = _run(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=ws)
    return set(proc.stdout.splitlines())


# ── reporting ────────────────────────────────────────────────────────────────


def write_report(results: list[TaskResult], runs_dir: Path) -> str:
    payload = [
        {**vars(r), "checks": [vars(c) for c in r.checks], "ok": r.ok} for r in results
    ]
    (runs_dir / "results.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    arms = sorted({r.arm for r in results})
    tasks = sorted({r.task_id for r in results})
    lines = [
        "# Eval report",
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
            elif r.error:
                row.append("ERR")
            else:
                row.append(f"{sum(c.passed for c in r.checks)}/{len(r.checks)}")
        lines.append("| " + " | ".join(row) + " |")

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
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
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
                    TaskResult(arm=arm, task_id=task["id"], error=f"build: {exc}")
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
            )
            results.append(res)
            status = "ok" if res.ok else (res.error or "checks failed")
            print(f"{label} {status} ({res.duration_s}s, {res.tokens_out} out-tokens)")

    if args.dry_run:
        print("dry run complete — workspaces built, no API calls made")
        return 0
    print("\n" + write_report(results, runs_dir))
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
