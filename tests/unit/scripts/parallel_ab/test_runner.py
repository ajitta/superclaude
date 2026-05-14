"""Tests for parallel-A/B single-variant runner (Phase 3)."""

from __future__ import annotations

import asyncio
import json
from dataclasses import replace
from pathlib import Path

import pytest

from superclaude.scripts.parallel_ab.observation import Observation, ToolCall
from superclaude.scripts.parallel_ab.runner import (
    SpawnResult,
    _build_cmd,
    _looks_like_auth_fail,
    _parse_output,
    run_variant,
)
from superclaude.scripts.parallel_ab.spec_loader import RunnerCfg, Scenario, Variant


def _scenario() -> Scenario:
    return Scenario(input="/sc:brainstorm rate limiter", baseline_skill="brainstorm")


def _variant(id_: str = "A", flag: str = "--vs[k:5]") -> Variant:
    return Variant(id=id_, flag=flag, extra_args="")


def _cfg(bare: bool = True, oauth_fallback: bool = True) -> RunnerCfg:
    return RunnerCfg(
        cli="claude -p",
        model="claude-haiku-4-5",
        timeout_seconds=60,
        bare=bare,
        oauth_fallback=oauth_fallback,
    )


def _json_stdout(
    text: str = "hello",
    input_tokens: int = 1240,
    output_tokens: int = 3200,
    tools: list[dict] | None = None,
) -> bytes:
    payload = {
        "result": text,
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
        "tools_used": tools or [],
    }
    return json.dumps(payload).encode("utf-8")


class _FakeSpawner:
    """Records calls and returns canned :class:`SpawnResult` per invocation."""

    def __init__(self, results: list[SpawnResult | Exception]):
        self._results = list(results)
        self.calls: list[tuple[list[str], int]] = []

    async def __call__(self, cmd: list[str], timeout_s: int) -> SpawnResult:
        self.calls.append((list(cmd), timeout_s))
        if not self._results:
            raise AssertionError("FakeSpawner exhausted")
        item = self._results.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


@pytest.mark.asyncio
async def test_ok_path_writes_observation(tmp_path: Path):
    spawner = _FakeSpawner([SpawnResult(stdout=_json_stdout(), stderr=b"", returncode=0)])
    obs = await run_variant(
        _variant(), _scenario(), _cfg(), tmp_path, spawner=spawner
    )
    assert isinstance(obs, Observation)
    assert obs.exit_status == "ok"
    assert obs.tokens.input == 1240
    assert obs.tokens.output == 3200
    out_file = tmp_path / "obs-A.json"
    assert out_file.exists()
    loaded = json.loads(out_file.read_text(encoding="utf-8"))
    assert loaded["variant_id"] == "A"
    assert loaded["exit_status"] == "ok"


@pytest.mark.asyncio
async def test_non_zero_exit_with_oauth_fallback_retries(tmp_path: Path):
    # plain (non-slash) input so --bare is actually added and the retry can drop it
    plain = Scenario(input="explain rate limiting", baseline_skill=None)
    spawner = _FakeSpawner([
        SpawnResult(stdout=b"", stderr=b"Error: not authenticated. Please log in.", returncode=1),
        SpawnResult(stdout=_json_stdout(), stderr=b"", returncode=0),
    ])
    obs = await run_variant(
        _variant(), plain, _cfg(bare=True, oauth_fallback=True), tmp_path,
        spawner=spawner,
    )
    assert obs.exit_status == "ok"
    assert len(spawner.calls) == 2
    # second cmd should drop --bare
    assert "--bare" in spawner.calls[0][0]
    assert "--bare" not in spawner.calls[1][0]


@pytest.mark.asyncio
async def test_non_zero_exit_without_oauth_fallback_does_not_retry(tmp_path: Path):
    spawner = _FakeSpawner([
        SpawnResult(stdout=b"", stderr=b"Error: not authenticated", returncode=1),
    ])
    obs = await run_variant(
        _variant(), _scenario(), _cfg(bare=True, oauth_fallback=False), tmp_path,
        spawner=spawner,
    )
    assert obs.exit_status == "error"
    assert len(spawner.calls) == 1


@pytest.mark.asyncio
async def test_non_zero_exit_without_auth_pattern_does_not_retry(tmp_path: Path):
    # exit=1 but stderr has no auth keywords → don't retry even with oauth_fallback
    spawner = _FakeSpawner([
        SpawnResult(stdout=b"", stderr=b"Error: file not found", returncode=1),
    ])
    obs = await run_variant(
        _variant(), _scenario(), _cfg(bare=True, oauth_fallback=True), tmp_path,
        spawner=spawner,
    )
    assert obs.exit_status == "error"
    assert len(spawner.calls) == 1


