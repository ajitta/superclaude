"""Routing-overlap guard for model-facing descriptions.

Claude Code routes by description: the model reads the skill listing (every
model-invocable command and skill) and the agent list, then picks one entry.
Two entries in the same list whose descriptions say nearly the same thing leave
that pick to chance, and no per-file test sees it, because each file is fine on
its own.

This is a lexical approximation, borrowed from addyosmani/agent-skills
(`scripts/run-evals.js`, Tier 2): stemmed TF-IDF vectors over the name and the
description, cosine similarity per pair, inside each list Claude Code shows
the model. It catches the near-duplicate a copy-paste or a renamed command
leaves behind; it cannot judge meaning, which only a model run can.

What is compared is the routing text, not the whole description:
- the on-request tier sentence is the same words in every on-request command
  (`test_command_structure.py` pins it), so it says nothing about the entry;
- the "Not for …" gate names the sibling to use instead on purpose
  ("specialist waves — /sc:pm"), so siblings that disambiguate each other would
  read as overlapping. Measured on the 4.30.5 tree: with the gate kept,
  /sc:agent and /sc:pm scored 0.75; with it stripped, 0.21.
"""

from __future__ import annotations

import itertools
import math
import re
from pathlib import Path

import pytest

from tests.unit.md_helpers import load_frontmatter

SRC = Path(__file__).parent.parent.parent / "src" / "superclaude"

# Pairs at or above this cosine fail. The 4.30.5 tree peaks at 0.55
# (/sc:save vs /sc:load, a deliberate mirror pair that differs in its verb);
# agents peak at 0.24. agent-skills fails at 0.75; 0.70 keeps the same margin
# over our own highest legitimate pair.
OVERLAP_MAX = 0.70

_STOP = frozenset(
    "a an and any are as at be before by for from in into is it its my need needs "
    "of on or our so that the them this to use want we when with you your help me i".split()
)
_ON_REQUEST = re.compile(
    r"On request only — the user's /sc:[\w-]+ or a workflow step that names it\."
)
_NOT_FOR = re.compile(r"\bNot for\b")


def _stem(token: str) -> str:
    """Light suffix stripping (agent-skills' stemmer), not a real stemmer."""
    for suffix in ("ally", "ing", "ed", "es", "al"):
        if len(token) > len(suffix) + 3 and token.endswith(suffix):
            token = token[: -len(suffix)]
            break
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        token = token[:-1]
    if len(token) > 4 and token.endswith("e"):
        token = token[:-1]
    if len(token) > 4 and token[-1] == token[-2] and token[-1] not in "aeiou":
        token = token[:-1]
    if len(token) > 3 and token.endswith("y"):
        token = token[:-1] + "i"
    return token


def _tokens(text: str) -> list[str]:
    words = re.split(r"[\s-]+", re.sub(r"[^a-z0-9\s-]", " ", text.lower()))
    return [_stem(w) for w in words if len(w) > 2 and w not in _STOP]


def routing_text(description: str) -> str:
    """The part of a description that routes: no tier boilerplate, no sibling gate."""
    return _ON_REQUEST.sub("", _NOT_FOR.split(description, maxsplit=1)[0])


def similarities(entries: dict[str, str]) -> list[tuple[float, str, str]]:
    """Cosine of every pair of ``{name: routing text}``, highest first.

    The name counts twice, as in agent-skills: a name is the strongest routing cue.
    """
    docs: dict[str, dict[str, int]] = {}
    for name, text in entries.items():
        name_tokens = _tokens(name.replace("-", " "))
        counts: dict[str, int] = {}
        for token in name_tokens + name_tokens + _tokens(text):
            counts[token] = counts.get(token, 0) + 1
        docs[name] = counts
    df: dict[str, int] = {}
    for counts in docs.values():
        for token in counts:
            df[token] = df.get(token, 0) + 1
    n = len(docs)
    vectors = {
        name: {t: f * math.log(1 + n / (1 + df[t])) for t, f in counts.items()}
        for name, counts in docs.items()
    }

    def cosine(a: dict[str, float], b: dict[str, float]) -> float:
        dot = sum(w * b.get(t, 0.0) for t, w in a.items())
        norm = math.sqrt(sum(w * w for w in a.values())) * math.sqrt(
            sum(w * w for w in b.values())
        )
        return dot / norm if norm else 0.0

    pairs = [
        (cosine(vectors[a], vectors[b]), a, b)
        for a, b in itertools.combinations(sorted(vectors), 2)
    ]
    return sorted(pairs, reverse=True)


