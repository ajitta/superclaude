# Integration Test Design: Cross-Directory Reference Validation

**Target**: SuperClaude 6-directory cross-referencing system
**Scope**: Content consistency and wiring integrity across core/, agents/, modes/, mcp/, hooks/, scripts/
**Type**: Integration (file-system, no mocking)
**Status**: Design only — no implementation

---

## 1. Context and Rationale

SuperClaude's content framework is a graph of cross-references between markdown files,
Python scripts, and JSON configs. A persona abbreviation in FLAGS.md must resolve to an
agent filename. An MCP abbreviation in an agent's `<mcp servers="..."/>` must be declared
in FLAGS.md and have a corresponding MCP_*.md doc file. A path string in TRIGGER_MAP must
point to a file that exists on disk.

None of these contracts are enforced by the Python type system or import machinery. They
are text-based and break silently — a broken persona abbreviation does not raise an
exception; Claude simply gets no agent routing. The existing `tests/unit/test_agent_structure.py`
validates per-agent file structure thoroughly, but no tests span directory boundaries.

This document specifies the integration test suite that closes that gap.

---

## 2. Test File Location

```
tests/
└── integration/
    ├── __init__.py                         (exists)
    ├── test_pytest_plugin.py               (exists — plugin fixture tests)
    └── test_cross_directory_refs.py        (NEW — this design)
```

Rationale for `tests/integration/`: these tests do file I/O against the real source tree
and verify multi-file consistency, which matches the integration test definition already
used in this project (contrast with unit tests in `tests/unit/` that test Python class
behaviour with fixtures). They are also meaningfully slower than unit tests if the file
count grows, so the existing `pytest -m` marker separation remains useful.

No new conftest.py is needed. The tests share a single module-level fixture that resolves
the content root path.

---

## 3. Fixtures

All fixtures are module-level constants or session-scoped pytest fixtures. No mocking.

```python
# Canonical path resolution — all tests derive from this
CONTENT_ROOT = Path(__file__).parent.parent.parent / "src" / "superclaude"

# Derived directories
AGENTS_DIR  = CONTENT_ROOT / "agents"
MODES_DIR   = CONTENT_ROOT / "modes"
MCP_DIR     = CONTENT_ROOT / "mcp"
CORE_DIR    = CONTENT_ROOT / "core"
HOOKS_DIR   = CONTENT_ROOT / "hooks"
SCRIPTS_DIR = CONTENT_ROOT / "scripts"
SKILLS_DIR  = CONTENT_ROOT / "skills"
COMMANDS_DIR = CONTENT_ROOT / "commands"
```

### Shared parsing helpers (module-level functions, not fixtures)