@pytest.mark.asyncio
async def test_timeout_produces_timeout_obs(tmp_path: Path):
    spawner = _FakeSpawner([asyncio.TimeoutError()])
    obs = await run_variant(
        _variant(), _scenario(), _cfg(), tmp_path, spawner=spawner
    )
    assert obs.exit_status == "timeout"
    assert (tmp_path / "obs-A.json").exists()


@pytest.mark.asyncio
async def test_tool_calls_parsed_from_json(tmp_path: Path):
    tools = [{"name": "Grep", "count": 3}, {"name": "Read", "count": 2}]
    spawner = _FakeSpawner([
        SpawnResult(stdout=_json_stdout(tools=tools), stderr=b"", returncode=0),
    ])
    obs = await run_variant(_variant(), _scenario(), _cfg(), tmp_path, spawner=spawner)
    assert obs.tool_calls == (
        ToolCall(name="Grep", count=3),
        ToolCall(name="Read", count=2),
    )


@pytest.mark.asyncio
async def test_plain_text_stdout_fallback_zero_tokens(tmp_path: Path):
    spawner = _FakeSpawner([SpawnResult(stdout=b"plain text reply", stderr=b"", returncode=0)])
    obs = await run_variant(_variant(), _scenario(), _cfg(), tmp_path, spawner=spawner)
    assert obs.exit_status == "ok"
    assert obs.tokens.input == 0
    assert obs.tokens.output == 0
    assert obs.final_output_sha256  # non-empty


# ---- pure helpers ----


def test_build_cmd_includes_bare():
    # non-slash input → --bare is honored
    plain = Scenario(input="explain rate limiting", baseline_skill=None)
    cmd = _build_cmd(_variant(), plain, _cfg(bare=True))
    assert "--bare" in cmd
    assert "--model" in cmd
    assert "claude-haiku-4-5" in cmd


def test_build_cmd_omits_bare():
    plain = Scenario(input="explain rate limiting", baseline_skill=None)
    cmd = _build_cmd(_variant(), plain, _cfg(bare=False))
    assert "--bare" not in cmd


def test_build_cmd_suppresses_bare_for_slash_command():
    # --bare strips skills → a /sc: input would resolve to "Unknown command"
    cmd = _build_cmd(_variant(), _scenario(), _cfg(bare=True))
    assert "--bare" not in cmd


def test_build_cmd_prompt_concatenates_input_flag_extra_args():
    v = Variant(id="X", flag="--vs", extra_args="--explain")
    cmd = _build_cmd(v, _scenario(), _cfg(bare=False))
    # prompt is the last argument
    prompt = cmd[-1]
    assert "/sc:brainstorm rate limiter" in prompt
    assert "--vs" in prompt
    assert "--explain" in prompt


def test_build_cmd_empty_flag_no_double_space():
    v = Variant(id="X", flag="", extra_args="")
    cmd = _build_cmd(v, _scenario(), _cfg(bare=False))
    assert cmd[-1] == "/sc:brainstorm rate limiter"


def test_looks_like_auth_fail_detects_keywords():
    assert _looks_like_auth_fail(b"Authentication failed")
    assert _looks_like_auth_fail(b"missing API key")
    assert _looks_like_auth_fail(b"unauthorized request")
    assert _looks_like_auth_fail(b"please login")
    assert _looks_like_auth_fail(b"invalid credentials")
    assert not _looks_like_auth_fail(b"file not found")
    assert not _looks_like_auth_fail(b"")


def test_parse_output_handles_invalid_json():
    p = _parse_output(b"not json at all")
    assert p.text == "not json at all"
    assert p.input_tokens == 0
    assert p.output_tokens == 0


def test_parse_output_extracts_usage_and_tools():
    payload = _json_stdout(text="reply", input_tokens=10, output_tokens=20,
                           tools=[{"name": "Bash", "count": 1}])
    p = _parse_output(payload)
    assert p.text == "reply"
    assert p.input_tokens == 10
    assert p.output_tokens == 20
    assert p.tool_calls == (ToolCall(name="Bash", count=1),)


def test_parse_output_extracts_is_error_flag():
    err_payload = json.dumps({"result": "rate limited", "is_error": True}).encode("utf-8")
    assert _parse_output(err_payload).is_error is True
    # absent key defaults to False
    assert _parse_output(_json_stdout()).is_error is False


@pytest.mark.asyncio
async def test_run_variant_marks_json_is_error_as_error(tmp_path: Path):
    # claude -p can return rc=0 with is_error=true (API-level failure)
    payload = json.dumps({"result": "overloaded", "is_error": True}).encode("utf-8")
    spawner = _FakeSpawner([SpawnResult(stdout=payload, stderr=b"", returncode=0)])
    obs = await run_variant(_variant(), _scenario(), _cfg(), tmp_path, spawner=spawner)
    assert obs.exit_status == "error"
