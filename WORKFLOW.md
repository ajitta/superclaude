# SuperClaude Code Quality Workflow

**Generated:** 2026-01-17
**Source:** `/sc:analyze "src/superclaude"` findings
**Strategy:** Wave-based parallel execution
**Total Effort:** ~7h (with parallelization)

---

## Executive Summary

| Wave | Priority | Tasks | Parallel | Duration |
|------|----------|-------|----------|----------|
| 1 | P0 | Dead code removal + mcp_fallback tests | Yes | 1.5h |
| 2 | P1 | Windows paths + imports | Yes | 30m |
| 3 | P1 | Hook tracker optimization | No | 2h |
| 4 | P2 | Logging + exports + tests | Yes | 2h |

**Prerequisites:** `uv pip install -e ".[dev]"` and all tests passing

---

## Wave 1: Critical Fixes (P0)

### Task 1.1: Remove Dead Code in confidence.py

**File:** `src/superclaude/pm_agent/confidence.py`
**Lines:** 794-1264 (~470 lines)
**Risk:** Medium

**Pre-check (REQUIRED):**
```bash
# Verify no external usages of legacy methods
grep -r "_has_official_docs\|_no_duplicates\|_architecture_compliant" src/ tests/ --include="*.py" | grep -v "confidence.py"
grep -r "_has_oss_reference\|_root_cause_identified\|_detect_tech_stack" src/ tests/ --include="*.py" | grep -v "confidence.py"
```

**Expected result:** Empty (no matches outside confidence.py)

**Steps:**
1. [ ] Create backup branch: `git checkout -b backup/pre-cleanup`
2. [ ] Search for usages (pre-check above)
3. [ ] If no usages found, delete lines 794-1264
4. [ ] Run tests: `uv run pytest tests/unit/test_confidence.py -v`
5. [ ] Commit: `refactor: remove ~470 lines of unused legacy methods from confidence.py`

**Methods to remove:**
- `_has_official_docs()` (line 794)
- `_no_duplicates()` (line 825)
- `_architecture_compliant()` (line 879)
- `_detect_tech_stack()` (line 917)
- `_find_architecture_conflicts()` (line 931)
- `_has_oss_reference()` (line 971)
- `_validate_oss_references()` (line 1018)
- `_find_cached_pattern()` (line 1054)
- `_match_known_oss_pattern()` (line 1084)
- `_root_cause_identified()` (line 1165)
- `_has_existing_patterns()` (line 1197)
- `_has_clear_path()` (line 1220)

---

### Task 1.2: Add test_mcp_fallback.py

**New file:** `tests/unit/test_mcp_fallback.py`
**Coverage target:** >80%

**Steps:**
1. [ ] Create `tests/unit/test_mcp_fallback.py`
2. [ ] Implement test cases (see template below)
3. [ ] Run: `uv run pytest tests/unit/test_mcp_fallback.py -v --cov=superclaude.hooks.mcp_fallback`
4. [ ] Commit: `test: add comprehensive tests for mcp_fallback module`

**Test template:**
```python
"""Tests for MCP fallback notification tracker."""
import pytest
from pathlib import Path
from superclaude.hooks.mcp_fallback import (
    should_notify_fallback,
    check_mcp_and_notify,
    get_fallback_for,
    cleanup_old_fallback_sessions,
    MCP_FALLBACKS,
)
from superclaude.hooks.hook_tracker import reset_session

@pytest.fixture(autouse=True)
def clean_session():
    """Reset session before each test."""
    reset_session()
    yield

class TestShouldNotifyFallback:
    def test_first_notification_returns_true(self):
        should_notify, fallback = should_notify_fallback("tavily")
        assert should_notify is True
        assert fallback == "WebSearch (native)"

    def test_second_notification_returns_false(self):
        should_notify_fallback("tavily")  # First call
        should_notify, _ = should_notify_fallback("tavily")  # Second call
        assert should_notify is False

    def test_different_mcp_gets_notification(self):
        should_notify_fallback("tavily")
        should_notify, _ = should_notify_fallback("context7")
        assert should_notify is True

class TestCheckMcpAndNotify:
    def test_returns_formatted_notification(self):
        result = check_mcp_and_notify("serena")
        assert result == "⚠️ serena unavailable → using Native search"

    def test_returns_none_on_subsequent(self):
        check_mcp_and_notify("serena")
        result = check_mcp_and_notify("serena")
        assert result is None

class TestGetFallbackFor:
    def test_known_mcp_returns_fallback(self):
        assert get_fallback_for("tavily") == "WebSearch (native)"
        assert get_fallback_for("context7") == "Tavily/WebSearch"
        assert get_fallback_for("sequential") == "Native reasoning"

    def test_unknown_mcp_returns_native(self):
        assert get_fallback_for("unknown_mcp") == "Native"

class TestCleanup:
    def test_cleanup_old_sessions(self):
        # Create some notifications
        should_notify_fallback("tavily")
        # Cleanup with 0 TTL should clean current session
        cleaned = cleanup_old_fallback_sessions(ttl_seconds=0)
        assert cleaned >= 0
```