```python
def parse_flags_persona_index(flags_md: Path) -> dict[str, str]:
    """Parse <persona_index> from FLAGS.md.

    Input line format:
        arch=system-architect(architecture) | fe=frontend-architect(UI,a11y) | ...

    Returns:
        {"arch": "system-architect", "fe": "frontend-architect", ...}

    Strategy:
        1. Extract content of <persona_index>...</persona_index> via regex
        2. Split on ' | '
        3. For each token, split on '=' to get abbreviation and target
        4. Strip the parenthetical suffix from target: "system-architect(architecture)" -> "system-architect"
    """

def parse_flags_mcp_abbreviations(flags_md: Path) -> dict[str, str]:
    """Parse <mcp>...</mcp> flag definitions from FLAGS.md.

    Input line format:
        --c7|--context7: imports, frameworks, official docs -> Context7 curated docs

    Returns all short aliases:
        {"c7": "--c7", "context7": "--context7", "seq": "--seq", "sequential": "--sequential", ...}

    Strategy:
        1. Extract <mcp>...</mcp> block
        2. For each line starting with '--', split on ':' to get flag string
        3. Split flag string on '|' to get all aliases
        4. Strip leading '--' from each alias
    """

def parse_agent_mcp_servers(agent_path: Path) -> list[str]:
    """Extract MCP server abbreviations from <mcp servers="..."/> in an agent file.

    Returns:
        ["seq", "c7"] from <mcp servers="seq|c7"/>

    Strategy:
        regex r'<mcp\s+servers=["\']([^"\']*)["\']' on file content,
        then split result on '|'
    """

def parse_command_personas(command_path: Path) -> list[str]:
    """Extract persona abbreviations from <personas p="..."/> in a command file.

    Returns:
        ["arch", "fe", "be"] from <personas p="arch|fe|be"/>

    Strategy:
        regex r'<personas\s+[^>]*p=["\']([^"\']*)["\']' on file content,
        then split result on '|'
    """

def parse_trigger_map_paths(context_loader: Path) -> list[str]:
    """Extract relative file paths from TRIGGER_MAP in context_loader.py.

    Returns:
        ["modes/MODE_Brainstorming.md", "mcp/MCP_Context7.md", ...]

    Strategy:
        Import context_loader as a module and read the TRIGGER_MAP list
        directly before regex compilation (the raw string tuples).
        Fallback: regex r'"((?:modes|mcp|core)/[^"]+\.md)"' on file content.

    Note: Use the import approach to stay in sync with actual runtime paths.
    The regex fallback avoids import side effects (CACHE_DIR creation).
    """

def parse_composite_flag_paths(context_loader: Path) -> list[str]:
    """Extract paths from COMPOSITE_FLAGS in context_loader.py.

    Returns unique path strings from --frontend-verify and --all-mcp entries.
    Same import/regex strategy as parse_trigger_map_paths.
    """

def parse_hooks_json_script_refs(hooks_json: Path) -> list[str]:
    """Extract script filenames from hooks.json command strings.

    Returns:
        ["session_init.py", "context_reset.py", "skill_activator.py",
         "context_loader.py", "prettier_hook.py", "test_runner_hook.py"]

    Strategy:
        json.loads(hooks_json.read_text())
        Walk all "command" values, extract filename after '{{SCRIPTS_PATH}}/'
        via regex r'\{\{SCRIPTS_PATH\}\}/(\S+\.py)'
    """

def parse_skill_agent_field(skill_manifest: Path) -> str | None:
    """Extract 'agent:' value from SKILL.md YAML frontmatter.

    Returns:
        "quality-engineer" or None if not present

    Strategy:
        Same parse_frontmatter logic already in test_agent_structure.py.
        Candidate for extraction to tests/helpers.py if shared across modules.
    """
```

---

## 4. Test Cases

Grouped by integration point. Each group maps to a test class in `test_cross_directory_refs.py`.

### 4.1 FLAGS.md persona_index -> Agent filenames

**Class**: `TestPersonaIndexResolution`

**Risk**: HIGH. Every command's `<personas p="..."/>` and the FLAGS.md model routing table
depend on this mapping. A mismatched abbreviation silently disables agent routing.

| ID | Test name | What it checks | Pass condition |
|----|-----------|----------------|----------------|
| P01 | `test_every_persona_target_file_exists` | Each value in persona_index maps to an existing .md file | `AGENTS_DIR / f"{target}.md"` exists for all targets |
| P02 | `test_no_duplicate_abbreviations` | Abbreviation keys in persona_index are unique | `len(parsed) == len(set(parsed.keys()))` |
| P03 | `test_alias_targets_same_file` | Aliases like `qa=quality-engineer` and `qual=quality-engineer` both resolve | The target file exists regardless of how many abbreviations point to it |
| P04 | `test_model_routing_names_are_valid_agents` | Agent names in FLAGS.md `<model_routing>` (opus/sonnet/haiku lists) all have corresponding .md files | Parse the three lists, verify each stem exists in AGENTS_DIR |

**Parsing strategy for P04**: Extract `<model_routing>...</model_routing>` block, find
lines containing `opus:`, `sonnet:`, `haiku:`, split on comma/whitespace to get names.

