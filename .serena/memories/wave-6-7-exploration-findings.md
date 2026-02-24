# Wave 6-7 Opus 4.6 Alignment - Codebase Exploration Findings

## WAVE 6 TARGETS

### 1. Skills: confidence-check/SKILL.md (SK1, SK2)

**Current State:**
- Frontmatter: name, description, triggers, mcp, context, agent, user-invocable, allowed-tools
- Hooks: PreToolUse for WebFetch|WebSearch with validate_confidence_context.py
- Component: XML format with role, stats, thresholds, checks, mcp_integration, usage, pytest, roi, bounds

**Issues Found:**
- **SK1**: No @deprecated annotation found (file is clean)
- **SK2**: No "disable-model-invocation" field in frontmatter (needs documentation if needed)

**Status:** ✅ SK1 clean, SK2 requires clarification on need

---

### 2. Hooks: hooks.json (H1, H3)

**Current State:**
- schema_version: "2.1.37"
- 5 hook types: SessionStart, UserPromptSubmit, PostToolUse, Setup, TeammateIdle, TaskCompleted
- TeammateIdle & TaskCompleted present with experimental markers (v2.1.33)
- All commands use {{SCRIPTS_PATH}} template variable
- "once: true" support for session-scoped hooks

**Issues Found:**
- **H1**: ✅ TeammateIdle/TaskCompleted already present with [experimental] markers
- **H3**: No async hook support documentation found (hooks are command-based, not async)

**Status:** ✅ H1 done, H3 requires documentation of async expectations/constraints

---

## WAVE 7 TARGETS

### 3. ALL Agent Files (A4, A5, A6, A7) - 20 agents

**Frontmatter Inventory:**

All 20 agents have consistent YAML frontmatter:
- name: [agent-name]
- description: [mission]
- memory: user (ALL agents have this field)

**No `autonomy` field found in ANY agent file (A6 STATUS):**
- pm-agent, system-architect, frontend-architect, backend-architect, security-engineer
- quality-engineer, devops-architect, performance-engineer, refactoring-expert, root-cause-analyst
- technical-writer, deep-research-agent, business-panel-experts, socratic-mentor, requirements-analyst
- learning-guide, self-review, python-expert, repo-index

**No `color` field found in ANY agent file (A4 STATUS):**
- Color coding not used in agent definitions
- Agent differentiation via role/mission/mindset instead

**Negative examples found (A5 STATUS):**
- ✅ pm-agent: "Never: Execute implementations directly, skip documentation, alter user code"
- ✅ system-architect: "Never: Implement code directly, make unilateral tech decisions, skip trade-off documentation"
- ✅ All agents have `<bounds will="..." wont="..."/>` sections with negative examples
- ✅ Some have `<tool_guidance>` with "Never" subsections

**Cross-references to commands found (A7 STATUS):**
- pm-agent: No command references
- system-architect: No command references
- quality-engineer: No command references
- refactoring-expert: Serena + Morphllm (MCP references, not commands)
- deep-research-agent: Tavily + Context7 (MCP references)
- business-panel-experts: Sequentia + Tavily (MCP references)
- socratic-mentor: Sequential + Context7 (MCP references)

**Status:** A4/A5/A6 need implementation, A7 shows minimal command cross-refs

---

### 4. Commands: index-repo.md vs index.md (CMD5)

**index.md:**
- Type: command | Mission: "Generate comprehensive project documentation"
- Flow: 1. Analyze 2. Organize 3. Generate 4. Validate 5. Maintain
- Outputs: Per --type (docs|api|structure|readme) → KNOWLEDGE.md, API.md, etc.
- Distinction: vs index-repo → index-repo is token-efficient (3KB), index is comprehensive

**index-repo.md:**
- Type: command | Mission: "Repository indexing with 94% token reduction (58K → 3K)"
- Flow: 1. Detect 2. Analyze 3. Extract 4. Generate (PROJECT_INDEX.md + .json) 5. Validate
- ROI: creation 2K tokens, reading 3K, full-read 58K
- Boundaries: document-only, preserve source code

**Relationship (CMD5):**
- `/sc:index` = comprehensive docs generation (multiple output types)
- `/sc:index-repo` = minimal token-efficient index (2 files: .md + .json)
- Clear separation: index is for knowledge base, index-repo for structure

**Status:** ✅ Relationship clear and documented in both files

---

### 5. Commands: internal section ordering (CMD6)

**Pattern observed across commands (agent.md, git.md, test.md, brainstorm.md, implement.md):**

Consistent order:
1. --- (frontmatter: description)
2. <component> + <config>
3. <role> (mission)
4. <syntax>
5. <triggers>
6. <flow>
7. <tools> or <outputs>
8. <checklist>
9. <mcp> or <personas>
10. <patterns>
11. <examples>
12. <bounds>
13. <boundaries> (optional, type="execution|document-only")
14. <handoff> (optional, next commands)

**Consistency:** ✅ Ordering is consistent across all command files examined

**Status:** CMD6 consistent

---

### 6. MODE_Token_Efficiency.md (M2)

**Deprecated symbols (v5.1):**
```xml
<deprecated v="5.1">
  double-arrow->arrow | 
  bidirectional-arrow->arrow | 
  therefore->arrow | 
  because->prose
</deprecated>
```

**Current symbol definitions:**
- Logic: ->, <->, &, |, :, >>
- Status: done, fail, warn, progress, pending, critical
- Domains: perf, analysis, config, security, deploy, design, arch

**Abbreviations defined:**
- System: cfg, impl, arch, perf, ops, env
- Process: req, deps, val, test, docs, std
- Quality: qual, sec, err, rec, sev, opt

