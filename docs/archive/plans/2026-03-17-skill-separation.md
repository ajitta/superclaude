# Skill Separation Implementation Plan

> **For agentic workers:** REQUIRED: Use subagent-driven-development (if subagents available) or executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce skills from 15 to 4 by migrating workflow content to commands/core and deleting redundant skills, eliminating 22 conflicts.

**Architecture:** Skills retain ONLY CC-native capabilities (hooks, disable-model-invocation, allowed-tools, scripts). Workflow procedures move to commands. Cross-cutting principles move to core/RULES.md.

**Tech Stack:** Markdown (XML components), Python (test updates), YAML frontmatter

**Analysis:** `docs/analysis/2026-03-17-skill-content-conflict-analysis.md`

---

## Migration Map

| Skill | Action | Target | Reason |
|-------|--------|--------|--------|
| confidence-check | **KEEP** | — | PreToolUse hook + script |
| simplicity-coach | **KEEP** | — | Stop hook + script + references |
| ship | **KEEP** | — | disable-model-invocation |
| finishing-a-development-branch | **KEEP** | — | disable-model-invocation + allowed-tools |
| brainstorming | **→ CMD** | Enhance `/sc:brainstorm` | Workflow procedure |
| writing-plans | **→ CMD** | New `/sc:plan` | Workflow procedure |
| executing-plans | **→ CMD** | Enhance `/sc:implement` | Workflow procedure |
| systematic-debugging | **→ CMD** | Enhance `/sc:troubleshoot` | Workflow procedure |
| test-driven-development | **→ CMD** | Enhance `/sc:test` | Workflow procedure |
| requesting-code-review | **→ CMD** | Enhance `/sc:review` | Workflow procedure |
| receiving-code-review | **→ CMD** | Enhance `/sc:review` | Workflow procedure |
| verification-before-completion | **→ CORE** | Enhance `core/RULES.md` | Cross-cutting principle |
| using-superclaude | **→ CORE** | Enhance `ARCHITECTURE.md` | Meta-guidance |
| dispatching-parallel-agents | **DELETE** | — | Redundant with FLAGS.md --delegate |
| using-git-worktrees | **DELETE** | — | Redundant with CC built-in worktree |

---

## Chunk 1: Create /sc:plan Command

> From: `skills/writing-plans/SKILL.md` (68 lines)
> To: `commands/plan.md` (new file)

### Task 1: Create /sc:plan command

**Files:**
- Create: `src/superclaude/commands/plan.md`

- [ ] **Step 1: Write the command file**

```markdown
---
description: Create detailed implementation plans with TDD tasks, exact file paths, and verification commands
---
<component name="plan" type="command">

  <role>
    /sc:plan
    <mission>Create detailed implementation plans with TDD tasks, exact file paths, and verification commands</mission>
  </role>

  <syntax>/sc:plan [spec-or-topic] [--from docs/specs/...] [--output docs/plans/...]</syntax>

  <flow>
    1. Load: Read spec or requirements (from --from path or user description)
    2. Map: List files to create/modify and their responsibilities
    3. Decompose: Break into tasks — each is a single action (2-5 min), checkbox syntax, exact paths, complete code
    4. Template: Add plan header (goal, architecture, tech stack)
    5. Save: Write to docs/plans/YYYY-MM-DD-<feature-name>.md
    6. Handoff: Ready for /sc:implement --plan
  </flow>

  <outputs note="Per execution">
  | Artifact | Purpose |
  |----------|---------|
  | `docs/plans/YYYY-MM-DD-<name>.md` | Implementation plan with TDD tasks |
  </outputs>

  <mcp servers="seq|c7"/>
  <personas p="arch|anal"/>

  <tools>
    - Read: Spec and codebase analysis
    - Grep/Glob: File structure mapping
    - Write: Plan document creation
  </tools>

  <templates note="Included in plan output">
Plan header:
  # [Feature] Implementation Plan
  **Goal:** [One sentence]
  **Architecture:** [2-3 sentences]
  **Tech Stack:** [Key technologies]

Task format:
  ### Task N: [Component]
  **Files:** Create: path | Modify: path:lines | Test: path
  - [ ] Step 1: Write failing test
  - [ ] Step 2: Verify it fails
  - [ ] Step 3: Write minimal implementation
  - [ ] Step 4: Verify it passes
  - [ ] Step 5: Commit
  </templates>

  <examples>
  | Input | Output |
  |-------|--------|
  | `/sc:plan --from docs/specs/2026-03-17-auth-design.md` | TDD plan from spec |
  | `/sc:plan 'add user profiles'` | Plan from description |
  | `/sc:plan --from REQUIREMENTS.md --output docs/plans/profiles.md` | Custom output path |
  </examples>

  <token_note>Medium consumption — scales with spec complexity</token_note>

  <bounds will="plan creation|task decomposition|file mapping|TDD structure" wont="write implementation code|execute tasks|skip spec review" fallback="Ask user for spec clarification when requirements are ambiguous"/>

  <handoff next="/sc:implement /sc:brainstorm"/>
</component>
```

