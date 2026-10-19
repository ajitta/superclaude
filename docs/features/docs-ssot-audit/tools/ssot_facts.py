"""Print the SSOT facts the docs-ssot audit compares documents against.

Run from the repo root: ``uv run python docs/features/docs-ssot-audit/tools/ssot_facts.py``.
Read-only. Output is JSON on stdout; 02-method.md records the command.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "src" / "superclaude"
sys.path.insert(0, str(ROOT / "src"))


def md(sub: str, pattern: str = "*.md") -> list[str]:
    return sorted(
        p.name for p in (SRC / sub).glob(pattern) if p.name.upper() != "README.MD"
    )


def main() -> None:
    import click

    from superclaude.cli import main as cli_main
    from superclaude.cli.hook_dispatch import HOOKS
    from superclaude.cli.install_mcp import MCP_SERVERS
    from superclaude.cli.install_paths import COMPONENTS
    from superclaude.scripts import context_loader as cl
    from superclaude.utils import DEFAULT_CONTEXT_MAX_TOKENS

    facts: dict = {}
    facts["version"] = re.search(
        r'(?m)^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text()
    ).group(1)
    facts["counts"] = {
        "commands": len(md("commands")),
        "agents": len(md("agents")),
        "modes": len(md("modes", "MODE_*.md")),
        "mcp_docs": len(md("mcp", "MCP_*.md")),
        "output_styles": len(md("output-styles")),
        "skills": len([p for p in (SRC / "skills").iterdir() if p.is_dir()]),
        "core_always_loaded": 3,
        "core_rule_modules": len(md("core/rules")),
        "mcp_servers_registry": len(MCP_SERVERS),
        "hook_scripts": len(HOOKS),
    }
    facts["commands"] = [p[:-3] for p in md("commands")]
    facts["agents"] = [p[:-3] for p in md("agents")]
    facts["modes"] = md("modes")
    facts["mcp_docs"] = md("mcp", "MCP_*.md")
    facts["mcp_servers"] = {
        k: {"command": v.get("command"), "method": v.get("method")}
        for k, v in MCP_SERVERS.items()
    }
    facts["components"] = COMPONENTS
    hooks_json = json.loads((SRC / "hooks" / "hooks.json").read_text())
    regs = [
        (event, h["command"])
        for event, groups in hooks_json["hooks"].items()
        for g in groups
        for h in g["hooks"]
    ]
    facts["hooks_json"] = {
        "registrations": len(regs),
        "events": sorted({e for e, _ in regs}),
        "commands": sorted({c for _, c in regs}),
        "scripts": sorted({c.split()[2] for _, c in regs}),
    }
    facts["hook_registry"] = sorted(HOOKS)
    # CLI surface, by click introspection.
    cli: dict = {}

    def walk(cmd, name):
        info = {"help": (cmd.help or "").strip().splitlines()[0] if cmd.help else ""}
        params = []
        for p in cmd.params:
            if isinstance(p, click.Option):
                params.append({"opts": p.opts + p.secondary_opts, "help": p.help})
        info["options"] = params
        if isinstance(cmd, click.Group):
            info["subcommands"] = {}
            for sub, c in cmd.commands.items():
                info["subcommands"][sub] = walk(c, sub)
        return info

    for name, cmd in cli_main.main.commands.items():
        cli[name] = walk(cmd, name)
    facts["cli"] = cli
    facts["context_loader"] = {
        "DEFAULT_CONTEXT_MAX_TOKENS": DEFAULT_CONTEXT_MAX_TOKENS,
        "VALID_FLAGS": sorted(cl.VALID_FLAGS),
        "RETIRED_FLAGS": cl.RETIRED_FLAGS,
        "CC_NATIVE_PASSTHROUGH": sorted(cl.CC_NATIVE_PASSTHROUGH),
        "RETIRED_COMMANDS": cl.RETIRED_COMMANDS,
        "RETIRED_FUZZY_CUTOFF": cl.RETIRED_FUZZY_CUTOFF,
        "TRIGGER_MAP_files": sorted({t[1] for t in cl.TRIGGER_MAP}),
        "COMPOSITE_FLAGS": cl.COMPOSITE_FLAGS,
    }
    mk = (ROOT / "Makefile").read_text()
    facts["make_targets"] = sorted(
        re.search(r"^\.PHONY:(.*)$", mk, re.M).group(1).split()
    )
    wf = (ROOT / ".github" / "workflows" / "test.yml").read_text()
    facts["ci"] = {
        "python_matrix": re.findall(r'python-version: \[([^\]]+)\]', wf),
        "triggers": re.findall(r"^  (pull_request|push|workflow_dispatch):", wf, re.M),
        "jobs": re.findall(r"^  ([a-z-]+):\n    name:", wf, re.M),
    }
    core = SRC / "core"
    facts["core"] = {
        f: {"lines": len((core / f).read_text().splitlines()), "bytes": (core / f).stat().st_size}
        for f in ("FLAGS.md", "PRINCIPLES.md", "RULES.md")
    }
    facts["core"]["always_loaded_lines_total"] = sum(
        facts["core"][f]["lines"] for f in ("FLAGS.md", "PRINCIPLES.md", "RULES.md")
    )
    facts["core"]["RULES_md_est_tokens"] = facts["core"]["RULES.md"]["bytes"] // 4
    facts["core"]["RULES_md_sections"] = re.findall(
        r"^  <([a-z_]+)>", (core / "RULES.md").read_text(), re.M
    )
    tasks = (ROOT / "evals" / "tasks.yaml").read_text()
    facts["evals"] = {
        "arms": re.search(r"^arms: \[([^\]]+)\]", tasks, re.M).group(1).split(", "),
        "tasks": len(re.findall(r"^  - id:", tasks, re.M)),
    }
    facts["pyproject_dev_deps"] = re.findall(
        r'^\s+"([a-zA-Z0-9_-]+)[>=<]', re.search(r"dev = \[(.*?)\]", (ROOT / "pyproject.toml").read_text(), re.S).group(1), re.M
    )
    facts["docs_dirs"] = sorted(p.name for p in (ROOT / "docs").iterdir() if p.is_dir())
    facts["tests"] = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "tests").rglob("test_*.py"))
    print(json.dumps(facts, indent=1, default=str))


if __name__ == "__main__":
    main()
