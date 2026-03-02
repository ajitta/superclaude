"""Skill dependency resolver.

Parses SKILL.md frontmatter for `requires` and `enhances` fields,
builds a dependency graph, and provides topological sort + cycle detection.

This is an experimental/prototype module (Phase 4 / Sprint 7).
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DepNode:
    """A node in the dependency graph."""

    name: str
    version: str
    requires_skills: list[str] = field(default_factory=list)
    requires_mcp: list[str] = field(default_factory=list)
    enhances_skills: list[str] = field(default_factory=list)


@dataclass
class DependencyIssue:
    """A problem found during dependency analysis."""

    kind: str  # "circular" | "missing_skill" | "missing_mcp"
    message: str
    involved: list[str] = field(default_factory=list)


class DependencyGraph:
    """Graph of skill dependencies with resolution and validation."""

    def __init__(self) -> None:
        self._nodes: dict[str, DepNode] = {}
        # Adjacency: skill -> list of skills it depends on
        self._edges: dict[str, list[str]] = defaultdict(list)

    @property
    def nodes(self) -> dict[str, DepNode]:
        return dict(self._nodes)

    def add_node(self, node: DepNode) -> None:
        """Register a skill node in the graph."""
        self._nodes[node.name] = node
        for dep in node.requires_skills:
            self._edges[node.name].append(dep)

    def resolve(self, skill_name: str) -> list[str]:
        """Return install order via topological sort starting from skill_name.

        Returns list of skill names in dependency-first order.
        Raises ValueError if skill_name is not in the graph.
        """
        if skill_name not in self._nodes:
            raise ValueError(f"Unknown skill: {skill_name}")

        visited: set[str] = set()
        order: list[str] = []

        def _dfs(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            for dep in self._edges.get(name, []):
                if dep in self._nodes:
                    _dfs(dep)
            order.append(name)

        _dfs(skill_name)
        return order

    def resolve_all(self) -> list[str]:
        """Return full topological sort of all skills (dependency-first)."""
        visited: set[str] = set()
        order: list[str] = []

        def _dfs(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            for dep in self._edges.get(name, []):
                if dep in self._nodes:
                    _dfs(dep)
            order.append(name)

        for name in sorted(self._nodes):
            _dfs(name)
        return order

    def check_circular(self) -> list[tuple[str, str]]:
        """Detect circular dependencies. Returns list of (from, to) edge pairs forming cycles."""
        cycles: list[tuple[str, str]] = []
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = {n: WHITE for n in self._nodes}

        def _dfs(name: str) -> None:
            color[name] = GRAY
            for dep in self._edges.get(name, []):
                if dep not in color:
                    continue
                if color[dep] == GRAY:
                    cycles.append((name, dep))
                elif color[dep] == WHITE:
                    _dfs(dep)
            color[name] = BLACK

        for name in self._nodes:
            if color[name] == WHITE:
                _dfs(name)

        return cycles

    def missing_dependencies(self) -> list[DependencyIssue]:
        """Find required skills/MCP servers that are not present in the graph."""
        issues: list[DependencyIssue] = []
        known_skills = set(self._nodes.keys())

        for name, node in sorted(self._nodes.items()):
            for dep in node.requires_skills:
                if dep not in known_skills:
                    issues.append(
                        DependencyIssue(
                            kind="missing_skill",
                            message=f"Skill '{name}' requires '{dep}' which is not installed",
                            involved=[name, dep],
                        )
                    )
            for mcp in node.requires_mcp:
                issues.append(
                    DependencyIssue(
                        kind="missing_mcp",
                        message=f"Skill '{name}' requires MCP server '{mcp}'",
                        involved=[name, mcp],
                    )
                )

        return issues

    def enhancement_map(self) -> dict[str, list[str]]:
        """Return mapping of skill -> list of skills that enhance it."""
        result: dict[str, list[str]] = defaultdict(list)
        for name, node in self._nodes.items():
            for target in node.enhances_skills:
                result[target].append(name)
        return dict(result)


def build_graph(skills_root: Path) -> DependencyGraph:
    """Build a DependencyGraph from all skills under skills_root.

    Uses extract_dependencies from skill_linter if available,
    otherwise falls back to direct frontmatter parsing.
    """
    graph = DependencyGraph()

    try:
        from .skill_linter import extract_dependencies
    except ImportError:
        extract_dependencies = None

    for entry in sorted(skills_root.iterdir()):
        if not entry.is_dir() or entry.name.startswith("_"):
            continue
        manifest = entry / "SKILL.md"
        if not manifest.exists():
            manifest = entry / "skill.md"
        if not manifest.exists():
            continue

        if extract_dependencies is not None:
            deps = extract_dependencies(entry)
        else:
            deps = _fallback_extract(entry)

        node = DepNode(
            name=deps.get("name", entry.name),
            version=deps.get("version", "unversioned"),
            requires_skills=deps.get("requires_skills", []),
            requires_mcp=deps.get("requires_mcp", []),
            enhances_skills=deps.get("enhances_skills", []),
        )
        graph.add_node(node)

    return graph


def _fallback_extract(skill_dir: Path) -> dict:
    """Minimal frontmatter extraction without yaml dependency."""
    import re

    try:
        import yaml
    except ImportError:
        yaml = None

    manifest = skill_dir / "SKILL.md"
    if not manifest.exists():
        manifest = skill_dir / "skill.md"
    if not manifest.exists():
        return {"name": skill_dir.name}

    text = manifest.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        return {"name": skill_dir.name}

    if yaml is not None:
        try:
            data = yaml.safe_load(match.group(1))
            if not isinstance(data, dict):
                return {"name": skill_dir.name}
        except Exception:
            return {"name": skill_dir.name}
    else:
        return {"name": skill_dir.name}

    metadata = data.get("metadata", {}) or {}
    requires = metadata.get("requires", {}) or {}
    enhances = metadata.get("enhances", {}) or {}

    return {
        "name": data.get("name", skill_dir.name),
        "version": data.get("version", "unversioned"),
        "requires_skills": requires.get("skills", []) or [],
        "requires_mcp": requires.get("mcp", []) or [],
        "enhances_skills": enhances.get("skills", []) or [],
    }