- [ ] **Step 2: Verify command structure**
```bash
uv run pytest tests/unit/test_command_structure.py -v -k "plan"
```

---

## Chunk 2: Enhance Existing Commands (brainstorm, implement, troubleshoot)

### Task 2: Enhance /sc:brainstorm — add spec output and correct handoff

**Files:**
- Modify: `src/superclaude/commands/brainstorm.md`

Key changes from brainstorming skill:
- Add spec artifact output (`docs/specs/YYYY-MM-DD-<topic>-design.md`)
- Fix handoff chain to include `/sc:plan` (restores workflow gate)
- Add approval gate in flow before handoff

- [ ] **Step 1: Update flow to include spec writing and approval gate**

Replace flow (lines 13-19):
```xml
  <flow>
    1. Explore: Socratic dialogue + systematic questioning
    2. Analyze: Multi-persona coordination + domain expertise
    3. Validate: Feasibility assessment + requirement validation
    4. Specify: Write spec to docs/specs/YYYY-MM-DD-<topic>-design.md
    5. Approve: Present spec for user review — do not proceed without confirmation
    6. Handoff: Route to /sc:plan for implementation planning
  </flow>
```

- [ ] **Step 2: Update outputs table**

Replace outputs (lines 21-26):
```xml
  <outputs note="Per execution">
| Artifact | Purpose |
|----------|---------|
| `docs/specs/YYYY-MM-DD-<topic>-design.md` | Design specification document |
| Conversation output | Socratic dialogue + validated requirements |
  </outputs>
```

- [ ] **Step 3: Fix handoff to restore workflow gate chain**

Replace handoff (line 74):
```xml
  <handoff next="/sc:plan /sc:design /sc:research"/>
```

- [ ] **Step 4: Verify**
```bash
uv run pytest tests/unit/test_command_structure.py -v -k "brainstorm"
```

---

### Task 3: Enhance /sc:implement — add plan-aware mode

**Files:**
- Modify: `src/superclaude/commands/implement.md`

Key changes from executing-plans skill:
- Add --plan flag for plan-loading mode
- Add plan-aware flow steps (load plan → execute tasks → verify each)

- [ ] **Step 1: Update syntax to include --plan flag**

Replace syntax (line 11):
```xml
  <syntax>/sc:implement [feature] [--plan docs/plans/...] [--type component|api|service|feature] [--framework react|vue|express] [--safe] [--with-tests]</syntax>
```

- [ ] **Step 2: Update flow to include plan-aware path**

Replace flow (lines 13-19):
```xml
  <flow>
    1. Load: If --plan provided, read plan document and extract tasks; otherwise analyze requirements + tech context
    2. Plan: Approach + activate personas; for plan mode, follow task order exactly
    3. Checkpoint: If changes affect >3 files → present numbered plan → wait for user approval before editing
    4. Execute: Code + framework best practices; for plan mode, mark tasks complete as you go
    5. Validate: Security + quality checks; run verification command per task
    6. Integrate: Docs + testing recs; report any blockers encountered
  </flow>
```

