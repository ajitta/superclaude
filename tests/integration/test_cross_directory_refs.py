"""Cross-directory reference validation integration tests.

Verifies wiring integrity across core/, agents/, modes/, mcp/, hooks/, scripts/, commands/.
These tests read the real source tree (no mocking) and catch silent breakages
in text-based cross-references that the Python type system cannot enforce.

Design doc: docs/test-design-cross-ref-integration.md
"""

import json
import re
from pathlib import Path

import pytest

# --- Path constants ---
CONTENT_ROOT = Path(__file__).parent.parent.parent / "src" / "superclaude"
AGENTS_DIR = CONTENT_ROOT / "agents"
MODES_DIR = CONTENT_ROOT / "modes"
MCP_DIR = CONTENT_ROOT / "mcp"
CORE_DIR = CONTENT_ROOT / "core"
HOOKS_DIR = CONTENT_ROOT / "hooks"
SCRIPTS_DIR = CONTENT_ROOT / "scripts"
SKILLS_DIR = CONTENT_ROOT / "skills"
COMMANDS_DIR = CONTENT_ROOT / "commands"

pytestmark = pytest.mark.integration


# --- Parsing helpers ---


def parse_flags_mcp_section() -> dict[str, str]:
    """Parse <mcp> block from FLAGS.md for flag names.

    Returns: {"c7": "MCP_Context7.md", "context7": "MCP_Context7.md", ...}
    """
    content = (CORE_DIR / "FLAGS.md").read_text(encoding="utf-8")
    match = re.search(r"<mcp>(.*?)</mcp>", content, re.DOTALL)
    if not match:
        return {}

    # Extract all --flag entries
    flags = {}
    for line in match.group(1).strip().split("\n"):
        line = line.strip()
        if not line.startswith("--"):
            continue
        # e.g. "--c7|--context7: imports, frameworks, official docs → Context7 curated docs"
        flag_part = line.split(":")[0].strip()
        aliases = [f.strip().lstrip("-") for f in flag_part.split("|")]
        for alias in aliases:
            flags[alias] = alias
    return flags


def parse_agent_mcp_servers(agent_path: Path) -> list[str]:
    """Extract MCP server abbreviations from <mcp servers="..."/> in an agent file."""
    content = agent_path.read_text(encoding="utf-8")
    match = re.search(r'<mcp\s+servers=["\']([^"\']*)["\']', content)
    if not match:
        return []
    return [s.strip() for s in match.group(1).split("|") if s.strip()]



def parse_hooks_json_script_refs() -> list[str]:
    """Extract script filenames from hooks.json command strings."""
    content = (HOOKS_DIR / "hooks.json").read_text(encoding="utf-8")
    data = json.loads(content)
    scripts = set()
    for _event, entries in data.get("hooks", {}).items():
        for entry in entries:
            for hook in entry.get("hooks", []):
                cmd = hook.get("command", "")
                match = re.search(r"\{\{SCRIPTS_PATH\}\}/(\S+\.py)", cmd)
                if match:
                    scripts.add(match.group(1))
    return sorted(scripts)