**Status:** ✅ M2 deprecation documented, symbols defined clearly

---

### 7. Modes directory (M4)

**Files present:**
- MODE_Business_Panel.md
- MODE_Orchestration.md
- MODE_Introspection.md
- MODE_Task_Management.md
- MODE_DeepResearch.md
- MODE_Brainstorming.md
- MODE_Token_Efficiency.md
- __init__.py

**No README.md found in modes/ directory**

**Status:** M4 = No README.md in modes/

---

### 8. MCP directory files (MCP1, MCP5, MCP6, MCP7)

**MCP files present:**
- MCP_Magic.md
- MCP_Airis-Agent.md (deprecated)
- MCP_Morphllm.md
- MCP_Playwright.md
- MCP_Chrome-DevTools.md
- MCP_Context7.md
- MCP_Tavily.md
- MCP_Sequential.md
- MCP_Serena.md
- MCP_Mindbase.md (deprecated)
- __init__.py

**MCP1 Status - Deprecated Files:**
- ✅ MCP_Mindbase.md: `<deprecated>Standalone mindbase is deprecated. Use airis-mcp-gateway instead`
- ✅ MCP_Airis-Agent.md: `<deprecated>Standalone airis-agent is deprecated. Use airis-mcp-gateway instead`

**MCP5 Status - Version accuracy:**
- Context7.md: No version tag found
- Sequential.md: No version tag found
- Tavily.md: No version tag found (has config_req for API key)
- Others: No version tags found

**MCP6 Status - Standardization:**
- All MCPs use: <component name="..." type="mcp"> format
- All have: <config>, <role>, <choose>, <synergy>, etc.
- Consistent XML structure across all files

**MCP7 Status - README.md:**
- No README.md found in mcp/ directory
- __init__.py present but no overview doc

**Status:** MCP1 ✅, MCP5 no versions, MCP6 ✅ consistent, MCP7 no README

---

### 9. Scripts directory (S2)

**All scripts present:**
```
__init__.py
clean_command_names.py
token_estimator.py
session_init.py
prettier_hook.py
skill_activator.py
context_reset.py (verified)
context_loader.py
validate_confidence_context.py
skill_watcher.py
(+ shell scripts in original listing: skill-activator.sh, session-init.sh)
```

**context_reset.py review:**
- Purpose: Reset context_loader cache for /clear and /compact
- Mechanism: Deletes dedup cache file to force re-injection of dynamic contexts
- Cache location: ~/.claude/.superclaude_hooks/
- Implementation: MD5 hash of cwd + 8-char session ID
- Status: ✅ S2 verified, implementation sound

**Status:** ✅ All scripts present, context_reset.py documented

---

### 10. Core: RESEARCH_CONFIG.md (C13)

**Configuration keys present:**

Defined keys (used):
- planning: unified|intent-planning|planning-only
- max_hops: 5
- confidence: 0.7
- memory: true
- parallel: true
- hop_config: max, timeout, parallel, loop_detect
- confidence.weights: relevance, completeness
- reflection.freq: after_each_hop
- tool_routing: tavily, playwright, sequential, context7, serena

**Aspirational/undefined keys (C13 STATUS):**
- `credentials:` - mentioned in tool_routing but not fully defined
- `fallback_chains:` - implied in tool_routing but not explicit section
- `rate_limit:` - mentioned in parallel_rules but not config section
- `cache_policy:` - optimization section mentions cache but no policy definition

**Status:** C13 - Some aspirational keys exist, some need definition

---

## SUMMARY TABLE

| Wave | Target | Finding | Status |
|------|--------|---------|--------|
| 6 | SK1 | @deprecated annotation in SKILL.md | ✅ Clean |
| 6 | SK2 | disable-model-invocation field | ⚠️ Not found |
| 6 | H1 | TeammateIdle/TaskCompleted hooks | ✅ Present |
| 6 | H3 | Async hook support docs | ❌ None found |
| 7 | A4 | color field in agents | ❌ None found (0/20) |
| 7 | A5 | negative examples in agents | ✅ All present |
| 7 | A6 | autonomy field in agents | ❌ None found (0/20) |
| 7 | A7 | cross-refs to commands | ⚠️ Minimal (MCP refs only) |
| 7 | CMD5 | index vs index-repo relationship | ✅ Clear |
| 7 | CMD6 | internal section ordering | ✅ Consistent |
| 7 | M2 | deprecated symbol mappings | ✅ Documented |
| 7 | M4 | modes/ README.md | ❌ Missing |
| 7 | MCP1 | deprecated MCP files | ✅ Both marked |
| 7 | MCP5 | version accuracy | ❌ No versions |
| 7 | MCP6 | standardization | ✅ Consistent |
| 7 | MCP7 | mcp/ README.md | ❌ Missing |
| 7 | S2 | context_reset.py | ✅ Verified |
| 7 | C13 | undefined config keys | ⚠️ Some aspirational |

---

## KEY INSIGHTS

1. **Agent Structure Stable:** All 20 agents use consistent YAML frontmatter with `memory: user`
2. **Negative Examples Universal:** All agents have bounds/tool_guidance with "Never" sections
3. **Command Ordering Consistent:** Clear XML structure pattern across all commands
4. **MCP Files Deprecation Clear:** Mindbase + Airis-Agent properly marked with links to gateway
5. **Hooks Experimental Status:** TeammateIdle/TaskCompleted clearly marked as experimental (v2.1.33)
6. **Documentation Gaps:** No README files in modes/ or mcp/ directories
7. **Field Additions Needed:** autonomy + color fields missing from all agent files
8. **Context Reset Implementation:** Solid hash-based cache management with TTL