- [ ] **Step 3: Verify**
```bash
uv run pytest tests/unit/test_command_structure.py -v -k "implement"
```

---

### Task 4: Enhance /sc:troubleshoot — add systematic debugging method

**Files:**
- Modify: `src/superclaude/commands/troubleshoot.md`

Key changes from systematic-debugging skill:
- Mandatory reproduce step
- Test-before-fix requirement when --fix is used
- Explicit 3-hypothesis limit

- [ ] **Step 1: Update flow to include reproduce and test-before-fix**

Replace flow (lines 13-19):
```xml
  <flow>
    1. Reproduce: Confirm failure — read full error, identify exact trigger, verify it's consistent
    2. Investigate: Check git log/diff, trace data flow, find working examples
    3. Hypothesize: Form specific hypothesis ("X causes Y because Z") — max 3 cycles before escalating to user
    4. Confirm: Test hypothesis by changing one variable at a time; check environment before code
    5. Test: Write failing test that reproduces the exact bug (required before any fix)
    6. Fix: Apply single change addressing root cause — no "while I'm here" fixes
    7. Verify: Failing test passes, all existing tests pass, no regressions
  </flow>
```

- [ ] **Step 2: Verify**
```bash
uv run pytest tests/unit/test_command_structure.py -v -k "troubleshoot"
```

---

## Chunk 3: Enhance Commands (test, review)

### Task 5: Enhance /sc:test — add TDD mode

**Files:**
- Modify: `src/superclaude/commands/test.md`

Key changes from test-driven-development skill:
- Add --tdd flag for RED-GREEN-REFACTOR cycle
- One behavior per test rule
- Refactor only when green

- [ ] **Step 1: Update syntax**

Replace syntax (line 11):
```xml
  <syntax>/sc:test [target] [--type unit|integration|e2e|all] [--tdd] [--coverage] [--watch] [--fix]</syntax>
```

- [ ] **Step 2: Add TDD pattern to patterns section**

Replace patterns (lines 40-45):
```xml
  <patterns>
    - Discovery: Pattern categorization → runner selection
    - Coverage: Metrics → comprehensive reporting
    - E2E: Browser automation → cross-platform validation
    - Watch: File monitoring → continuous execution
    - TDD (--tdd): RED (write one failing test) → GREEN (simplest code to pass) → REFACTOR (clean up under green) → repeat
  </patterns>
```

- [ ] **Step 3: Add TDD example**

Add after line 54 (inside examples table):
```
| `--tdd src/auth/` | RED-GREEN-REFACTOR cycle for auth module |
```

- [ ] **Step 4: Verify**
```bash
uv run pytest tests/unit/test_command_structure.py -v -k "test"
```

---

### Task 6: Enhance /sc:review — add structured review dispatch and feedback processing

**Files:**
- Modify: `src/superclaude/commands/review.md`

Key changes from requesting-code-review + receiving-code-review skills:
- 2D review model (spec fidelity + code quality)
- Structured feedback processing (classify → verify → implement/pushback)
- Agent dispatch for isolated review

- [ ] **Step 1: Update flow to include 2D review and feedback processing**

Replace flow (lines 14-21):
```xml
  <flow>
    1. Scope: Determine review range — PR number, git diff, specific files, or branch comparison
    2. Gather: Read all changed files, identify spec/plan if exists (docs/specs/ or docs/plans/)
    3. Review-2D: Dimension 1 (spec fidelity) — does code match what was planned? Dimension 2 (code quality) — correctness, security, edge cases, test coverage. When no spec exists, weight shifts to Dimension 2
    4. Categorize: Group findings as Critical (must fix) | Important (should fix) | Suggestion (nice to have)
    5. Verify: Run tests and linting on changed code to confirm findings
    6. Process: For each finding — classify (change request vs concern vs question) → verify against codebase → implement fix or push back with evidence
  </flow>
```