def parse_skill_agent_field(skill_manifest: Path) -> str | None:
    """Extract 'agent:' value from SKILL.md YAML frontmatter."""
    content = skill_manifest.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return None
    # Find frontmatter block
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    frontmatter = parts[1]
    match = re.search(r"^\s*agent:\s*(.+)$", frontmatter, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


# NOTE: parse_model_routing_agents() removed — model routing moved from a
# centralized FLAGS.md <model_routing> block to per-agent frontmatter
# `model:` fields (Apr 2026). TestModelRouting was deleted alongside.


# --- Collected file lists for parametrize ---
AGENT_FILES = sorted(
    f for f in AGENTS_DIR.glob("*.md") if f.name != "README.md"
)
COMMAND_FILES = sorted(
    f for f in COMMANDS_DIR.glob("*.md") if f.name != "README.md"
)
SKILL_MANIFESTS = sorted(SKILLS_DIR.glob("*/SKILL.md"))


# ===== Test Classes =====


class TestMCPWiring:
    """FLAGS.md MCP flags → MCP doc files."""

    EXPECTED_MCP_DOCS = [
        "MCP_Context7.md",
        "MCP_Sequential.md",
        "MCP_Playwright.md",
        "MCP_Serena.md",
        "MCP_AstGrep.md",
        "MCP_Magic.md",
        "MCP_Tavily.md",
        "MCP_Chrome-DevTools.md",
    ]

    def test_every_mcp_doc_file_exists(self):
        for doc_name in self.EXPECTED_MCP_DOCS:
            doc_path = MCP_DIR / doc_name
            assert doc_path.exists(), f"Expected MCP doc {doc_name} not found"

    def test_mcp_config_doc_pairing(self):
        """Every .json in configs/ has a matching MCP_*.md."""
        CONFIG_TO_DOC = {
            "context7": "Context7",
            "sequential": "Sequential",
            "playwright": "Playwright",
            "serena": "Serena",
            "ast-grep": "AstGrep",
            "magic": "Magic",
            "tavily": "Tavily",
            "chrome-devtools": "Chrome-DevTools",
        }
        configs_dir = MCP_DIR / "configs"
        if not configs_dir.exists():
            pytest.skip("mcp/configs/ not found")
        for config_file in configs_dir.glob("*.json"):
            stem = config_file.stem
            assert stem in CONFIG_TO_DOC, f"No doc mapping for config {config_file.name}"
            doc_name = f"MCP_{CONFIG_TO_DOC[stem]}.md"
            assert (MCP_DIR / doc_name).exists(), (
                f"Config {config_file.name} expects {doc_name} but it's missing"
            )

    def test_no_orphan_mcp_doc_files(self):
        """No MCP_*.md file without a known mapping."""
        known = set(self.EXPECTED_MCP_DOCS)
        actual = {f.name for f in MCP_DIR.glob("MCP_*.md")}
        orphans = actual - known
        assert not orphans, f"Orphan MCP docs found: {orphans}"


# NOTE: TestTriggerMapPaths removed — context_trigger_map.py and
# context_injection.py were deleted; trigger wiring moved to runtime
# config files instead of importable modules.


class TestHooksScriptPaths:
    """hooks.json script paths → actual script files."""

    def test_all_hooks_json_scripts_exist(self):
        scripts = parse_hooks_json_script_refs()
        assert len(scripts) > 0, "No scripts found in hooks.json"
        for script in scripts:
            script_path = SCRIPTS_DIR / script
            assert script_path.exists(), (
                f"hooks.json references '{script}' but "
                f"scripts/{script} does not exist"
            )

    def test_hooks_json_is_valid_json(self):
        content = (HOOKS_DIR / "hooks.json").read_text(encoding="utf-8")
        data = json.loads(content)  # Raises on invalid JSON
        assert "hooks" in data

    def test_hooks_json_has_expected_event_keys(self):
        content = (HOOKS_DIR / "hooks.json").read_text(encoding="utf-8")
        data = json.loads(content)
        expected_events = {"SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse"}
        actual_events = set(data["hooks"].keys())
        assert expected_events <= actual_events, (
            f"Missing hook events: {expected_events - actual_events}"
        )

    def test_hooks_json_schema_version_present(self):
        content = (HOOKS_DIR / "hooks.json").read_text(encoding="utf-8")
        data = json.loads(content)
        assert "schema_version" in data


class TestAgentModeMapping:
    """Agent <mcp servers="..."/> → FLAGS.md MCP abbreviations."""

    @pytest.mark.parametrize("agent_path", AGENT_FILES, ids=lambda p: p.stem)
    def test_agent_mcp_abbreviations_are_valid(self, agent_path):
        servers = parse_agent_mcp_servers(agent_path)
        if not servers:
            pytest.skip(f"{agent_path.stem} has no <mcp servers>")
        flags_mcp = parse_flags_mcp_section()
        for server in servers:
            assert server in flags_mcp, (
                f"Agent {agent_path.stem} references MCP server '{server}' "
                f"not found in FLAGS.md <mcp> section"
            )


class TestSkillAgentRouting:
    """SKILL.md agent: → agent files (one-way).

    NOTE: VALID_AGENTS-based three-way checks removed — superclaude.scripts.
    skill_metadata module was deleted. The remaining check verifies that
    each skill's `agent:` field points to an actual agents/*.md file.
    """

    # Claude Code built-in agent types (no .md file in SuperClaude agents/)
    BUILTIN_AGENTS = {"general-purpose"}

    def test_skill_agent_field_has_matching_file(self):
        for manifest in SKILL_MANIFESTS:
            agent = parse_skill_agent_field(manifest)
            if agent and agent not in self.BUILTIN_AGENTS:
                agent_file = AGENTS_DIR / f"{agent}.md"
                assert agent_file.exists(), (
                    f"Skill {manifest.parent.name} has agent '{agent}' "
                    f"but agents/{agent}.md does not exist"
                )


class TestInstallPathsMapping:
    """COMPONENTS dict → source directories."""

    def test_all_component_source_dirs_exist(self):
        from superclaude.cli.install_paths import COMPONENTS
        for component, (source_subdir, _target, _desc) in COMPONENTS.items():
            source_dir = CONTENT_ROOT / source_subdir
            assert source_dir.exists(), (
                f"COMPONENTS['{component}'] source '{source_subdir}' "
                f"does not exist at {source_dir}"
            )

    def test_all_component_keys_match_expected(self):
        from superclaude.cli.install_paths import COMPONENTS
        expected = {"commands", "agents", "core", "modes", "mcp", "skills", "templates"}
        assert set(COMPONENTS.keys()) == expected


# NOTE: TestModeFileNaming removed — the test asserted lowercase kebab-case
# (e.g. brainstorming.md), but the project's official convention is
# `MODE_PascalCase.md` (see .claude/rules/mode-authoring.md "Naming"). The
# test was aspirational and contradicted the documented convention.


class TestCoreImportChain:
    """CLAUDE_SC.md @-references → actual files."""

    def test_claude_sc_references_valid(self):
        sc_path = CONTENT_ROOT / "CLAUDE_SC.md"
        if not sc_path.exists():
            pytest.skip("CLAUDE_SC.md not found in source")
        content = sc_path.read_text(encoding="utf-8")
        refs = re.findall(r"@(\S+)", content)
        assert len(refs) > 0, "No @-references found in CLAUDE_SC.md"
        for ref in refs:
            ref_path = CONTENT_ROOT / ref
            assert ref_path.exists(), (
                f"CLAUDE_SC.md references @{ref} but "
                f"{ref_path} does not exist"
            )

    def test_core_files_exist(self):
        """The 3 core files must exist."""
        for name in ["FLAGS.md", "PRINCIPLES.md", "RULES.md"]:
            assert (CORE_DIR / name).exists(), f"Core file {name} missing"


