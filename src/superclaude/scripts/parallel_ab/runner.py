"""Single-variant runner: wraps ``claude -p`` subprocess + writes observation."""

from __future__ import annotations

import asyncio
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Awaitable, Callable

from .observation import (
    Observation,
    Tokens,
    ToolCall,
    compute_sha256,
    emit,
)
from .spec_loader import RunnerCfg, Scenario, Variant

_AUTH_PATTERNS = re.compile(
    r"authent|credential|api[\s\-]?key|unauthor|login",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SpawnResult:
    stdout: bytes
    stderr: bytes
    returncode: int


@dataclass(frozen=True)
class ParsedResult:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    tool_calls: tuple[ToolCall, ...] = ()
    axes: dict[str, str] = field(default_factory=dict)
    is_error: bool = False


Spawner = Callable[[list[str], int], Awaitable[SpawnResult]]


async def _default_spawn(cmd: list[str], timeout_s: int) -> SpawnResult:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise
    return SpawnResult(
        stdout=stdout or b"",
        stderr=stderr or b"",
        returncode=proc.returncode if proc.returncode is not None else -1,
    )


def _is_slash_command(text: str) -> bool:
    """True when the scenario input is a slash command (needs skills loaded)."""
    return text.lstrip().startswith("/")


def _build_cmd(variant: Variant, scenario: Scenario, cfg: RunnerCfg) -> list[str]:
    base = cfg.cli.split()  # "claude -p" → ["claude", "-p"]
    cmd: list[str] = [
        *base,
        "--model", cfg.model,
        "--output-format", "json",
    ]
    # `--bare` strips skills/plugins; a slash-command input would then resolve
    # to "Unknown command". Suppress --bare for slash inputs regardless of cfg.
    if cfg.bare and not _is_slash_command(scenario.input):
        cmd.append("--bare")
    prompt_parts = [
        s for s in (scenario.input, variant.flag, variant.extra_args) if s
    ]
    cmd.append(" ".join(prompt_parts))
    return cmd


def _looks_like_auth_fail(stderr: bytes) -> bool:
    if not stderr:
        return False
    text = stderr.decode("utf-8", errors="replace")
    return bool(_AUTH_PATTERNS.search(text))


def _parse_output(stdout: bytes) -> ParsedResult:
    text = stdout.decode("utf-8", errors="replace")
    try:
        d = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return ParsedResult(text=text)
    if not isinstance(d, dict):
        return ParsedResult(text=text)
    result_text = str(d.get("result") or d.get("output") or text)
    usage = d.get("usage") or {}
    tools_raw = d.get("tools_used") or []
    tool_calls = tuple(
        ToolCall(name=str(t.get("name", "")), count=int(t.get("count", 0)))
        for t in tools_raw
        if isinstance(t, dict)
    )
    return ParsedResult(
        text=result_text,
        input_tokens=int(usage.get("input_tokens", 0)),
        output_tokens=int(usage.get("output_tokens", 0)),
        tool_calls=tool_calls,
        is_error=bool(d.get("is_error", False)),
    )


async def run_variant(
    variant: Variant,
    scenario: Scenario,
    runner_cfg: RunnerCfg,
    out_dir: Path,
    *,
    spawner: Spawner = _default_spawn,
) -> Observation:
    """Run a single variant via ``claude -p`` and write its observation JSON."""
    out_dir = Path(out_dir)
    cmd = _build_cmd(variant, scenario, runner_cfg)
    if runner_cfg.bare and _is_slash_command(scenario.input):
        sys.stderr.write(
            f"[parallel-ab] variant {variant.id}: --bare suppressed — "
            f"slash-command input needs skills loaded\n"
        )
    t0 = time.monotonic()

    try:
        result = await spawner(cmd, runner_cfg.timeout_seconds)
    except asyncio.TimeoutError:
        return _write_obs(
            Observation(
                variant_id=variant.id,
                exit_status="timeout",
                wall_seconds=time.monotonic() - t0,
            ),
            out_dir,
        )

    # Auth-fallback retry: drop --bare and try again once.
    if (
        result.returncode != 0
        and runner_cfg.bare
        and runner_cfg.oauth_fallback
        and _looks_like_auth_fail(result.stderr)
    ):
        sys.stderr.write(
            f"[parallel-ab] variant {variant.id}: auth-like failure; "
            f"retrying without --bare\n"
        )
        retry_cmd = [c for c in cmd if c != "--bare"]
        try:
            result = await spawner(retry_cmd, runner_cfg.timeout_seconds)
        except asyncio.TimeoutError:
            return _write_obs(
                Observation(
                    variant_id=variant.id,
                    exit_status="timeout",
                    wall_seconds=time.monotonic() - t0,
                ),
                out_dir,
            )

    parsed = _parse_output(result.stdout)
    # claude -p can return rc=0 with `is_error: true` for API-level failures
    # (rate limit, overload) — treat those as error, not ok.
    ok = result.returncode == 0 and not parsed.is_error
    obs = Observation(
        variant_id=variant.id,
        exit_status="ok" if ok else "error",
        wall_seconds=time.monotonic() - t0,
        tokens=Tokens(input=parsed.input_tokens, output=parsed.output_tokens),
        tool_calls=parsed.tool_calls,
        final_output_sha256=compute_sha256(parsed.text),
        axes=parsed.axes,
    )
    return _write_obs(obs, out_dir)


def _write_obs(obs: Observation, out_dir: Path) -> Observation:
    emit(obs, out_dir / f"obs-{obs.variant_id}.json")
    return obs
