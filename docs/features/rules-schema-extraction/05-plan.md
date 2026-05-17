---
status: draft
revised: 2026-04-14
---

# Rules Schema Extraction — Implementation Plan

**Goal:** Extract 3 duplicated enum sets from `tests/unit/test_*_structure.py` into `.claude/rules/schemas.yaml` as single source of truth, fixing the latent `red` color drift in the process.

**Architecture:** New YAML sidecar + conftest fixture loader. Two existing test files swap hardcoded Python sets for loaded values. Prose rule docs gain one-line pointers. No XML conversion, no body rewrites.

**Tech Stack:** Python 3.10+, pyyaml (already in deps), pytest, UV.

**Scope recap (from spec):**
- Extract: `agent_colors`, `effort_values`, `forbidden_command_fields`
- Resolve: `red` drift — remove from schema (no agent uses it; not in role-group table)
- Preserve: 828 lines of prose rule docs (untouched)
- Baseline: 1,628+ passing (CLAUDE.md); no new failures allowed

---

## Phase 0 — Baseline capture (2 min, no changes)

### Task 0.1: Record pre-change test baseline

**Files:** none (read-only)

- [ ] Run `uv run pytest tests/unit/ --tb=no -q 2>&1 | tail -5`
- [ ] Record pass/fail/error counts verbatim in Phase 5 verification
- [ ] Confirm `frontend-architect` skill-reference is the 1 known pre-existing failure (per CLAUDE.md + memory 1070)

**Gate:** baseline recorded. If fresh failures unrelated to our scope appear, stop and report.

---

## Phase 1 — Schema YAML file (TDD, ~5 min)

### Task 1.1: Write failing test for schema file existence + shape

**Files:**
- Create: `tests/unit/test_rules_schemas.py` (new, ~30 lines)