---

### Quality Gate 1

**Run after Wave 1 complete:**
```bash
uv run pytest -v
uv run pytest tests/unit/test_mcp_fallback.py --cov=superclaude.hooks.mcp_fallback --cov-report=term-missing
```

**Criteria:**
- [ ] All tests pass
- [ ] mcp_fallback coverage >80%
- [ ] No import errors

---

## Wave 2: Path & Import Fixes (P1)

### Task 2.1: Fix Windows Path Compatibility

**File:** `src/superclaude/pytest_plugin.py:207-209`

**Current (broken on Windows):**
```python
if "/unit/" in test_path:
    item.add_marker(pytest.mark.unit)
elif "/integration/" in test_path:
    item.add_marker(pytest.mark.integration)
```

**Fixed:**
```python
import os
# ... at line 207
normalized_path = test_path.replace("\\", "/")  # Normalize to forward slashes
if "/unit/" in normalized_path:
    item.add_marker(pytest.mark.unit)
elif "/integration/" in normalized_path:
    item.add_marker(pytest.mark.integration)
```

**Steps:**
1. [ ] Edit `pytest_plugin.py` line 207-209
2. [ ] Add path normalization
3. [ ] Run tests: `uv run pytest`
4. [ ] Commit: `fix: Windows path compatibility in pytest_plugin auto-markers`

---

### Task 2.2: Move Imports to Module Level

**Files:**
- `src/superclaude/cli/main.py`
- `src/superclaude/pm_agent/reflexion.py`

**main.py changes:**
```python
# Add at top of file (after existing imports):
import re
import yaml

# Remove from inside functions:
# - Line 481-484 (agents command)
# - Line 514-515 (agents command)
# - Line 541-544 (agents command)
# - Line 665-666 (skills command)
# - Line 700-701 (skills command)
```

**reflexion.py changes:**
```python
# Move from line 154-156 to top of file:
import re
```

**Steps:**
1. [ ] Edit `cli/main.py` - move imports to top
2. [ ] Edit `pm_agent/reflexion.py` - move import to top
3. [ ] Run: `make lint`
4. [ ] Run: `uv run pytest`
5. [ ] Commit: `style: move imports to module level per PEP 8`

---

### Quality Gate 2

**Run after Wave 2 complete:**
```bash
# Check no imports inside functions
grep -rn "^    import " src/superclaude/*.py src/superclaude/**/*.py
make lint
uv run pytest
```

**Criteria:**
- [ ] grep returns empty
- [ ] Linting passes
- [ ] All tests pass

---

## Wave 3: Performance Optimization (P1)

### Task 3.1: Optimize hook_tracker.py I/O

**File:** `src/superclaude/hooks/hook_tracker.py`

**Current problem:** `check_and_mark()` loads JSON twice (lines 386-390)

**Optimized implementation:**
```python
def check_and_mark(
    hook_type: str,
    command: str,
    source: str,
    once: bool = False,
    matcher: str | None = None,
) -> bool:
    """Check if hook should execute and mark it if so - optimized single I/O."""
    if not once:
        return True

    session_id = get_session_id()
    hook_id = _generate_hook_id(hook_type, command, source, matcher)

    # Single load
    data = _load_tracker_data()

    # Check if already executed
    session_data = data.get(session_id)
    if session_data and hook_id in session_data.executions:
        return False

    # Mark as executed
    if session_id not in data:
        data[session_id] = SessionData(
            session_id=session_id,
            started_at=datetime.now().isoformat(),
        )

    data[session_id].executions[hook_id] = HookExecution(
        hook_id=hook_id,
        hook_type=hook_type,
        executed_at=datetime.now().isoformat(),
        source=source,
    )

    # Single save
    _save_tracker_data(data)
    return True
```