---

### 4.2 FLAGS.md MCP abbreviations -> MCP doc files

**Class**: `TestMcpFlagToDocResolution`

**Risk**: HIGH. The INSTRUCTION_MAP in context_loader.py and agent `<mcp servers="..."/>`
tags both depend on consistent MCP abbreviations.

MCP doc filename convention: `MCP_{Name}.md` where `Name` is the proper-cased server name.

Abbreviation-to-filename mapping (derived from FLAGS.md `<mcp>` block):

| Flag | Expected doc file |
|------|------------------|
| c7, context7 | MCP_Context7.md |
| seq, sequential | MCP_Sequential.md |
| magic | MCP_Magic.md |
| morph, morphllm | MCP_Morphllm.md |
| serena | MCP_Serena.md |
| play, playwright | MCP_Playwright.md |
| perf, devtools | MCP_Chrome-DevTools.md |
| tavily | MCP_Tavily.md |

| ID | Test name | What it checks | Pass condition |
|----|-----------|----------------|----------------|
| M01 | `test_every_mcp_flag_has_doc_file` | Every primary abbreviation in FLAGS.md `<mcp>` block corresponds to a MCP_*.md file | Verify the 8 canonical doc files exist; test fails if any is missing |
| M02 | `test_mcp_config_doc_pairing` | Every .json in mcp/configs/ has a matching MCP_*.md and vice versa | `{stem}.json` and `MCP_{StemProper}.md` both present for all 8 MCPs |
| M03 | `test_no_orphan_mcp_doc_files` | No MCP_*.md file exists without a FLAGS.md declaration | Parse FLAGS.md MCP names, compare against glob of MCP_*.md files |

**Note on M02**: The pairing is by convention (e.g. `configs/context7.json` ↔ `MCP_Context7.md`).
Test should define the expected mapping explicitly rather than attempting to infer it dynamically,
to make failures obvious rather than masked by mapping logic errors.

---

### 4.3 Agent `<mcp servers="..."/>` -> FLAGS.md abbreviations

**Class**: `TestAgentMcpServerRefs`

**Risk**: MEDIUM. An unrecognised server abbreviation is a silent no-op. This is the
contract between agent authors and FLAGS.md maintainers.

| ID | Test name | What it checks | Pass condition |
|----|-----------|----------------|----------------|
| A01 | `test_all_agent_mcp_abbreviations_in_flags` | Every abbreviation in every agent's `<mcp servers="..."/>` exists as a key in FLAGS.md MCP section | Parametrised over all agent files; collect all server tokens, compare against `parse_flags_mcp_abbreviations()` |
| A02 | `test_readme_agent_examples_use_valid_abbreviations` | agents/README.md example `<mcp servers="..."/>` snippets use valid abbreviations | Same check applied to README.md content |

**Observed abbreviations in use** (from codebase scan):
`seq`, `c7`, `serena`, `morph`, `play`, `perf`, `tavily`, `magic`

All present in FLAGS.md. Test becomes the regression guard for future additions.

---

### 4.4 context_loader.py TRIGGER_MAP paths -> Actual files

**Class**: `TestTriggerMapFilePaths`

**Risk**: HIGH. A missing file in TRIGGER_MAP produces a silent context injection failure.
This is the primary runtime wiring that loads behavioral context into Claude.

| ID | Test name | What it checks | Pass condition |
|----|-----------|----------------|----------------|
| T01 | `test_all_trigger_map_paths_exist` | Every relative path in TRIGGER_MAP exists under CONTENT_ROOT | `(CONTENT_ROOT / path).exists()` for all paths |
| T02 | `test_all_composite_flag_paths_exist` | Every path in COMPOSITE_FLAGS (`--frontend-verify`, `--all-mcp`) exists | Same existence check |
| T03 | `test_instruction_map_paths_are_subset_of_trigger_map` | Every key in INSTRUCTION_MAP is also in TRIGGER_MAP | `set(INSTRUCTION_MAP.keys()) <= {path for path, _ in raw_TRIGGER_MAP}` |
| T04 | `test_no_duplicate_trigger_map_paths` | Same relative path does not appear twice in TRIGGER_MAP | `len(paths) == len(set(paths))` |
| T05 | `test_mode_files_in_trigger_map_are_not_in_instruction_map` | Mode files use full .md injection, not short instructions | `not any(p.startswith("modes/") for p in INSTRUCTION_MAP)` |

