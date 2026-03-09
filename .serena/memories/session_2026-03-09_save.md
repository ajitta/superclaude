# Session 2026-03-09: Workflow Anti-Patterns & pm_agent Analysis

## What Was Done

### 1. Workflow Anti-Pattern Root Causes (from plan)
Implemented fixes for three recurring failure patterns: redundant exploration, wrong initial diagnosis, test iteration loops.

**RULES.md changes:**
- Added `Status Check 🔴`: targeted searches (git log, grep) before implementation
- Added `Diagnosis 🔴`: 3+ hypotheses, environment before code, falsify before confirming
- Updated Workflow: `Status Check → Understand → Plan → Execute → Validate`

**PRINCIPLES.md changes:**
- Added Diagnosis line to `<decisions>`: multi-hypothesis, environment-first, known-pitfalls check

**confidence.py changes:**
- Added `AlreadyImplementedCheck` class (searches git log for existing implementations)
- Added to DEFAULT_CHECKS (6 checks now, rebalanced weights to 1.0)

**Auto memory:**
- Created `testing_patterns.md` — persistent cross-session testing pitfall knowledge

### 2. pm_agent Full Analysis (3 parallel agents)
Ran comprehensive analysis across code quality, content alignment, and test coverage.

**Critical findings fixed:**
1. `rglob` unbounded scan → iterative with `_exclude_dirs` set + early `break`
2. Path traversal in reflexion.py → sanitize test_name (`/`, `\`, `..`)
3. Cache key collision → `Path.resolve()` normalization
4. Falsy ID bug in task_cleanup → explicit `is not None` check
5. Uncaught json.loads in PRStatusCheck → try-except wrapper

**pm-agent.md vs pm_agent/ decision:**
- These are SEPARATE SYSTEMS: pm-agent.md = Claude behavioral prompt, pm_agent/ = pytest plugin
- Do NOT integrate — different layers, different users, correctly separated
- Fixed pm-agent.md: removed aspirational Serena claims, added `<outputs>` section
- Fixed pm_agent/__init__.py: docstring clarified as "Pytest Patterns"

### 3. Test Coverage Gaps Identified (not yet fixed)
- PRStatusCheck: 0 tests (uses subprocess)
- AlreadyImplementedCheck._check_git_log(): 0 tests
- detect_tech_stack_multi_dir(): 0 tests
- SelfCheckProtocol.check_and_cleanup_tasks(): 0 tests

## Files Modified
- `src/superclaude/core/RULES.md` — status gate + diagnostic protocol
- `src/superclaude/core/PRINCIPLES.md` — diagnosis discipline
- `src/superclaude/pm_agent/confidence.py` — AlreadyImplementedCheck, 5 bug fixes
- `src/superclaude/pm_agent/reflexion.py` — path traversal fix
- `src/superclaude/pm_agent/task_cleanup.py` — falsy ID fix
- `src/superclaude/pm_agent/__init__.py` — docstring clarification
- `src/superclaude/agents/pm-agent.md` — aspirational claims removed, outputs added
- `tests/unit/test_confidence.py` — updated for 6-check defaults
- `tests/conftest.py` — added already_implemented_check to fixtures

## Key Decision
pm-agent.md (prompt engineering layer) and pm_agent/ (pytest plugin layer) should remain separate. Integration would violate YAGNI — Claude already gets the same heuristics via RULES.md prompt instructions.
