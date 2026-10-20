"""Print `--task <id>` arguments for the canary probes that invoke a /sc command
changed since the last `v*` tag (or since BASE given as the first argument).

`make canary-commands` feeds the output to `run_eval.py --canary`; `make release`
asks for that run (or CANARY_OK=1) when a command body changed. A probe invokes a
command when its prompt names `/sc:<name>` or its `covers` list holds `<name>`.
Prints nothing when no probe matches.
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


def changed_commands(base: str) -> set[str]:
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{base}..HEAD", "--", COMMANDS],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    names = {Path(p).stem for p in out if p.endswith(".md")}
    names.discard("README")
    return names


def probes_for(commands: set[str], tasks: list[dict]) -> list[str]:
    """Canary task ids whose prompt invokes one of `commands`, or whose `covers`
    list names one (a probe that runs a chain of commands), in tasks.yaml order."""
    pattern = re.compile(r"/sc:([a-z][a-z-]*)")
    hits = []
    for task in tasks:
        if not task.get("canary"):
            continue
        named = set(pattern.findall(task.get("prompt", ""))) | set(
            task.get("covers", [])
        )
        if named & commands:
            hits.append(task["id"])
    return hits


def main(argv: list[str]) -> int:
    base = argv[1] if len(argv) > 1 else ""
    if not base:
        base = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0", "--match", "v*"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    tasks = yaml.safe_load((EVALS_DIR / "tasks.yaml").read_text(encoding="utf-8"))[
        "tasks"
    ]
    ids = probes_for(changed_commands(base), tasks)
    print(" ".join(f"--task {i}" for i in ids))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