def _description(path: Path) -> str:
    front = load_frontmatter(path)
    return f"{front.get('description') or ''} {front.get('when_to_use') or ''}".strip()


def skill_listing() -> dict[str, str]:
    """Every entry the model sees in the skill listing: commands plus model-invocable skills."""
    entries = {
        f"sc:{p.stem}": routing_text(_description(p))
        for p in sorted((SRC / "commands").glob("*.md"))
        if p.name != "README.md"
    }
    for path in sorted((SRC / "skills").glob("*/SKILL.md")):
        if load_frontmatter(path).get("disable-model-invocation") is True:
            continue  # not in the listing at all
        entries[path.parent.name] = routing_text(_description(path))
    return entries


def agent_list() -> dict[str, str]:
    return {
        p.stem: routing_text(_description(p))
        for p in sorted((SRC / "agents").glob("*.md"))
        if p.name != "README.md"
    }


@pytest.mark.parametrize(
    "pool", [skill_listing, agent_list], ids=["skill-listing", "agents"]
)
def test_no_two_entries_route_alike(pool):
    entries = pool()
    assert len(entries) > 1
    overlapping = [p for p in similarities(entries) if p[0] >= OVERLAP_MAX]
    assert not overlapping, (
        "descriptions too alike to route apart (fix the description, not the threshold): "
        + "; ".join(f"{a} ↔ {b} {score:.2f}" for score, a, b in overlapping)
    )


def test_overlap_metric_discriminates():
    """The guard can fail: a renamed copy scores above the cap, unrelated entries far below."""
    listing = skill_listing()
    copy = dict(listing, **{"sc:review-copy": listing["sc:review"]})
    top_score, a, b = similarities(copy)[0]
    assert {a, b} == {"sc:review", "sc:review-copy"}
    assert top_score >= OVERLAP_MAX
    scores = {frozenset((a, b)): s for s, a, b in similarities(listing)}
    assert scores[frozenset(("sc:git", "sc:research"))] < 0.2


def test_sibling_gate_is_not_counted_as_overlap():
    """The Not-for gate names siblings on purpose; stripping it is what keeps them apart."""
    raw = {
        f"sc:{p.stem}": _description(p)
        for p in sorted((SRC / "commands").glob("*.md"))
        if p.name != "README.md"
    }
    pair = frozenset(("sc:agent", "sc:pm"))
    with_gate = {frozenset((a, b)): s for s, a, b in similarities(raw)}[pair]
    routed = {frozenset((a, b)): s for s, a, b in similarities(skill_listing())}[pair]
    assert routed < with_gate
    assert routed < OVERLAP_MAX
    assert "/sc:" not in routing_text(raw["sc:pm"]) + routing_text(raw["sc:agent"])


# README "All Commands" states the listing cost of superclaude's own entries.
README_LISTING_CLAIM = (
    "superclaude's descriptions take under 10,000 characters together"
)
README_LISTING_LIMIT = 10_000


def test_readme_listing_figure_holds():
    """The README figure stays true: grow past it and the README must change too."""
    readme = (SRC.parent.parent / "README.md").read_text(encoding="utf-8")
    assert README_LISTING_CLAIM in readme
    listed = [p for p in (SRC / "commands").glob("*.md") if p.name != "README.md"]
    listed += [
        p
        for p in (SRC / "skills").glob("*/SKILL.md")
        if load_frontmatter(p).get("disable-model-invocation") is not True
    ]
    total = sum(len(_description(p)) for p in listed)
    assert total < README_LISTING_LIMIT, (
        f"listing text is {total} chars; update the README note"
    )
