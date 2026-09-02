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
    # None = no refusal; otherwise the stop_details.category or "unknown".
    refusal_category: str | None = None


Spawner = Callable[[list[str], int], Awaitable[SpawnResult]]


def detect_refusal(payload: dict) -> str | None:
    """Return the refusal category when *payload* records a model refusal.

    Claude Fable 5.x safety classifiers end a turn with the API's
    ``stop_reason: "refusal"`` plus ``stop_details.category`` (``cyber``,
    ``bio``, ``reasoning_extraction``, ...). The ``result`` object carries a
    top-level ``stop_reason`` but no ``stop_details`` (Claude Code 2.1.258
    result schema); the category lives on the assistant message, which the
    stream-json ``assistant`` events expose. Callers pass the assistant
    message first and the result object second and never let the result's
    ``"unknown"`` replace a category. A ``subtype`` naming a refusal counts
    as a fallback. A refusal is not ``is_error``: the CLI returns rc=0 and
    the refusal text lands in ``result``, which is why callers must not treat
    that text as a normal answer.
    """
    if not isinstance(payload, dict):
        return None
    refused = payload.get("stop_reason") == "refusal" or "refusal" in str(
        payload.get("subtype") or ""
    )
    if not refused:
        return None
    details = payload.get("stop_details") or {}
    category = details.get("category") if isinstance(details, dict) else None
    return str(category) if category else "unknown"


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
        "--model",
        cfg.model,
        # stream-json (which needs --verbose under -p) exposes the assistant
        # message objects, and with them the refusal category and per-call
        # tool_use blocks; the single-object json result carries neither.
        "--output-format",
        "stream-json",
        "--verbose",
    ]
    # `--bare` strips skills/plugins; a slash-command input would then resolve
    # to "Unknown command". Suppress --bare for slash inputs regardless of cfg.
    if cfg.bare and not _is_slash_command(scenario.input):
        cmd.append("--bare")
    prompt_parts = [s for s in (scenario.input, variant.flag, variant.extra_args) if s]
    cmd.append(" ".join(prompt_parts))
    return cmd


def _looks_like_auth_fail(stderr: bytes) -> bool:
    if not stderr:
        return False
    text = stderr.decode("utf-8", errors="replace")
    return bool(_AUTH_PATTERNS.search(text))


def _parse_events(text: str) -> list[dict]:
    """Return the JSON objects in *text*: one for ``--output-format json``,
    one per line for ``stream-json``. Non-JSON lines are skipped."""
    try:
        whole = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        whole = None
    if isinstance(whole, dict):
        return [whole]
    events: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(obj, dict):
            events.append(obj)
    return events


def _parse_output(stdout: bytes) -> ParsedResult:
    text = stdout.decode("utf-8", errors="replace")
    events = _parse_events(text)
    if not events:
        return ParsedResult(text=text)
    result = next((e for e in reversed(events) if e.get("type") == "result"), None)
    if result is None:
        # single-object json output has no `type`; a stream without a result
        # event (killed mid-run) parses as best-effort from what arrived.
        result = events[-1] if len(events) == 1 else {}
    assistant_msgs = [
        e.get("message") or {} for e in events if e.get("type") == "assistant"
    ]

    result_text = str(result.get("result") or result.get("output") or text)
    usage = result.get("usage") or {}

    tools_raw = result.get("tools_used") or []
    if tools_raw:
        tool_calls = tuple(
            ToolCall(name=str(t.get("name", "")), count=int(t.get("count", 0)))
            for t in tools_raw
            if isinstance(t, dict)
        )
    else:
        counts: dict[str, int] = {}
        for msg in assistant_msgs:
            for block in msg.get("content") or []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    name = str(block.get("name", ""))
                    counts[name] = counts.get(name, 0) + 1
        tool_calls = tuple(ToolCall(name=n, count=c) for n, c in sorted(counts.items()))

    # Assistant messages carry the category; the result object only confirms
    # the refusal, so it never downgrades a category already found.
    category: str | None = None
    for msg in assistant_msgs:
        found = detect_refusal(msg)
        if found is not None and (category is None or category == "unknown"):
            category = found
    if category is None:
        category = detect_refusal(result)

    return ParsedResult(
        text=result_text,
        input_tokens=int(usage.get("input_tokens", 0)),
        output_tokens=int(usage.get("output_tokens", 0)),
        tool_calls=tool_calls,
        is_error=bool(result.get("is_error", False)),
        refusal_category=category,
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
    # (rate limit, overload) — treat those as error, not ok. A safety refusal
    # also returns rc=0, with the refusal text in `result`; it gets its own
    # exit status so the matrix can tell "the model declined" from "the run
    # broke", which is the signal a model-release canary needs.
    refused = parsed.refusal_category is not None
    ok = result.returncode == 0 and not parsed.is_error and not refused
    if ok:
        exit_status = "ok"
    elif refused:
        exit_status = "refusal"
    else:
        exit_status = "error"
    obs = Observation(
        variant_id=variant.id,
        exit_status=exit_status,
        wall_seconds=time.monotonic() - t0,
        tokens=Tokens(input=parsed.input_tokens, output=parsed.output_tokens),
        tool_calls=parsed.tool_calls,
        final_output_sha256=compute_sha256(parsed.text),
        axes=parsed.axes,
        refusal_category=parsed.refusal_category or "",
    )
    return _write_obs(obs, out_dir)


def _write_obs(obs: Observation, out_dir: Path) -> Observation:
    emit(obs, out_dir / f"obs-{obs.variant_id}.json")
    return obs