- [ ] Write test `test_schemas_yaml_exists_and_parses()` asserting `.claude/rules/schemas.yaml` exists, is valid YAML, and has top-level keys: `agent_colors`, `effort_values`, `forbidden_command_fields`
- [ ] Write test `test_agent_colors_mapping_matches_role_groups()` asserting `agent_colors` is a dict mapping role-group → color, with exactly 6 groups from `agent-authoring.md` (architecture, engineering, research, documentation, management, indexing)
- [ ] Write test `test_red_not_in_agent_colors()` asserting `"red"` is NOT in `agent_colors.values()` (drift fix regression guard)
- [ ] Run `uv run pytest tests/unit/test_rules_schemas.py -v` — **verify all 3 fail** (file doesn't exist yet)

### Task 1.2: Create schema YAML

**Files:**
- Create: `.claude/rules/schemas.yaml` (new, ~25 lines)

- [ ] Write YAML content exactly:

```yaml
# Single source of truth for mechanically-enforced enum rules from .claude/rules/*-authoring.md.
# Prose authoring guides remain authoritative for *how* to author; this file is authoritative for *what values are valid*.
# Loaded by tests/conftest.py via fixture `rules_schemas`.
# Last reviewed: 2026-04-14

# Agent color palette — maps role group to required color.
# Source: .claude/rules/agent-authoring.md "color by role group" table.
agent_colors:
  architecture: blue       # system design, frontend, backend, devops
  engineering: green       # coding, security, performance, quality, refactoring
  research: purple         # investigation, research, requirements
  documentation: yellow    # writing, teaching, mentoring
  management: orange       # orchestration, business, review, simplicity
  indexing: cyan           # repository scanning

# Effort enum — adaptive reasoning depth (CC v2.1.69+).
# Source: .claude/rules/agent-authoring.md "effort" table.
effort_values:
  - low       # mechanical/structured (repo-index, git-workflow)
  - medium    # standard design + analysis (default)
  - high      # complex reasoning, deep debugging
  - max       # multi-perspective synthesis (Opus 4.6 only)

# Command frontmatter forbidden fields — these belong on agents/skills, not commands.
# Source: .claude/rules/command-authoring.md "Forbidden fields" list.
forbidden_command_fields:
  - name           # derived from filename
  - model          # agent-only
  - permissionMode # agent-only
  - memory         # agent-only
  - color          # agent-only
  - autonomy       # not an official CC field
  - context        # skill-only
  - agent          # skill-only
  - hooks          # skill-only
```

- [ ] Run `uv run pytest tests/unit/test_rules_schemas.py -v` — **verify all 3 pass**

### Task 1.3: Commit Phase 1

- [ ] `rtk git add tests/unit/test_rules_schemas.py .claude/rules/schemas.yaml`
- [ ] `rtk git commit -m "feat: add .claude/rules/schemas.yaml as SSOT for agent/command enum rules"`

---

## Phase 2 — Wire loader fixture (TDD, ~4 min)

### Task 2.1: Write failing fixture-usage test

**Files:**
- Modify: `tests/unit/test_rules_schemas.py` (append ~10 lines)

- [ ] Append test `test_conftest_fixture_rules_schemas_loads(rules_schemas)` asserting the fixture returns a dict with the 3 top-level keys
- [ ] Run `uv run pytest tests/unit/test_rules_schemas.py::test_conftest_fixture_rules_schemas_loads -v` — **verify it errors** (fixture missing)

### Task 2.2: Add fixture to conftest

**Files:**
- Modify: `tests/conftest.py` (append ~12 lines)

- [ ] Append at end of file:

```python
from pathlib import Path
import yaml
import pytest

@pytest.fixture(scope="session")
def rules_schemas() -> dict:
    """Load .claude/rules/schemas.yaml as source of truth for enum rules."""
    path = Path(__file__).parent.parent / ".claude" / "rules" / "schemas.yaml"
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)
```

- [ ] Run `uv run pytest tests/unit/test_rules_schemas.py -v` — **verify all pass**

### Task 2.3: Commit Phase 2

- [ ] `rtk git add tests/conftest.py tests/unit/test_rules_schemas.py`
- [ ] `rtk git commit -m "feat: add rules_schemas pytest fixture loading schemas.yaml"`

---

## Phase 3 — Rewire test_agent_structure.py (TDD, ~5 min)

### Task 3.1: Write failing drift-guard test

**Files:**
- Modify: `tests/unit/test_agent_structure.py:17` (change VALID_COLORS literal)

- [ ] Add test function `test_valid_colors_comes_from_schema(rules_schemas)` asserting `VALID_COLORS == set(rules_schemas["agent_colors"].values())` and `"red" not in VALID_COLORS`
- [ ] Run that test — **it fails** (VALID_COLORS still has `red` at line 17)

### Task 3.2: Replace hardcoded constants with fixture values

**Files:**
- Modify: `tests/unit/test_agent_structure.py:15-18` (remove hardcoded VALID_COLORS + VALID_EFFORT_VALUES, keep VALID_PERMISSION_MODES + VALID_MEMORY_SCOPES as-is — those aren't duplicated in rule docs)

- [ ] Replace:
  ```python
  VALID_COLORS = {"blue", "green", "orange", "purple", "yellow", "cyan", "red"}
  VALID_EFFORT_VALUES = {"low", "medium", "high", "max"}
  ```
  with module-level helper load (keep pattern consistent with existing module-level constants):
  ```python
  _SCHEMAS_PATH = Path(__file__).parent.parent.parent / ".claude" / "rules" / "schemas.yaml"
  _SCHEMAS = yaml.safe_load(_SCHEMAS_PATH.read_text(encoding="utf-8"))
  VALID_COLORS = set(_SCHEMAS["agent_colors"].values())
  VALID_EFFORT_VALUES = set(_SCHEMAS["effort_values"])
  ```
- [ ] Ensure `import yaml` and `from pathlib import Path` exist at top (add if missing)
- [ ] Run `uv run pytest tests/unit/test_agent_structure.py -v` — **verify all pass**, no new failures vs baseline
- [ ] Run the Task 3.1 drift-guard test — **verify it now passes**

### Task 3.3: Commit Phase 3

- [ ] `rtk git add tests/unit/test_agent_structure.py`
- [ ] `rtk git commit -m "refactor(tests): load VALID_COLORS + VALID_EFFORT_VALUES from schemas.yaml, fix red drift"`

---

## Phase 4 — Rewire test_command_structure.py (TDD, ~4 min)

### Task 4.1: Write failing assertion

**Files:**
- Modify: `tests/unit/test_command_structure.py:16-19`

- [ ] Add test `test_forbidden_fields_matches_schema(rules_schemas)` asserting `FORBIDDEN_FIELDS == set(rules_schemas["forbidden_command_fields"])`
- [ ] Run it — **passes** (values happen to match). This is a regression guard, not a fix. Acceptable TDD variant: the test locks the coupling.

### Task 4.2: Replace hardcoded FORBIDDEN_FIELDS

**Files:**
- Modify: `tests/unit/test_command_structure.py:16-19`

- [ ] Replace hardcoded set with:
  ```python
  _SCHEMAS_PATH = Path(__file__).parent.parent.parent / ".claude" / "rules" / "schemas.yaml"
  _SCHEMAS = yaml.safe_load(_SCHEMAS_PATH.read_text(encoding="utf-8"))
  FORBIDDEN_FIELDS = set(_SCHEMAS["forbidden_command_fields"])
  ```
- [ ] Ensure `import yaml`, `from pathlib import Path` are at top
- [ ] Run `uv run pytest tests/unit/test_command_structure.py -v` — **verify all pass**

### Task 4.3: Commit Phase 4

- [ ] `rtk git add tests/unit/test_command_structure.py`
- [ ] `rtk git commit -m "refactor(tests): load FORBIDDEN_FIELDS from schemas.yaml"`

---

## Phase 5 — Prose pointers + final verify (~3 min)

### Task 5.1: Add pointer lines to authoring docs

**Files:**
- Modify: `.claude/rules/agent-authoring.md` — near the "color by role group" table (currently cited in research; find exact line via grep)
- Modify: `.claude/rules/agent-authoring.md` — near the "effort" table
- Modify: `.claude/rules/command-authoring.md` — near "Forbidden fields" list

- [ ] For each, append one italicized line directly after the relevant table/list:
  ```markdown
  *Mechanical source of truth: `.claude/rules/schemas.yaml`. Prose here remains authoritative for rationale and role grouping.*
  ```
- [ ] Run `uv run pytest tests/unit/ --tb=no -q 2>&1 | tail -5` — verify baseline preserved (no prose-test coupling should trigger)

### Task 5.2: Deploy and full-suite verification

- [ ] `make deploy` — propagates schemas.yaml to `~/.claude/rules/schemas.yaml` (verify install path includes `.claude/rules/` — if not, this is out-of-scope; schemas.yaml is consumed by tests only, not runtime)
- [ ] **Verify**: confirm whether install pipeline touches `.claude/rules/` — read `src/superclaude/cli/install_paths.py` if uncertain. If `.claude/rules/` is **test-only** (not installed to user scope), note this in commit message — schemas.yaml lives in repo only
- [ ] Run `uv run pytest tests/unit/ --tb=short 2>&1 | tail -20`
- [ ] Compare pass count to Phase 0 baseline: **must be baseline + new test_rules_schemas.py tests, no net regressions**
- [ ] Cite evidence in final report: "Before: N/M pass. After: (N+4)/(M+4) pass. New tests: test_rules_schemas.py (4). No regressions."

### Task 5.3: Commit Phase 5

- [ ] `rtk git add .claude/rules/agent-authoring.md .claude/rules/command-authoring.md`
- [ ] `rtk git commit -m "docs(rules): point color/effort/forbidden-fields tables to schemas.yaml"`

---

## Verification checklist (R15)

- [ ] `uv run pytest tests/unit/test_rules_schemas.py -v` — 4 tests pass (exists/parses, role-group mapping, no-red, fixture-loads)
- [ ] `uv run pytest tests/unit/test_agent_structure.py -v` — baseline + drift-guard pass
- [ ] `uv run pytest tests/unit/test_command_structure.py -v` — baseline + schema-match pass
- [ ] `uv run pytest tests/unit/ --tb=no -q` — total pass count = Phase 0 baseline + 4
- [ ] `grep -r "VALID_COLORS\s*=\s*{" tests/unit/` — returns 0 matches (no more hardcoded literal)
- [ ] `grep -r "FORBIDDEN_FIELDS\s*=\s*{" tests/unit/` — returns 0 matches
- [ ] `grep -c "red" tests/unit/test_agent_structure.py` — returns 0 (drift eliminated)

## Risks + mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Install pipeline doesn't copy `.claude/rules/` to user scope → runtime CC doesn't see schemas.yaml | Medium | schemas.yaml is test-only infrastructure, not runtime content. If install doesn't copy, that's correct. Verify in Task 5.2 |
| Existing unrelated test uses `VALID_COLORS` from test_agent_structure module | Low | Grep `tests/` for imports of these names before Task 3.2 |
| conftest fixture scope="session" conflicts with existing session fixtures | Low | `rules_schemas` is a new name; no collision expected. Verify with `grep -r "def rules_schemas" tests/` before Task 2.2 |
| `red` removal breaks an agent not previously grep'd | Very Low | Already confirmed via `grep "^color: red" src/superclaude/agents/*.md` → 0 matches |

## Out-of-scope (deferred, do not touch)

- XML body wrapping of any rule doc (per research + spec decision)
- Gotchas files (intentional line format)
- skill-authoring.md / mode-authoring.md extraction (no observed drift, no duplication)
- Install pipeline changes to publish `.claude/rules/` to user scope (schemas.yaml is test-only)

## Handoff

- **Next**: `/sc:implement --plan docs/features/rules-schema-extraction/05-plan.md`
- **Reference**: spec [`./01-discovery.md`](./01-discovery.md), research `docs/research/rules-xml-conversion-ajitta-2026-04-14.md` (related, separate slug — consider promotion via `/sc:promote-feature rules-xml-conversion`)
- **Estimate**: ~18 min total (phases 0–5), 5 commits, <60 lines net diff excluding new test file (~40 lines)