**Parsing strategy**: Extract raw TRIGGER_MAP before re.compile step. The raw list is
defined as a list of `(pattern_str, path, priority)` tuples in lines 86-173. Import the
module with `importlib.import_module` after inserting CONTENT_ROOT.parent.parent into
sys.path, then read `context_loader.TRIGGER_MAP` — but this fires `_get_base_path()` and
creates the cache dir. Safer: apply the regex `r'"((?:modes|mcp|core)/[^"]+\.md)"'`
directly against the source file text to extract path strings without executing module-level
side effects.

---

### 4.5 hooks.json script paths -> Actual script files

**Class**: `TestHooksJsonScriptPaths`

**Risk**: HIGH. A missing script produces a hook execution failure at session start or
on every prompt — the noisiest possible failure mode.

| ID | Test name | What it checks | Pass condition |
|----|-----------|----------------|----------------|
| H01 | `test_all_hooks_json_scripts_exist` | Every `{{SCRIPTS_PATH}}/script.py` reference in hooks.json corresponds to an existing file in `src/superclaude/scripts/` | Extract filenames via `parse_hooks_json_script_refs()`, verify each exists in SCRIPTS_DIR |
| H02 | `test_hooks_json_is_valid_json` | hooks.json parses without error | `json.loads(content)` does not raise |
| H03 | `test_hooks_json_has_expected_event_keys` | Top-level "hooks" dict contains the 4 known events | `{"SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse"} <= set(data["hooks"].keys())` |
| H04 | `test_hooks_json_schema_version_present` | schema_version field exists | `"schema_version" in data` |

---

### 4.6 mcp/configs/*.json -> mcp/MCP_*.md parity

**Class**: `TestMcpConfigDocParity`

**Risk**: LOW-MEDIUM. Orphaned configs or docs create install-time confusion but do not
break runtime. However, the install logic in `install_mcp.py` pairs these files, so
asymmetry can cause silent install failures.