- [ ] **Step 2: Add dispatch tool and structured output**

Replace tools (lines 31-36):
```xml
  <tools>
    - Grep: Search for patterns across changed files
    - Read: Examine file contents and context
    - Bash: Run tests and linting commands
    - Agent: Dispatch isolated reviewer subagent for large reviews (context: fork)
  </tools>
```

- [ ] **Step 3: Add pushback examples**

Add after the existing examples table (line 43):
```xml
  <example name="pushback-protocol" type="info">
    When a review finding is incorrect, push back with evidence:
    - "This breaks test_X because [reason]. See [file:line]"
    - "Module B uses [different pattern]. Not applicable here."
    - "No current consumer for this abstraction. Deferring per YAGNI."
  </example>
```

- [ ] **Step 4: Update handoff**

Replace handoff (line 48):
```xml
  <handoff next="/sc:implement /sc:test /sc:troubleshoot"/>
```

- [ ] **Step 5: Verify**
```bash
uv run pytest tests/unit/test_command_structure.py -v -k "review"
```

---

## Chunk 4: Migrate to Core

### Task 7: Add verification principles to core/RULES.md

**Files:**
- Modify: `src/superclaude/core/RULES.md`

Key changes from verification-before-completion skill:
- Add verification rule to core_rules section
- Update workflow_gates to reference commands instead of skills

- [ ] **Step 1: Add verification rule to core_rules (after line 38 "Clarification")**

Add new rule:
```
Verification 🔴: before claiming done, run full test suite fresh (not cached); compare pass count to baseline; cite evidence ("42/42 pass, baseline 40")
```

- [ ] **Step 2: Update workflow_gates to reference commands**

Replace workflow_gates (lines 72-77):
```xml
  <workflow_gates note="Recommended workflow chain">
    /sc:brainstorm -> /sc:plan: User approves spec before planning
    /sc:plan -> /sc:implement --plan: Plan document committed to repo
    /sc:implement -> /sc:test: Implementation complete
    /sc:test -> done: Test pass evidence required (actual output, not claims)
  </workflow_gates>
```

- [ ] **Step 3: Verify RULES.md is valid XML**
```bash
uv run pytest tests/unit/test_content_structure.py -v
```

---

### Task 8: Add framework usage guidance to ARCHITECTURE.md

**Files:**
- Modify: `src/superclaude/ARCHITECTURE.md`

Key changes from using-superclaude skill:
- Update skills/ section to reflect new scope (hooks + safety only)
- Add instruction priority note
- Update skill count

- [ ] **Step 1: Update skills/ section (lines 57-61)**

Replace:
```markdown
### skills/ — HOW TO EXECUTE

Execution containers with hooks, tool restrictions, and optional subagent isolation. Managed by Claude Code's native skill system — auto-detected via `description` keyword matching.

**Contract:** Skills define execution procedures with safety boundaries. They can restrict tools (`allowed-tools`), run in isolation (`context: fork`), and attach lifecycle hooks. Skills are the only content type that can modify Claude Code's permission model at runtime.
```

With:
```markdown
### skills/ — RUNTIME HOOKS & SAFETY

CC-native execution containers limited to capabilities that commands and agents cannot provide: lifecycle hooks, tool restrictions, auto-invocation blocking, and script execution.

**Contract:** Skills exist only when CC-native features are required. Workflow procedures belong in commands/. Domain expertise belongs in agents/. Skills provide:
- `hooks` (PreToolUse, PostToolUse, Stop) — runtime behavior modification
- `disable-model-invocation` — prevent auto-execution of destructive workflows
- `allowed-tools` — restrict tool access for safety
- Script execution via `{{SKILLS_PATH}}` template variables

**Current skills (4):** confidence-check (PreToolUse hook), simplicity-coach (Stop hook + scripts), ship (disable-model-invocation), finishing-a-development-branch (disable-model-invocation + allowed-tools)
```

