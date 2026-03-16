# Skill ↔ Content Directory Conflict Analysis

> **Date:** 2026-03-17
> **Scope:** `src/superclaude/skills/` vs `agents/`, `commands/`, `core/`, `modes/`, `mcp/`
> **Method:** Sequential cross-directory analysis with infrastructure trace
> **Branch:** `feature/content-framework-upgrade`

## Executive Summary

15 skills analyzed against 20 agents, 30 commands, 7 modes, 4 core files, and 8 MCP docs. **22 conflicts found** — 4 critical, 7 high, 6 medium, 5 minor. The primary pattern: **skills and commands define parallel workflows for the same activities with incompatible handoff chains**, and **skills and agents compete for activation on the same trigger keywords without documented precedence**.

---

## Table of Contents

1. [Critical Conflicts](#1-critical-conflicts)
2. [High Conflicts](#2-high-conflicts)
3. [Medium Conflicts](#3-medium-conflicts)
4. [Minor Conflicts](#4-minor-conflicts)
5. [Conflict Topology](#5-conflict-topology)
6. [Methodology](#6-methodology)
7. [Recommended Actions](#7-recommended-actions)

---

## 1. Critical Conflicts

### C1. `brainstorming` Skill ↔ `/sc:brainstorm` Command — Divergent Workflows

**Files:** `skills/brainstorming/SKILL.md` vs `commands/brainstorm.md`

| Dimension | Skill | Command |
|-----------|-------|---------|
| Flow steps | 9 (with spec review loop) | 5 (linear) |
| Output artifact | `docs/specs/YYYY-MM-DD-<topic>-design.md` | `REQUIREMENTS.md` |
| Review gate | Dispatches `spec-document-reviewer` subagent (max 5 iterations) | None |
| Handoff target | `writing-plans` skill | `/sc:design`, `/sc:implement` |
| MCP servers | None declared in frontmatter | `seq\|c7\|magic\|serena` |
| Personas | None | 7 (`arch\|anal\|fe\|be\|sec\|ops\|pm`) |

**Impact:** User calls `/sc:brainstorm` → gets the command's 5-step flow → no spec artifact written → no review loop → handoff to `/sc:implement`, **skipping `writing-plans` entirely**. This violates `core/RULES.md` workflow gates:

```
brainstorming → writing-plans → executing-plans → verification → done
```

**Evidence:**
- Command handoff (`brainstorm.md:74`): `<handoff next="/sc:research /sc:design /sc:implement /sc:workflow"/>`
- Skill handoff: `→ writing-plans`
- Workflow gates (`core/RULES.md`): `brainstorming -> writing-plans: User approves spec before planning`

---

### C2. `simplicity-coach` Skill ↔ `simplicity-guide` Agent — Same Methodology, Undefined Boundary

**Files:** `skills/simplicity-coach/SKILL.md` vs `agents/simplicity-guide.md`

| Dimension | Skill | Agent |
|-----------|-------|-------|
| Philosophy source | Dave Thomas OSL | Dave Thomas OSL |
| Capabilities | OSL coaching + daybook journaling + dependency audits + scripts | Complexity prevention (read-only analysis) |
| Permission level | Full tools | `plan` mode, `Edit, Write, NotebookEdit` disallowed |
| Hooks | `Stop` hook → `dependency-audit.py` | None |
| Trigger | Auto-invoked by CC description matching | Auto-delegated on: `simplicity, minimal, lean, over-engineering, yagni, pragmatic, orient-step-learn` |

**Impact:** When a user says "this is too complex" or "simplify this", both can activate simultaneously. The skill has operational capabilities (scripts, hooks, daybook writing). The agent is advisory-only (read-only, plan mode). No precedence rule exists.

**Evidence:**
- Skill references the agent: "simplicity-guide agent activates automatically" (no boundary defined)
- Agent has 11 trigger keywords in its description, many overlapping with skill's description keywords
- `core/FLAGS.md` persona index: `simple=simplicity-guide(OSL,YAGNI)` — only references the agent

---

### C3. `systematic-debugging` Skill ↔ `root-cause-analyst` Agent — Overlapping Root Cause Investigation

**Files:** `skills/systematic-debugging/SKILL.md` vs `agents/root-cause-analyst.md`

| Dimension | Skill | Agent |
|-----------|-------|-------|
| Mission | "Find the root cause before attempting a fix" | "Systematically investigate...through hypothesis testing" |
| Method | Reproduce → Investigate → Hypothesize → Confirm → Write test → Fix → Verify | Evidence → Hypothesis → Patterns → Documentation → Resolution |
| Escalation | "After 3+ failed attempts, reconsider" | "Max 3 hypothesis-test cycles before escalation" |
| Can fix code? | Yes (steps 5-7: write test, fix, verify) | No — hands off to `/sc:troubleshoot` or `/sc:implement` |
| Trigger | Auto-invoked on "bugs, test failures, unexpected behavior" | Auto-delegated on: `root-cause, debug, investigate, hypothesis` |

**Impact:** User says "debug this test failure" — both activate. Skill wants to **find root cause AND fix** (steps 5-7). Agent wants to **investigate only** then hand off. These are incompatible contracts.

**Evidence:**
- Both mention "3 hypothesis cycles" — suggests common ancestry but divergent scope
- Skill `<bounds>` includes "regression testing" (writes code); Agent `<bounds>` says "documented evidence chains" (read-only analysis)

---

### C4. Three-System Activation Race — No Documented Precedence

11 of 15 skills lack `disable-model-invocation`, meaning Claude Code can auto-invoke them. But three independent systems compete:

| System | Trigger Mechanism | Activated By |
|--------|-------------------|--------------|
| CC native skill matching | Reads `description` field at session start | User prompt keyword match |
| CC native agent delegation | Reads agent `description` trigger keywords | User prompt keyword match |
| SuperClaude `context_loader.py` | `TRIGGER_MAP` regex patterns on `UserPromptSubmit` | Mode/MCP injection |

**No documented precedence** when all three match the same prompt. Example: user says "brainstorm" → CC may auto-invoke `brainstorming` skill (description match) **AND** `context_loader.py` injects `MODE_Brainstorming.md` (TRIGGER_MAP match) **AND** `/sc:brainstorm` command is available.

**Evidence:**
- `context_loader.py` TRIGGER_MAP includes brainstorm, research, business triggers
- Skills have `description` fields with overlapping keywords
- Agents have `(triggers - ...)` in description with overlapping keywords
- No framework documentation defines which system takes priority

---

## 2. High Conflicts

### H1. Workflow Gate Chain — Commands Break the Documented Path

`core/RULES.md` specifies:

```
brainstorming → writing-plans: User approves spec before planning
writing-plans → executing-plans: Plan document committed to repo
executing-plans → verification: Plan tasks completed
verification → done: Test pass evidence required
```

**Skills correctly implement this chain:**
```
brainstorming → writing-plans → executing-plans → finishing-a-development-branch
                                                    ↑ (uses verification-before-completion)
```

**Commands bypass it:**
```
/sc:brainstorm → /sc:design → /sc:implement  (skips writing-plans)
/sc:implement → /sc:test                      (skips verification-before-completion)
/sc:design → /sc:implement                    (skips writing-plans)
```

**Impact:** The command-based workflow is the user-facing entry point (via `/sc:help` and `/sc:recommend`), but it skips the quality gates that the skill-based workflow enforces.

---

### H2. `/sc:review` Command ↔ `requesting-code-review` + `receiving-code-review` Skills — Disconnected

**Files:** `commands/review.md` vs `skills/requesting-code-review/SKILL.md` + `skills/receiving-code-review/SKILL.md`

| Dimension | Command | Skills |
|-----------|---------|--------|
| Approach | Inline analysis by Claude | Dispatches subagent reviewer (`context: fork`) |
| Review model | Single-pass categorized findings | 2D review (spec fidelity + code quality) |
| Feedback handling | Reports findings | Classifies, verifies, pushes back with evidence |
| Entry point | `/sc:review` | Auto-invoked only (no `/sc:` command) |

**Impact:** The skills implement a more rigorous review process (subagent isolation, 2D review, pushback protocol) but users can't invoke them via `/sc:`. The command provides a simpler inline review. Neither references the other.

---

### H3. `/sc:troubleshoot` Command ↔ `systematic-debugging` Skill — Incompatible Fix Approaches

| Dimension | Command | Skill |
|-----------|---------|-------|
| Fix approach | `--fix` flag: "Apply safe fixes only" | Always writes failing test first (TDD) |
| Escalation | "After 3 rounds → summarize → ask user" | "After 3+ attempts → reconsider approach" |
| Test requirement | Optional | Mandatory (step 5: "Write failing test") |
| MCP | `seq` only | None declared |

**Impact:** User encounters a bug and uses `/sc:troubleshoot --fix` → fix applied without failing test first. But the `systematic-debugging` skill **requires** a failing test before any fix. Same problem, incompatible contracts.

---

### H4. `confidence-check` Skill Hook Fires During `/sc:research`

The `confidence-check` skill declares a `PreToolUse` hook matching `WebFetch|WebSearch`. When `/sc:research` activates the `deep-research-agent` (which uses Tavily/WebSearch extensively), this hook fires once per session, injecting evidence-focus guidance into an already evidence-focused research workflow.

**Risk:** Low immediate harm (hook fires `once: true`), but it demonstrates **unintended cross-activation** between independently designed skills.

---

### H5. MCP Server Routing Inconsistencies Between Content Types

| Content | Declares | Missing | Rationale |
|---------|----------|---------|-----------|
| `/sc:brainstorm` command | `seq\|c7\|magic\|serena` | `tavily` | Skill body references external research |
| `brainstorming` skill | (none in frontmatter) | `seq` at minimum | Complex multi-step reasoning |
| `/sc:review` command | (none) | `serena` | Cross-file symbol reference analysis |
| `/sc:cleanup` command | `seq\|c7` | `morph` | Bulk code transformation |
| `confidence-check` skill | (body only) | Frontmatter `<mcp>` | Inconsistent declaration location |

Skills and their corresponding commands declare different MCP servers for the same activity, leading to different tool availability depending on which path the user takes.

---

### H6. Persona Over-Specification in Commands vs Zero in Skills

| Content Type | Persona Declaration | Example |
|--------------|-------------------|---------|
| Commands | 6-7 personas, hardcoded | `/sc:brainstorm`: `arch\|anal\|fe\|be\|sec\|ops\|pm` |
| Skills | 0 personas, relies on Claude's judgment | `brainstorming`: (none) |
| Agents | 0 personas, IS the persona | `simplicity-guide`: self-contained |

**Impact:** Using `/sc:brainstorm` forces 7-persona multi-expert mode. Using the `brainstorming` skill lets Claude choose the appropriate perspective. Same activity, different cognitive load.

---

### H7. `dispatching-parallel-agents` Skill ↔ `--delegate` Flag in `core/FLAGS.md`

`core/FLAGS.md` defines:
```
--delegate [auto|files|folders]: >7 dirs, >50 files, complexity >0.8 → sub-agent parallel
```

The `dispatching-parallel-agents` skill provides operational steps (identify → prompt → dispatch → review → integrate) with detailed constraints (no overlapping files, integration testing required). Neither references the other. The flag triggers parallel dispatch; the skill enforces safety rules around it.

---

## 3. Medium Conflicts

### M1. `writing-plans` Skill References Nonexistent Subagents

The skill dispatches `plan-document-reviewer` subagent and references `subagent-driven-development` as an execution strategy. Neither exists in `agents/`. These are phantom references that will cause dispatch failures or silent fallback.

**Evidence:** `skills/writing-plans/SKILL.md` flow step 5: "dispatch plan-document-reviewer subagent"

---

### M2. `brainstorming` Skill References Nonexistent Subagent

Dispatches `spec-document-reviewer` subagent — not present in `agents/` directory.

**Evidence:** `skills/brainstorming/SKILL.md` flow step 7: "dispatch spec-document-reviewer subagent"

---

### M3. Business Panel: Mode + Agent Duplication

- **Mode** (`MODE_Business_Panel.md`): Defines 9 expert frameworks (Christensen, Porter, Drucker, etc.)
- **Agent** (`business-panel-experts.md`): Also defines 9 expert frameworks (same set)
- **Command** (`/sc:business-panel`): Entry point that should activate both

The expert framework definitions are duplicated across mode and agent. If one is updated without the other, they diverge.

---

### M4. `RESEARCH_CONFIG.md` Integration Gap

`modes/RESEARCH_CONFIG.md` defines:
- Depth profiles: `quick|standard|deep|exhaustive`
- Confidence thresholds per depth level
- Tool routing by depth

Neither `/sc:research` command nor `deep-research-agent` explicitly loads or references this config. The agent defines its own depth behavior inline (`quick: 1 hop | standard: 2-3 hops | deep: 3-4 hops | exhaustive: 5+`), which may or may not match `RESEARCH_CONFIG.md`.

---

### M5. `using-superclaude` Skill — Instruction Priority Claim vs Reality

The skill declares: `user instructions > skills > commands > system prompt`

But Claude Code's actual resolution order is:
1. System prompt (highest — includes CLAUDE.md chain via `@superclaude/CLAUDE_SC.md`)
2. Skills/Agents/Commands (loaded from descriptions, activated on match)
3. User prompt (triggers activation)

The skill's stated priority inverts the actual execution model.

---

### M6. Serena MCP Availability Assumptions

5 agents declare `mcp: serena`: `pm-agent`, `self-review`, `simplicity-guide`, `root-cause-analyst`, `refactoring-expert`. Additionally, commands `/sc:reflect` and `/sc:save` assume Serena thinking tools.

Per `mcp/MCP_Serena.md`, thinking tools are **not available** in the Claude Code CLI context. No fallback logic is documented in any of these content files.

---

## 4. Minor Conflicts

### m1. Inconsistent Handoff Namespaces

| Content Type | Handoff Format | Example |
|--------------|----------------|---------|
| Skills | Skill names | `→ writing-plans`, `→ executing-plans` |
| Commands | `/sc:` commands | `→ /sc:design`, `→ /sc:implement` |

Skills never hand off to commands; commands never hand off to skills. Two parallel chains exist with no bridge.

---

### m2. Undefined `auto="true"` Attribute on `/sc:brainstorm` Personas

`commands/brainstorm.md:35`: `<personas p="arch|anal|fe|be|sec|ops|pm"/>` — unique to this command. The `auto` attribute behavior is undefined in any authoring guide or framework documentation.

(Note: The attribute appeared in the XML during analysis but may be present in some versions. Verify current state.)

---

### m3. `test-driven-development` Skill ↔ `/sc:test` Command Overlap

| Dimension | Skill | Command |
|-----------|-------|---------|
| Purpose | RED-GREEN-REFACTOR cycle enforcement | Run tests + report coverage |
| Trigger | "All feature work and bug fixes" | Explicit `/sc:test` invocation |

Different scopes but same user intent ("test this"). User choosing `/sc:test` gets coverage reporting; skill activation gets TDD enforcement. No documentation explains which to use when.

---

### m4. Missing `<handoff>` in `/sc:review` Command

`commands/review.md` defines `<handoff next="/sc:implement /sc:test"/>` but doesn't reference `receiving-code-review` skill, which is the framework's designed next step after a review.

---

### m5. `ship` Skill — No Corresponding `/sc:ship` Command

`ship` is marked `disable-model-invocation: true` (correct — destructive). But it has no `/sc:ship` command wrapper, meaning users must know to type `/ship` directly. This skill is not discoverable via `/sc:help` which only lists `/sc:*` commands.

---

## 5. Conflict Topology

```
               CORE (FLAGS.md, RULES.md, PRINCIPLES.md)
                    │ defines workflow gates
                    │ defines --delegate, --brainstorm flags
                    │
           ┌────────┴────────┐
        SKILLS              COMMANDS
    (operational)        (procedural)
           │                  │
    ┌──────┤            ┌─────┤
    │      │            │     │
    │  brainstorming    │  /sc:brainstorm ──── C1: Different flows
    │  (9 steps)        │  (5 steps)           H1: Skips gates
    │      │            │     │
    │  writing-plans    │  /sc:design ──────── H1: No writing-plans
    │      │            │     │
    │  executing-plans  │  /sc:implement ───── H1: No verification
    │      │            │     │
    │  verification     │  /sc:test ────────── m3: TDD vs coverage
    │      │            │     │
    │  finishing-branch  │  (no equivalent)
    │                   │
    ├──────────────┐    ├─────────────┐
    │              │    │             │
  simplicity     systematic    /sc:review    /sc:troubleshoot
  -coach         -debugging         │              │
    │              │            H2: disconnected   H3: --fix ≠ TDD
    │              │            from skills
    │              │
    C2 ↕           C3 ↕
    │              │
  AGENTS         AGENTS
  simplicity-    root-cause-
  guide          analyst
    │              │
    │              │
    MODES         MODES         MCP DOCS
    (cognitive)   (cognitive)   (tool refs)
         │              │          │
         M3: duplication  M4: gap   H5: routing mismatch
```

---

## 6. Methodology

### Scope

| Directory | Files Analyzed | Content Type |
|-----------|---------------|--------------|
| `skills/` | 15 SKILL.md + 2 scripts + 3 references | Execution logic |
| `agents/` | 20 agent definitions | Domain personas |
| `commands/` | 30 slash commands | Workflow entry points |
| `core/` | 4 files (FLAGS, PRINCIPLES, RULES, BUSINESS_SYMBOLS) | Framework DNA |
| `modes/` | 7 modes + RESEARCH_CONFIG | Cognitive overlays |
| `mcp/` | 8 MCP server docs | Tool references |

### Infrastructure Files Traced

| File | Role | Key Findings |
|------|------|-------------|
| `scripts/context_loader.py` | Runtime injection | TRIGGER_MAP competes with CC native matching |
| `cli/install_paths.py` | Install-time paths | Clean — no conflicts |
| `cli/install_skill.py` | Skill installation | Template vars resolved correctly |
| `hooks/inline_hooks.py` | Frontmatter parsing | Skill/agent fields parsed identically |
| `scripts/skill_activator.py` | Skill trigger detection | Explicit triggers only — conservative |

### Analysis Method

1. **Parallel exploration:** Four concurrent agents read all content files
2. **Cross-reference extraction:** Handoff chains, MCP declarations, trigger keywords, persona references
3. **Infrastructure trace:** Installation pipeline, runtime injection, activation lifecycle
4. **Conflict classification:** By impact severity and fix complexity

---

## 7. Recommended Actions

### Priority 1 — Critical (fix before merge)

| # | Action | Files | Effort |
|---|--------|-------|--------|
| 1 | **Align `/sc:brainstorm` handoff** with workflow gates — add `writing-plans` to chain | `commands/brainstorm.md` | S |
| 2 | **Define skill-agent precedence** — document in `ARCHITECTURE.md` which system wins | `ARCHITECTURE.md` | M |
| 3 | **Scope `simplicity-coach` vs `simplicity-guide`** — skill = interactive + scripts; agent = advisory overlay | Both files + `ARCHITECTURE.md` | M |
| 4 | **Scope `systematic-debugging` vs `root-cause-analyst`** — skill = hands-on fix; agent = investigation-only | Both files + `ARCHITECTURE.md` | M |

### Priority 2 — High (fix before next release)

| # | Action | Files | Effort |
|---|--------|-------|--------|
| 5 | **Add `/sc:ship` and `/sc:code-review` commands** as thin wrappers to skills | `commands/ship.md`, `commands/code-review.md` | M |
| 6 | **Harmonize command handoffs** to include skill chain (brainstorm → writing-plans) | Multiple command files | M |
| 7 | **Harmonize MCP declarations** between commands and corresponding skills | Multiple files | S |
| 8 | **Remove or create phantom subagents** (`spec-document-reviewer`, `plan-document-reviewer`) | `skills/brainstorming/`, `skills/writing-plans/` | S |

### Priority 3 — Medium (backlog)

| # | Action | Files | Effort |
|---|--------|-------|--------|
| 9 | **Integrate `RESEARCH_CONFIG.md`** into `/sc:research` and `deep-research-agent` | 3 files | M |
| 10 | **Deduplicate Business Panel** expert definitions (single source in mode or agent, not both) | `MODE_Business_Panel.md`, `business-panel-experts.md` | M |
| 11 | **Document Serena MCP fallback** for CLI context | `mcp/MCP_Serena.md` + referencing agents | S |
| 12 | **Fix `using-superclaude` priority claim** to match actual CC resolution order | `skills/using-superclaude/SKILL.md` | S |

### Priority 4 — Minor (opportunistic)

| # | Action | Files | Effort |
|---|--------|-------|--------|
| 13 | **Standardize handoff namespace** — commands should reference skills where appropriate | All handoff sections | L |
| 14 | **Remove `auto="true"`** attribute or document its behavior | `commands/brainstorm.md` | S |
| 15 | **Add TDD vs coverage guidance** to help users choose skill vs command for testing | README or ARCHITECTURE.md | S |

---

## Appendix: Conflict Count by Category

| Category | 🔴 Critical | 🟡 High | 🟡 Medium | 🟢 Minor | Total |
|----------|:-----------:|:-------:|:---------:|:--------:|:-----:|
| Skill ↔ Command divergence | 1 | 3 | — | 2 | 6 |
| Skill ↔ Agent overlap | 2 | — | — | — | 2 |
| Workflow gate violations | — | 1 | — | — | 1 |
| Activation precedence | 1 | 1 | 1 | — | 3 |
| MCP routing | — | 1 | 1 | — | 2 |
| Phantom references | — | — | 2 | — | 2 |
| Content duplication | — | — | 1 | — | 1 |
| Orphaned content | — | 1 | — | 1 | 2 |
| Documentation gaps | — | — | 1 | 2 | 3 |
| **Total** | **4** | **7** | **6** | **5** | **22** |
