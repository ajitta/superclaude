"""Parse and validate ``variants.yaml`` into a frozen :class:`ABSpec`."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ALLOWED_RUNNER_CLI = {"claude -p"}
DEFAULT_TIMEOUT_SECONDS = 60


class SpecError(ValueError):
    """Raised when ``variants.yaml`` fails validation."""


@dataclass(frozen=True)
class Scenario:
    input: str
    baseline_skill: str | None = None


@dataclass(frozen=True)
class Variant:
    id: str
    flag: str = ""
    extra_args: str = ""


@dataclass(frozen=True)
class RunnerCfg:
    cli: str
    model: str
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    bare: bool = True
    oauth_fallback: bool = True


@dataclass(frozen=True)
class ABSpec:
    scenario: Scenario
    variants: tuple[Variant, ...]
    runner: RunnerCfg


def _require(d: dict[str, Any], key: str, ctx: str) -> Any:
    if key not in d or d[key] in (None, ""):
        raise SpecError(f"{ctx}.{key} is required")
    return d[key]


def load_spec(path: Path) -> ABSpec:
    """Load and validate a ``variants.yaml`` spec file.

    Raises :class:`SpecError` on any structural or semantic violation.
    """
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise SpecError("top-level YAML must be a mapping")

    scenario_raw = raw.get("scenario") or {}
    if not isinstance(scenario_raw, dict):
        raise SpecError("scenario must be a mapping")
    scenario = Scenario(
        input=_require(scenario_raw, "input", "scenario"),
        baseline_skill=scenario_raw.get("baseline_skill"),
    )

    variants_raw = raw.get("variants") or []
    if not isinstance(variants_raw, list) or not variants_raw:
        raise SpecError("variants must be a non-empty list")
    seen: set[str] = set()
    variants: list[Variant] = []
    for idx, v in enumerate(variants_raw):
        if not isinstance(v, dict):
            raise SpecError(f"variants[{idx}] must be a mapping")
        vid = _require(v, "id", f"variants[{idx}]")
        if vid in seen:
            raise SpecError(f"duplicate variant id: {vid!r}")
        seen.add(vid)
        variants.append(
            Variant(
                id=str(vid),
                flag=str(v.get("flag", "")),
                extra_args=str(v.get("extra_args", "")),
            )
        )

    runner_raw = raw.get("runner") or {}
    if not isinstance(runner_raw, dict):
        raise SpecError("runner must be a mapping")
    cli = _require(runner_raw, "cli", "runner")
    if cli not in ALLOWED_RUNNER_CLI:
        raise SpecError(
            f"runner.cli must be one of {sorted(ALLOWED_RUNNER_CLI)}; got {cli!r}"
        )
    runner = RunnerCfg(
        cli=cli,
        model=_require(runner_raw, "model", "runner"),
        timeout_seconds=int(runner_raw.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)),
        bare=bool(runner_raw.get("bare", True)),
        oauth_fallback=bool(runner_raw.get("oauth_fallback", True)),
    )

    return ABSpec(scenario=scenario, variants=tuple(variants), runner=runner)
