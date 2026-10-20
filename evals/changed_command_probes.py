"""Print `--task <id>` arguments for the canary probes that exercise a /sc command
changed since the last `v*` tag (or since BASE given as the first argument).

`make canary-commands` feeds the output to `run_eval.py --canary`; `make release`
asks for that run (or CANARY_OK=1) when a command body changed. A probe exercises
a command when its prompt names `/sc:<name>`, one of its `skill_called` checks
expects `sc:<name>`, or its `covers:` list holds `<name>`. Prints nothing when no
probe matches; exits 2 when the base cannot be resolved (no reachable `v*` tag).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

EVALS_DIR = Path(__file__).resolve().parent
ROOT = EVALS_DIR.parent
COMMANDS = "src/superclaude/commands"
_PROMPT_NAME = re.compile(r"/sc:([a-z][a-z-]*)")
_SKILL_NAME = re.compile(r"sc:([a-z][a-z-]*)")


def changed_commands(base: str, root: Path = ROOT) -> set[str]:
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{base}..HEAD", "--", COMMANDS],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    names = {Path(p).stem for p in out if p.endswith(".md")}
    names.discard("README")
    return names


def commands_of(task: dict) -> set[str]:
    """Command names a probe exercises: its prompt, skill_called checks, covers."""
    names = set(_PROMPT_NAME.findall(task.get("prompt", "")))
    for check in task.get("checks", []):
        if check.get("type") == "skill_called":
            names.update(_SKILL_NAME.findall(check.get("pattern", "")))
    names.update(task.get("covers", []))
    return names


def probes_for(commands: set[str], tasks: list[dict]) -> list[str]:
    """Canary task ids that exercise one of `commands`, in tasks.yaml order."""
    return [t["id"] for t in tasks if t.get("canary") and commands_of(t) & commands]


def main(argv: list[str], root: Path = ROOT) -> int:
    base = argv[1] if len(argv) > 1 else ""
    try:
        if not base:
            base = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0", "--match", "v*"],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        changed = changed_commands(base, root)
    except subprocess.CalledProcessError:
        reason = base or "no v* tag reachable"
        print(f"no base to diff against ({reason}; git fetch --tags?)", file=sys.stderr)
        return 2
    tasks = yaml.safe_load((EVALS_DIR / "tasks.yaml").read_text(encoding="utf-8"))[
        "tasks"
    ]
    print(" ".join(f"--task {i}" for i in probes_for(changed, tasks)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