- [ ] **Step 2: Update Framework Taxonomy table (lines 7-17)**

Replace the skills line:
```
skills/         Execution logic     Procedure       CC-native auto-detection
```
With:
```
skills/         Runtime hooks       Safety gate     CC-native (hooks + safety only)
```

- [ ] **Step 3: Update Naming Trinity section — add note about skills (after line 134)**

Add:
```markdown

**Note:** Skills are deliberately absent from the naming trinity. They serve a cross-cutting infrastructure role (hooks, safety), not a domain-specific one. Workflow procedures that were formerly in skills now live in commands.
```

- [ ] **Step 4: Update CC-native delivery row in table (line 113)**

Replace:
```
| **CC-native** | agents/, commands/, skills/ | Auto-delegation, /sc:*, description match | Managed by Claude Code runtime |
```
With:
```
| **CC-native** | agents/, commands/, skills/ | Auto-delegation, /sc:*, hooks/safety | Managed by Claude Code runtime |
```

- [ ] **Step 5: Verify**
```bash
uv run pytest tests/unit/test_content_structure.py -v
```

---

## Chunk 5: Delete Skills and Update Tests

### Task 9: Delete 11 skill directories

**Files:**
- Delete: `src/superclaude/skills/brainstorming/`
- Delete: `src/superclaude/skills/writing-plans/`
- Delete: `src/superclaude/skills/executing-plans/`
- Delete: `src/superclaude/skills/verification-before-completion/`
- Delete: `src/superclaude/skills/test-driven-development/`
- Delete: `src/superclaude/skills/systematic-debugging/`
- Delete: `src/superclaude/skills/requesting-code-review/`
- Delete: `src/superclaude/skills/receiving-code-review/`
- Delete: `src/superclaude/skills/dispatching-parallel-agents/`
- Delete: `src/superclaude/skills/using-git-worktrees/`
- Delete: `src/superclaude/skills/using-superclaude/`

- [ ] **Step 1: Delete all 11 directories**
```bash
rm -rf src/superclaude/skills/brainstorming
rm -rf src/superclaude/skills/writing-plans
rm -rf src/superclaude/skills/executing-plans
rm -rf src/superclaude/skills/verification-before-completion
rm -rf src/superclaude/skills/test-driven-development
rm -rf src/superclaude/skills/systematic-debugging
rm -rf src/superclaude/skills/requesting-code-review
rm -rf src/superclaude/skills/receiving-code-review
rm -rf src/superclaude/skills/dispatching-parallel-agents
rm -rf src/superclaude/skills/using-git-worktrees
rm -rf src/superclaude/skills/using-superclaude
```

- [ ] **Step 2: Verify only 4 skills remain**
```bash
ls src/superclaude/skills/
# Expected: README.md, confidence-check/, finishing-a-development-branch/, ship/, simplicity-coach/
```

---

### Task 10: Update test_skill_structure.py (15 → 4 skills)

**Files:**
- Modify: `tests/unit/test_skill_structure.py`

- [ ] **Step 1: Replace skill name sets (lines 22-55)**

Replace lines 22-55 with:
```python
# All superclaude skill names — only CC-native capability skills remain
# (hooks, disable-model-invocation, allowed-tools, scripts)
HOOK_SKILL_NAMES = {
    "confidence-check",       # PreToolUse hook + validation script
    "simplicity-coach",       # Stop hook + dependency-audit script
}

SAFETY_SKILL_NAMES = {
    "ship",                          # disable-model-invocation
    "finishing-a-development-branch", # disable-model-invocation + allowed-tools
}

ALL_SKILL_NAMES = HOOK_SKILL_NAMES | SAFETY_SKILL_NAMES

# Skills that MUST have disable-model-invocation: true
SIDE_EFFECT_SKILLS = {
    "ship",
    "finishing-a-development-branch",
}

# No fork-context skills remain (requesting-code-review migrated to /sc:review)
FORK_CONTEXT_SKILLS: set[str] = set()
```