| ID | Test name | What it checks | Pass condition |
|----|-----------|----------------|----------------|
| C01 | `test_config_count_matches_doc_count` | Number of .json configs equals number of MCP_*.md docs | `len(config_files) == len(doc_files)` |
| C02 | `test_every_config_has_matching_doc` | For each configs/*.json, a MCP_{proper_name}.md exists | Define explicit mapping: `{"context7": "Context7", "sequential": "Sequential", ...}` |
| C03 | `test_every_doc_has_matching_config` | Inverse: for each MCP_*.md, a *.json exists | Same mapping, checked in reverse |

**Expected mapping** (hardcoded for clarity, not inferred):
```python
CONFIG_TO_DOC = {
    "context7":       "Context7",
    "sequential":     "Sequential",
    "playwright":     "Playwright",
    "serena":         "Serena",
    "morphllm":       "Morphllm",
    "magic":          "Magic",
    "tavily":         "Tavily",
    "chrome-devtools": "Chrome-DevTools",
}
```

---

### 4.7 MODE_Business_Panel.md `<selection ref="...">` -> Core file

**Class**: `TestModeXmlCrossRefs`

**Risk**: LOW. One file, one reference. But it tests a pattern that may expand as more
modes gain `ref=` attributes.

| ID | Test name | What it checks | Pass condition |
|----|-----------|----------------|----------------|
| X01 | `test_business_panel_selection_ref_exists` | `<selection ref="core/BUSINESS_SYMBOLS.md ..."/>` resolves to an existing file | Extract `ref` attr value, strip any fragment (space-delimited), check existence under CONTENT_ROOT |
| X02 | `test_all_mode_xml_refs_resolve` | Any `ref="..."` attribute in any mode file resolves | Glob all mode .md files, extract all `ref=` attrs, verify each as a file path |

---

### 4.8 Skill `agent:` field -> VALID_AGENTS -> Agent files (three-way)

**Class**: `TestSkillAgentThreeWay`

**Risk**: MEDIUM. skill_activator.py's VALID_AGENTS set is a manually maintained
allowlist. If a skill's `agent:` field references a name not in VALID_AGENTS, routing
silently falls back to None. If an agent file is added without updating VALID_AGENTS,
skills cannot route to it.

| ID | Test name | What it checks | Pass condition |
|----|-----------|----------------|----------------|
| S01 | `test_skill_agent_field_in_valid_agents` | Each skill's `agent:` frontmatter value is in `skill_activator.VALID_AGENTS` | Parse all SKILL.md files; for each `agent:` field, assert membership in VALID_AGENTS |
| S02 | `test_skill_agent_field_has_matching_file` | Each skill's `agent:` value also has a corresponding agent .md file | `(AGENTS_DIR / f"{agent_name}.md").exists()` |
| S03 | `test_valid_agents_all_have_files` | Every entry in VALID_AGENTS has an agent .md file | Verify no dangling entries in the set |
| S04 | `test_valid_agents_covers_all_agent_files` | Every agent .md file (excluding README) is represented in VALID_AGENTS | `{f.stem for f in AGENTS_DIR.glob("*.md") if f.name != "README.md"} == VALID_AGENTS` |

**Note**: S04 currently fails — `business-panel-experts`, `simplicity-guide`, `self-review`,
`requirements-analyst`, `socratic-mentor`, `learning-guide`, and `technical-writer` are
absent from VALID_AGENTS in skill_activator.py. This is expected: VALID_AGENTS appears to
only list agents that skills currently route to. The test should be written to document the
current gap explicitly rather than asserting equality, using `pytest.warns` or a softer
assertion with a clear message. The design choice about whether VALID_AGENTS should be
exhaustive is out of scope for this test suite and belongs in the IMPROVEMENT_PLAN.

Recommended formulation for S04:
```python
def test_valid_agents_subset_of_actual_agents():
    """VALID_AGENTS must not contain names without corresponding .md files.

    Note: VALID_AGENTS is intentionally a subset of all agents — it only
    covers agents that skill routing currently supports. This test catches
    stale entries only, not missing ones.
    """
    all_stems = {f.stem for f in AGENTS_DIR.glob("*.md") if f.name != "README.md"}
    for agent_name in VALID_AGENTS:
        assert agent_name in all_stems, f"VALID_AGENTS contains '{agent_name}' but no agents/{agent_name}.md exists"
```

---

### 4.9 Commands `<personas p="..."/>` -> FLAGS.md `<persona_index>`

**Class**: `TestCommandPersonaRefs`

**Risk**: MEDIUM. Commands are the primary user-facing entry point. An unresolvable persona
abbreviation silently fails to route to the correct agent during command execution.

| ID | Test name | What it checks | Pass condition |
|----|-----------|----------------|----------------|
| Q01 | `test_all_command_persona_abbreviations_in_flags` | Every abbreviation in every command's `<personas p="..."/>` exists as a key in FLAGS.md `<persona_index>` | Parametrised over all command .md files; collect all `p=` tokens, compare against `parse_flags_persona_index()` |
| Q02 | `test_all_command_persona_targets_have_files` | The resolved target agent file exists for every command persona | Compose Q01 + P01: abbreviation -> target name -> file existence |

**Commands without personas** (from codebase scan): `agent.md`, `help.md`, `load.md`,
`save.md`, `sc.md`, `task.md` (the last of which does have personas) — parser must
gracefully return an empty list for files without `<personas>`.

---

## 5. Parsing Strategy Summary

| Source | Parsing method | Risk of false negatives |
|--------|---------------|------------------------|
| FLAGS.md persona_index | Regex on `<persona_index>` block content, split on ` | ` | Low — format is stable |
| FLAGS.md MCP section | Regex on `<mcp>` block, extract `--flag` tokens | Low |
| Agent MCP servers | Regex `<mcp servers="([^"']*)"` | Low |
| Command personas | Regex `<personas[^>]*p="([^"']*)"` | Low — `auto=` attr must not interfere |
| TRIGGER_MAP paths | Regex `r'"((?:modes|mcp|core)/[^"]+\.md)"'` on source file | Low — format fixed by Python syntax |
| COMPOSITE_FLAGS paths | Same regex scoped to COMPOSITE_FLAGS dict block | Low |
| hooks.json scripts | `json.loads()` + walk "command" fields + regex `{{SCRIPTS_PATH}}/(\S+\.py)` | Low |
| SKILL.md agent field | Same `parse_frontmatter()` as test_agent_structure.py | Low |
| MODE ref= attrs | Regex `ref="([^"]*)"` on mode file content | Low |

All parsing is read-only against source files. No subprocess calls, no network, no
installed-path resolution. Tests run correctly from any working directory as long as
`Path(__file__).parent` resolves correctly.

---

## 6. Parametrisation Strategy

Tests P01, A01, A02, Q01, Q02 should be parametrised with `pytest.mark.parametrize` over
individual files so that a single broken file produces a named failure, not an obscure
index into a list:

```python
AGENT_FILES = sorted(
    f for f in AGENTS_DIR.glob("*.md") if f.name != "README.md"
)

@pytest.mark.parametrize("agent_path", AGENT_FILES, ids=lambda p: p.stem)
def test_all_agent_mcp_abbreviations_in_flags(agent_path):
    ...
```

This is consistent with the pattern already established in `test_agent_structure.py`.

Tests H01-H04 and C01-C03 need no parametrisation — they operate on single files.

---

## 7. CI Integration

### Should these run on every commit? Yes.

These tests are fast (see Section 8), have no external dependencies, and catch the class of
breakage that is hardest to detect by reading code — silent wiring failures. They belong in
the same `make test` / `uv run pytest` invocation as the unit tests.

### Recommended CI configuration

```yaml
# In CI pipeline (GitHub Actions or equivalent)
- name: Run full test suite
  run: uv run pytest tests/ -v --tb=short

# Optional: run cross-ref tests in isolation for faster feedback on content-only PRs
- name: Cross-reference integrity check (content PRs)
  run: uv run pytest tests/integration/test_cross_directory_refs.py -v
  if: contains(github.event.pull_request.changed_files, '.md') || contains(github.event.pull_request.changed_files, 'hooks.json')
```

### Marker recommendation

Tag the new test module with `@pytest.mark.integration` (already configured in pyproject.toml)
so it can be excluded from runs where only Python unit behaviour is under test:

```python
# At top of test_cross_directory_refs.py
pytestmark = pytest.mark.integration
```

This is consistent with the existing integration test in `tests/integration/test_pytest_plugin.py`.

### When cross-ref tests should be required (block merge):
- Any change to `src/superclaude/core/FLAGS.md`
- Any addition or removal of agent .md files
- Any change to `src/superclaude/hooks/hooks.json`
- Any change to `src/superclaude/scripts/context_loader.py`
- Any addition of a new skill SKILL.md

---

## 8. Expected Test Count and Execution Time

### Test count by class

| Class | Parametrised? | Base tests | Max expansions | Estimated total |
|-------|--------------|------------|----------------|-----------------|
| TestPersonaIndexResolution | No | 4 | — | 4 |
| TestMcpFlagToDocResolution | No | 3 | — | 3 |
| TestAgentMcpServerRefs | Yes (21 agent files) | 2 base | 21 per param test | ~23 |
| TestTriggerMapFilePaths | No | 5 | — | 5 |
| TestHooksJsonScriptPaths | No | 4 | — | 4 |
| TestMcpConfigDocParity | No | 3 | — | 3 |
| TestModeXmlCrossRefs | No | 2 | — | 2 |
| TestSkillAgentThreeWay | No | 4 | — | 4 |
| TestCommandPersonaRefs | Yes (30 command files) | 2 base | 30 per param test | ~32 |
| **Total** | | | | **~80** |

The parametrised tests (A01, Q01, Q02) expand over file count, not over individual
abbreviations, so the count stays bounded as the project grows.

### Execution time estimate

All tests perform:
- File existence checks (`Path.exists()` — ~0.1ms each)
- Regex matches against file content (~10-50ms per file read + match)
- JSON parse of hooks.json (~1ms)

With ~80 tests operating on ~70 files total, estimated wall time: **2-5 seconds**.
The existing 737-test suite runs in 1.33s; adding 80 tests reading ~70 files will roughly
double that. Total suite stays well under 10 seconds.

---

## 9. Test Gaps and Explicit Non-Goals

### Not covered by this design

| Gap | Reason excluded |
|-----|----------------|
| Semantic validity of content (e.g., "does this agent description make sense?") | Out of scope — human judgment required |
| Installed path validation (tests against ~/.claude/) | Belongs in `make verify` / `superclaude doctor`, not pytest |
| Hook runtime execution (does session_init.py actually produce correct output?) | Covered by the existing unit tests for individual scripts |
| Install path mapping in install_paths.py | Already covered by `tests/unit/test_cli_install.py` |
| Commands without `<personas>` | Acceptable — not all commands use agent routing |
| Agent files with multiple `<mcp>` tags | All current agents have exactly one; add if the pattern changes |

### Known acceptable failures to document

S04 (`test_valid_agents_covers_all_agent_files`) is expected to reveal that 7 agents are
absent from VALID_AGENTS. The test should be written to assert the less strict condition
(S03: no dangling entries), with a separate advisory test that logs the gap without failing,
until a deliberate decision is made about whether VALID_AGENTS should be exhaustive.

---

## 10. Suggested Addition to IMPROVEMENT_PLAN.md

Add the following entry under **Phase 1 — 1.4 scripts/ tests**:

```markdown
#### Cross-directory integration tests (NEW — `tests/integration/test_cross_directory_refs.py`)

| Integration point | Test class | Count |
|------------------|------------|-------|
| FLAGS.md persona_index ↔ agent files | TestPersonaIndexResolution | 4 |
| FLAGS.md MCP flags ↔ MCP_*.md docs | TestMcpFlagToDocResolution | 3 |
| Agent <mcp servers=""> ↔ FLAGS.md | TestAgentMcpServerRefs | ~23 |
| context_loader TRIGGER_MAP ↔ files | TestTriggerMapFilePaths | 5 |
| hooks.json scripts ↔ scripts/ | TestHooksJsonScriptPaths | 4 |
| mcp/configs/*.json ↔ MCP_*.md | TestMcpConfigDocParity | 3 |
| MODE ref= attrs ↔ core/ files | TestModeXmlCrossRefs | 2 |
| Skill agent: ↔ VALID_AGENTS ↔ files | TestSkillAgentThreeWay | 4 |
| Command personas ↔ FLAGS.md | TestCommandPersonaRefs | ~32 |
| **Total** | | **~80** |

Estimated execution time: 2-5s. Run on every commit. No mocking needed.
Coverage contribution: scripts/context_loader.py path constants gain indirect coverage.
```

Also add to **Phase 1 completion criteria**:
```markdown
- [ ] tests/integration/test_cross_directory_refs.py exists with ~80 tests passing
- [ ] All 9 cross-directory integration points are covered
```
