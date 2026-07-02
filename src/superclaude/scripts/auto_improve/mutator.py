"""Mutator wrapper — invokes `claude -p` headless CLI inside a worktree.

Tool surface is constrained to Edit/Write/Read (Bash explicitly omitted) to
honour spec R2 v0.1 guard #3: the agent must not run external commands that
could escape the worktree.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

DEFAULT_MODEL = "sonnet"
ALLOWED_TOOLS = "Edit Write Read"
DEFAULT_TIMEOUT_S = 600  # matches CoordinatorConfig.cycle_timeout_seconds default

DEFAULT_PROMPT = """\
You are the mutator agent in a Karpathy-style autoresearch loop. The current
working directory is an isolated git worktree.

Inspect:
  - `git log --oneline -20`
  - `results.tsv`

Then propose ONE specific change to improve the project's metric. Apply it
via Edit/Write tools. Do not run shell commands (Bash is disabled).

Return a one-paragraph rationale describing the change and your hypothesis
about why it should improve the metric. Keep it under 200 words.
"""


@dataclass(frozen=True)
class MutationResult:
    rationale: str
    tokens_used: int
    error: Optional[str] = None


class Mutator:
    """Subprocess wrapper around the `claude` CLI in headless print mode."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        prompt: str = DEFAULT_PROMPT,
        timeout: int = DEFAULT_TIMEOUT_S,
    ):
        self.model = model
        self.prompt = prompt
        self.timeout = timeout

    def _claude_path(self) -> str:
        which = shutil.which("claude")
        return which if which else "claude"

    def mutate(self, worktree_path: Path) -> MutationResult:
        # Prompt goes via stdin: --allowed-tools and --add-dir are variadic
        # (commander.js style), and a trailing positional prompt gets greedily
        # absorbed into one of them. claude CLI accepts prompt via stdin under
        # --print and that path bypasses the parsing ambiguity.
        cmd = [
            self._claude_path(),
            "-p",
            "--output-format",
            "json",
            "--allowed-tools",
            ALLOWED_TOOLS,
            "--model",
            self.model,
            "--permission-mode",
            "bypassPermissions",
            "--add-dir",
            str(worktree_path),
        ]
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(worktree_path),
                capture_output=True,
                text=True,
                timeout=self.timeout,
                input=self.prompt,
            )
        except FileNotFoundError as exc:
            return MutationResult(
                rationale="", tokens_used=0, error=f"claude CLI not found: {exc}"
            )
        except subprocess.TimeoutExpired:
            return MutationResult(
                rationale="",
                tokens_used=0,
                error=f"claude CLI exceeded timeout ({self.timeout}s) — killed",
            )

        if proc.returncode != 0:
            return MutationResult(
                rationale="",
                tokens_used=0,
                error=f"claude exited {proc.returncode}: {proc.stderr[:200]}",
            )

        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            return MutationResult(
                rationale="", tokens_used=0, error=f"claude stdout not JSON: {exc}"
            )

        rationale = (payload.get("result") or "").strip()
        usage = payload.get("usage") or {}
        tokens = int(usage.get("input_tokens", 0)) + int(usage.get("output_tokens", 0))

        if not rationale:
            return MutationResult(
                rationale="",
                tokens_used=tokens,
                error="empty rationale from mutator (R3 violation)",
            )

        return MutationResult(rationale=rationale, tokens_used=tokens)