- [ ] **Step 2: Update TestSkillCoverage (lines 94-119)**

Replace with:
```python
class TestSkillCoverage:
    """Validate all expected skills exist."""

    def test_total_skill_count(self):
        """Must have exactly 4 skills (2 hook + 2 safety)."""
        assert len(SKILL_DIRS) == 4, (
            f"Expected 4 skills, found {len(SKILL_DIRS)}: {SKILL_IDS}"
        )

    def test_all_hook_skills_present(self):
        """Both hook skills must exist."""
        actual = set(SKILL_IDS)
        missing = HOOK_SKILL_NAMES - actual
        assert not missing, f"Missing hook skills: {missing}"

    def test_all_safety_skills_present(self):
        """Both safety skills must exist."""
        actual = set(SKILL_IDS)
        missing = SAFETY_SKILL_NAMES - actual
        assert not missing, f"Missing safety skills: {missing}"

    def test_no_unexpected_skills(self):
        """No unexpected skill directories."""
        actual = set(SKILL_IDS)
        unexpected = actual - ALL_SKILL_NAMES
        assert not unexpected, f"Unexpected skills: {unexpected}"
```

- [ ] **Step 3: Update TestSkillFrontmatterPolicy (lines 164-196)**

Replace with:
```python
class TestSkillFrontmatterPolicy:
    """Validate frontmatter matches policy."""

    def test_side_effect_skills_have_disable_model_invocation(self, skill):
        dirname, content, fm = skill
        if dirname in SIDE_EFFECT_SKILLS:
            assert fm.get("disable-model-invocation") == "true", (
                f"{dirname}: side-effect skill must have disable-model-invocation: true"
            )

    def test_no_orphaned_fork_context(self, skill):
        """No remaining skills should have context: fork."""
        dirname, content, fm = skill
        assert fm.get("context") != "fork", (
            f"{dirname}: context: fork skills have been migrated to commands"
        )

    def test_no_orphaned_agent_field(self, skill):
        """No remaining skills should have agent: field."""
        dirname, content, fm = skill
        assert "agent" not in fm, (
            f"{dirname}: agent: field skills have been migrated to commands"
        )
```

- [ ] **Step 4: Update TestWorkflowGates (lines 233-248)**

Replace with:
```python
class TestWorkflowGates:
    """Validate workflow gates reference commands in RULES.md."""

    def test_rules_has_workflow_gates(self):
        rules_path = SKILLS_DIR.parent / "core" / "RULES.md"
        content = rules_path.read_text(encoding="utf-8")
        assert "<workflow_gates" in content, "RULES.md missing <workflow_gates> section"

    def test_workflow_gates_reference_commands(self):
        rules_path = SKILLS_DIR.parent / "core" / "RULES.md"
        content = rules_path.read_text(encoding="utf-8")
        for cmd in ["/sc:brainstorm", "/sc:plan", "/sc:implement", "/sc:test"]:
            assert cmd in content, (
                f"RULES.md workflow gates missing reference to '{cmd}'"
            )
```

- [ ] **Step 5: Run full test suite**
```bash
uv run pytest tests/unit/test_skill_structure.py -v
```

---

## Chunk 6: Update Documentation

### Task 11: Update skills/README.md

**Files:**
- Modify: `src/superclaude/skills/README.md`

- [ ] **Step 1: Rewrite README to reflect 4-skill scope**