**Steps:**
1. [ ] Backup current implementation
2. [ ] Refactor `check_and_mark()` to single load/save
3. [ ] Run tests: `uv run pytest tests/unit/ -v`
4. [ ] Commit: `perf: optimize hook_tracker to single I/O per check_and_mark`

---

### Quality Gate 3

```bash
uv run pytest tests/unit/test_hook_tracker.py -v
# Optional: Add benchmark test
```

**Criteria:**
- [ ] All hook_tracker tests pass
- [ ] No functional regressions

---

## Wave 4: Polish (P2)

### Task 4.1: Replace print() with logging

**File:** `src/superclaude/execution/parallel.py`

**Steps:**
1. [ ] Add at top: `import logging` and `logger = logging.getLogger(__name__)`
2. [ ] Replace all `print()` calls with `logger.info()` or `logger.debug()`
3. [ ] Run: `grep -n "print(" src/superclaude/execution/parallel.py` (should be empty)
4. [ ] Commit: `refactor: replace print() with logging in parallel.py`

---

### Task 4.2: Add __all__ exports

**Files:** All modules in `src/superclaude/`

**Example for confidence.py:**
```python
__all__ = [
    "ConfidenceCheck",
    "AsyncConfidenceCheck",
    "CheckResult",
    "ConfidenceResult",
    "ConfidenceChecker",
    "NoDuplicatesCheck",
    "ArchitectureCheck",
    "OfficialDocsCheck",
    "OssReferenceCheck",
    "RootCauseCheck",
    "DEFAULT_CHECKS",
]
```

**Steps:**
1. [ ] Add `__all__` to each module
2. [ ] Include only public API
3. [ ] Commit: `style: add __all__ exports to all public modules`

---

### Task 4.3: Add tests for parallel.py

**New file:** `tests/unit/test_parallel.py`

**Coverage target:** >80%

**Test cases:**
- Task dataclass and can_execute()
- ParallelExecutor.plan() dependency resolution
- ParallelExecutor.execute() parallel execution
- Circular dependency detection raises ValueError
- parallel_file_operations convenience function
- should_parallelize threshold

**Steps:**
1. [ ] Create `tests/unit/test_parallel.py`
2. [ ] Implement test cases
3. [ ] Run: `uv run pytest tests/unit/test_parallel.py -v --cov=superclaude.execution.parallel`
4. [ ] Commit: `test: add comprehensive tests for parallel execution engine`

---

### Quality Gate 4 (Final)

```bash
# No print statements
grep -rn "print(" src/superclaude/execution/parallel.py

# All modules have __all__
grep -l "__all__" src/superclaude/*.py src/superclaude/**/*.py | wc -l

# Full test suite with coverage
uv run pytest --cov=superclaude --cov-report=term-missing

# Linting
make lint
```

**Criteria:**
- [ ] No print() in parallel.py
- [ ] __all__ in all public modules
- [ ] Overall coverage >75%
- [ ] All tests pass
- [ ] Linting passes

---

## Completion Checklist

### Final Acceptance Criteria:
- [ ] Wave 1 complete + QG1 passed
- [ ] Wave 2 complete + QG2 passed
- [ ] Wave 3 complete + QG3 passed
- [ ] Wave 4 complete + QG4 passed
- [ ] `make test` passes
- [ ] `make lint` passes
- [ ] No regressions in CI/CD
- [ ] Update CHANGELOG.md with changes

### Git History (Expected):
```
feat: add comprehensive tests for parallel execution engine
style: add __all__ exports to all public modules
refactor: replace print() with logging in parallel.py
perf: optimize hook_tracker to single I/O per check_and_mark
style: move imports to module level per PEP 8
fix: Windows path compatibility in pytest_plugin auto-markers
test: add comprehensive tests for mcp_fallback module
refactor: remove ~470 lines of unused legacy methods from confidence.py
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Dead code removal breaks something | Pre-check grep + backup branch |
| Windows fix breaks Unix | Test both path formats |
| Cache introduces stale data | Short TTL + invalidation |

**Rollback:** Each wave is a separate commit. Revert specific commit if QG fails.

---

*Generated by /sc:workflow with --think-hard analysis*