Replace entire content with:
```markdown
# SuperClaude Skills

Skills are CC-native execution containers limited to capabilities that commands and agents cannot provide.

## When to Use Skills (vs Commands/Agents)

| Need | Content Type | Why |
|------|-------------|-----|
| Lifecycle hooks (PreToolUse, Stop) | **Skill** | Only skills can attach runtime hooks |
| Block auto-invocation | **Skill** | Only skills have `disable-model-invocation` |
| Tool restriction (allowed-tools) | **Skill** | Only skills whitelist tools at runtime |
| Script execution | **Skill** | Only skills have `{{SKILLS_PATH}}` resolution |
| Workflow procedures | **Command** | Commands define WHAT TO DO |
| Domain expertise | **Agent** | Agents define WHO TO BE |
| Cognitive overlay | **Mode** | Modes define HOW TO THINK |

## Current Skills (4)

| Skill | CC-Native Feature | Purpose |
|-------|-------------------|---------|
| `confidence-check` | PreToolUse hook | Injects evidence-focus guidance on WebFetch/WebSearch |
| `simplicity-coach` | Stop hook + scripts | Runs dependency audit at session end |
| `ship` | disable-model-invocation | Protects destructive delivery workflow from auto-execution |
| `finishing-a-development-branch` | disable-model-invocation + allowed-tools | Protects branch completion; restricts to Bash, Read, Grep, Glob |

## Authoring Guide

See `.claude/rules/skill-authoring.md` for frontmatter specification and XML body structure.

**Key rule:** Only create a skill when you need a CC-native capability (hooks, safety, scripts). Workflow procedures belong in `commands/`. Domain expertise belongs in `agents/`.
```

- [ ] **Step 2: Verify README exists and is valid**
```bash
test -f src/superclaude/skills/README.md && echo "OK"
```

---

### Task 12: Update CLAUDE.md skill references

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update Package Structure skills line**

Find and replace the skills line in Package Structure:
```
├── skills/              # 15 skills — execution containers with hooks (authoring: .claude/rules/skill-authoring.md)
```
With:
```
├── skills/              # 4 skills — CC-native hooks + safety only (authoring: .claude/rules/skill-authoring.md)
```

- [ ] **Step 2: Update Content Installation Flow skills line**

Find and replace:
```
src/superclaude/skills/    →  ~/.claude/skills/             (skill implementations)
```
With:
```
src/superclaude/skills/    →  ~/.claude/skills/             (4 hook/safety skills)
```

- [ ] **Step 3: Update Content Framework Taxonomy skills row**

Find and replace:
```
| `skills/` | Execution logic | CC-native auto-detection |
```
With:
```
| `skills/` | Runtime hooks + safety | CC-native (hooks, disable-model-invocation) |
```

- [ ] **Step 4: Verify no broken references**
```bash
grep -r "15 skills" CLAUDE.md src/superclaude/ARCHITECTURE.md
# Should return no results
```

---

### Task 13: Update skill-authoring.md

**Files:**
- Modify: `.claude/rules/skill-authoring.md`

- [ ] **Step 1: Add decision gate at top of file (after first heading)**

Add after line 1 (`# Skill Authoring Rules`):
```markdown

> **Decision gate:** Only create a skill when you need a CC-native capability:
> hooks, `disable-model-invocation`, `allowed-tools`, or script execution.
> Workflow procedures → `commands/`. Domain expertise → `agents/`.
```

- [ ] **Step 2: Verify**
```bash
head -5 .claude/rules/skill-authoring.md
```

---

### Task 14: Update context_loader.py skill summary

**Files:**
- Modify: `src/superclaude/scripts/context_loader.py`

- [ ] **Step 1: Check if skill count is hardcoded**
```bash
grep -n "skill" src/superclaude/scripts/context_loader.py | head -20
```

If skill count is dynamically computed (via directory listing), no change needed.
If hardcoded, update to reflect 4 skills.

---

### Task 15: Run full verification

- [ ] **Step 1: Run all structural tests**
```bash
uv run pytest tests/unit/test_skill_structure.py tests/unit/test_command_structure.py tests/unit/test_content_structure.py -v
```

- [ ] **Step 2: Run full test suite**
```bash
uv run pytest
```

- [ ] **Step 3: Verify install works**
```bash
uv run superclaude install --list-all
```

- [ ] **Step 4: Deploy and verify**
```bash
make deploy
```
