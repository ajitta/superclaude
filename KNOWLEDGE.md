# KNOWLEDGE.md

**Accumulated Insights, Best Practices, and Troubleshooting for SuperClaude Framework**

> This document captures lessons learned, common pitfalls, and solutions discovered during development.
> Consult this when encountering issues or learning project patterns.

**Last Updated**: 2026-01-27
**Version**: 4.2.1+ajitta

---

## Architecture Deep Dive

### Package Layout

SuperClaude uses a `src/` layout with hatchling (PEP 517) build system:

```
src/superclaude/
├── __init__.py              # Exports: ConfidenceChecker, ConfidenceResult, CheckResult, ReflexionPattern, SelfCheckProtocol
├── pytest_plugin.py         # Auto-loaded via pyproject.toml entry point (pytest11)
├── pm_agent/                # Pre/post implementation patterns
│   ├── confidence.py        # Protocol-based confidence checking (5 checks, weighted scoring)
│   ├── self_check.py        # Post-implementation validation ("The Four Questions")
│   ├── reflexion.py         # Cross-session error learning (JSONL storage, Jaccard matching)
│   └── token_budget.py      # Token allocation by complexity (simple:200, medium:1000, complex:2500)
├── execution/
│   ├── parallel.py          # ThreadPoolExecutor + topological sort (Wave→Checkpoint→Wave)
│   ├── reflection.py        # Post-execution analysis
│   └── self_correction.py   # Automated error correction
├── cli/                     # Click-based CLI (9 modules)
│   ├── main.py              # Entry: superclaude command group
│   ├── doctor.py            # Health check diagnostics
│   ├── install_skill.py     # Individual skill installation
│   ├── install_mcp.py       # MCP server config installation
│   ├── install_paths.py     # Installation path resolution
│   ├── install_settings.py  # Settings management
│   ├── install_commands.py  # Command file installation
│   ├── install_components.py # Component installation orchestration
│   └── install_inventory.py # Component inventory and listing
├── hooks/                   # Claude Code v2.1.0 hook system
│   ├── hook_tracker.py      # Session tracking (once:true, 24h TTL, SHA-256 session IDs)
│   ├── inline_hooks.py      # YAML frontmatter parser (wildcard tool filtering)
│   └── mcp_fallback.py      # First-notification-only MCP fallback handling
├── utils/
│   └── __init__.py          # Shared: word_overlap_ratio (Jaccard), atomic_write_json
├── agents/                  # 20 specialized agent definitions (.md)
├── commands/                # 30 slash command definitions (.md)
├── modes/                   # 7 behavioral modes + INDEX (.md)
├── mcp/                     # 10 MCP server configs + 11 docs
├── core/                    # 7 core configs (FLAGS, PRINCIPLES, RULES, etc.)
├── skills/                  # Skills (confidence-check)
└── scripts/                 # Shell/Python utilities
```

### Entry Points

```toml
# pyproject.toml
[project.scripts]
superclaude = "superclaude.cli.main:main"    # CLI entry

[project.entry-points.pytest11]
superclaude = "superclaude.pytest_plugin"     # Auto-loaded pytest plugin
```

### Key Dependencies

- `pytest>=7.0.0` — Test framework (core dependency)
- `click>=8.0.0` — CLI framework
- `rich>=13.0.0` — Terminal formatting
- `pyyaml>=6.0.0` — YAML frontmatter parsing
- `Python>=3.10` — Minimum Python version

---

## PM Agent Patterns (Core Module)

### ConfidenceChecker — Pre-Execution Gate

**File**: `src/superclaude/pm_agent/confidence.py`

The confidence system uses a Protocol-based architecture for extensibility:

```python
# Two protocols for sync and async checks
class ConfidenceCheck(Protocol):
    name: str
    weight: float
    def check(self, context: Dict[str, Any]) -> CheckResult: ...

class AsyncConfidenceCheck(Protocol):
    name: str
    weight: float
    async def check(self, context: Dict[str, Any]) -> CheckResult: ...
```

**5 Default Checks** (weights sum to 1.0):

| Check | Weight | What It Verifies |
|-------|--------|------------------|
| NoDuplicatesCheck | 0.25 | No existing implementations match task keywords |
| ArchitectureCheck | 0.25 | Proposed tech doesn't conflict with project stack |
| OfficialDocsCheck | 0.20 | Official documentation has been referenced |
| OssReferenceCheck | 0.15 | Working OSS implementations exist (3-tier lookup) |
| RootCauseCheck | 0.15 | Root cause is specific, evidenced, non-vague |

**Thresholds**:
- `>=90%`: Proceed with implementation
- `70-89%`: Present alternatives to user
- `<70%`: Ask clarifying questions

**Tech Stack Detection** (cached via `@lru_cache`):
- Scans `CLAUDE.md`, `pyproject.toml`, `package.json`
- Detects: Next.js, React, Vue, FastAPI, Django, Flask, Supabase, PostgreSQL, MongoDB, Turborepo, pytest
- Conflict matrix prevents incompatible technologies (e.g., React + jQuery, Supabase + custom_api)

**OSS Reference 3-Tier Verification**:
1. External URLs from reputable domains (github.com, stackoverflow.com, docs.python.org, etc.)
2. Local pattern cache (`docs/patterns/`, `.claude/patterns/`, `~/.claude/patterns/`)
3. Built-in pattern database (15 keyword→reference mappings: auth, jwt, api, crud, test, form, cache, queue, etc.)

**Data Classes**:
- `CheckResult(passed: bool, message: str, details: Dict)` — Individual check outcome
- `ConfidenceResult(score: float, checks: List[CheckResult], recommendation: str)` — Aggregate result
  - Implements `__float__()` and comparison operators for backward compatibility with raw float scores

**Context Enrichment** — After `assess()`, the context dict gains:
```python
context["confidence_checks"]        # List of status messages
context["potential_duplicates"]      # Matching files (if found)
context["detected_tech_stack"]       # {"frameworks": [], "databases": [], "tools": []}
context["architecture_conflicts"]    # Conflict descriptions
context["validated_oss_references"]  # Validated external refs
context["matched_oss_pattern"]       # Built-in database match
```

**Backward Compatibility** — Explicit flags bypass active verification:
```python
context = {"root_cause_identified": True}         # Skips heuristic
context = {"duplicate_check_complete": True}       # Skips search
context = {"architecture_check_complete": True}    # Skips detection
context = {"oss_reference_complete": True}         # Skips verification
```

---

### SelfCheckProtocol — Post-Implementation Validation

**File**: `src/superclaude/pm_agent/self_check.py`

Implements "The Four Questions" validation framework:

1. **Are all tests passing?** — Requires actual test output
2. **Are all requirements met?** — Lists each requirement
3. **No assumptions without verification?** — Shows documentation
4. **Is there evidence?** — Provides test results, code changes, validation

**7 Hallucination Red Flags** (detected automatically):
- "Tests pass" without showing output
- "Everything works" without evidence
- "Implementation complete" with failing tests
- Skipping error messages
- Ignoring warnings
- "Probably works" language
- Unverified claims about external services

**API**:
```python
protocol = SelfCheckProtocol()
passed, issues = protocol.validate(context)  # -> Tuple[bool, List[str]]
report = protocol.format_report(context)     # -> str (human-readable)
```

---

### ReflexionPattern — Cross-Session Error Learning

**File**: `src/superclaude/pm_agent/reflexion.py`

**Storage**:
- Solutions: `docs/memory/solutions_learned.jsonl` (append-only JSONL)
- Mistake docs: `docs/mistakes/` directory

**Matching Algorithm**:
- Uses Jaccard word overlap via `word_overlap_ratio()` from utils
- Match threshold: `0.7` (70% word overlap between error signatures)
- Signature creation: Combines error type + key context words

**API**:
```python
reflexion = ReflexionPattern()

# Look up past solutions
solution = reflexion.get_solution(error_info)  # Returns solution or None

# Record new error for future reference
reflexion.record_error(error_info)

# Aggregate statistics
stats = reflexion.get_statistics()
```

---

### TokenBudgetManager — Complexity-Based Allocation

**File**: `src/superclaude/pm_agent/token_budget.py`

**Complexity Levels**:

| Level | Token Budget | Use For |
|-------|-------------|---------|
| simple | 200 | Typo fixes, small tweaks |
| medium | 1,000 | Standard features, bug fixes |
| complex | 2,500 | Multi-file refactors, architecture changes |

**API**:
```python
budget = TokenBudgetManager(complexity="medium")
budget.allocate()               # Reset to level's limit
budget.use(150)                 # Deduct tokens
remaining = budget.remaining    # Property: tokens left
budget.reset()                  # Back to full allocation
```

---

## Execution Patterns

### ParallelExecutor — Wave→Checkpoint→Wave

**File**: `src/superclaude/execution/parallel.py`

**Core Classes**:
- `TaskStatus` — Enum: PENDING, RUNNING, COMPLETED, FAILED
- `Task` — Dataclass with dependency checking (`can_run()` checks all deps completed)
- `ParallelGroup` — Tasks that can run concurrently (no inter-dependencies)
- `ExecutionPlan` — Ordered list of groups with checkpoints
- `ParallelExecutor` — ThreadPoolExecutor-based execution engine

**Planning Algorithm**:
1. Topological sort of task dependency graph
2. Circular dependency detection (raises error)
3. Group independent tasks into parallel waves
4. Insert checkpoints between waves

**Convenience Functions**:
```python
# Quick parallel file operations
results = parallel_file_operations(operations)

# Check if parallelization is worthwhile (threshold=3)
if should_parallelize(operations):
    results = parallel_file_operations(operations)
```

**Performance**: 3.5x average speedup, up to 10x for large batches.

---

## Hooks System

### HookTracker — Session State Management

**File**: `src/superclaude/hooks/hook_tracker.py`

**Session ID Resolution** (in order):
1. `CLAUDE_SESSION_ID` environment variable
2. Cached session file
3. Generated SHA-256 hash

**Storage**: `~/.claude/.superclaude_hooks/hook_executions.json`

**Features**:
- `once: true` support — hooks execute only once per session
- 24-hour TTL — sessions auto-expire
- Thread-safe via `atomic_write_json()` from utils

**Key Functions**:
```python
should_execute_hook(hook_name)        # Check if hook should run
check_and_mark(hook_name)             # Atomic check-and-mark
cleanup_old_sessions()                # Remove expired sessions
get_session_stats()                   # Session diagnostics
```

### InlineHooks — Frontmatter Parser

**File**: `src/superclaude/hooks/inline_hooks.py`

Parses YAML frontmatter from skill/agent/command markdown files:

**Supported Fields**:
- `context: inline|fork` — Execution context
- `agent: <name>` — Agent type for skill
- `user-invocable: true|false` — Visibility in menu
- `allowed-tools: [...]` — Tool restrictions (supports wildcards)
- `hooks: {PreToolUse: [...]}` — Inline hook definitions

**Tool Filtering**: Supports exact match, wildcard patterns (`Bash(*)`), and agent patterns (`Task(AgentName)`).

### MCP Fallback — Graceful Degradation

**File**: `src/superclaude/hooks/mcp_fallback.py`

**10 MCP→Fallback Mappings**:

| MCP Server | Fallback |
|-----------|----------|
| context7 | Tavily / WebSearch |
| tavily | WebSearch (native) |
| sequential | Native reasoning |
| serena | Native search |
| morphllm | Edit (native) |
| magic | Write (native) |
| playwright | --chrome (native) |
| devtools | Playwright |
| mindbase | Serena memory |
| airis-agent | Native |

**Behavior**: First-notification-only per session — notifies once then silently falls back.

**Storage**: `~/.claude/.superclaude_hooks/mcp_fallbacks.json`

---

## Shared Utilities

**File**: `src/superclaude/utils/__init__.py`

### word_overlap_ratio(a, b) → float
Jaccard similarity coefficient for two strings. Used by ReflexionPattern for error signature matching.

### word_overlap_count(a, b) → int
Raw count of overlapping words between two strings.

### atomic_write_json(path, data)
Crash-safe JSON writes via temp file + `os.replace()`. Used by hook_tracker and mcp_fallback for thread-safe state persistence.

---

## CLI Commands Reference

**Entry**: `superclaude` (click-based)

| Command | Options | Purpose |
|---------|---------|---------|
| `install` | `--force`, `--list`, `--list-all`, `--scope user\|project` | Install components to ~/.claude/ or ./.claude/ |
| `uninstall` | `--scope`, `--dry-run`, `--yes`, `--keep-settings` | Remove installed components |
| `mcp` | `--servers`, `--list`, `--status`, `--scope`, `--dry-run` | MCP server configuration |
| `update` | `--scope` | Force reinstall (alias for install --force) |
| `install-skill` | `<name>` | Install individual skill |
| `doctor` | `--verbose` | Health check diagnostics |
| `agents` | `--list`, `--info <name>`, `--tokens`, `--scope` | Agent management |
| `skills` | `--list`, `--info <name>`, `--tokens`, `--scope` | Skill management |
| `version` | — | Show version |

**Installation Scopes**:
- `user` (default): `~/.claude/` — Global installation
- `project`: `./.claude/` — Project-specific

---

## Pytest Plugin

**Auto-loaded** after `uv pip install -e .` via pyproject.toml entry point.

### Fixtures

| Fixture | Type | Source |
|---------|------|--------|
| `confidence_checker` | `ConfidenceChecker` | pytest_plugin.py |
| `self_check_protocol` | `SelfCheckProtocol` | pytest_plugin.py |
| `reflexion_pattern` | `ReflexionPattern` | pytest_plugin.py |
| `token_budget` | `TokenBudgetManager` | pytest_plugin.py (reads `@pytest.mark.complexity`) |
| `pm_context` | Dict (all above) | pytest_plugin.py |

### Hooks

| Hook | Purpose |
|------|---------|
| `pytest_configure` | Register custom markers |
| `pytest_runtest_setup` | Confidence gating (skip if <70%) |
| `pytest_runtest_makereport` | Record failures to reflexion |
| `pytest_collection_modifyitems` | Auto-mark by directory (unit/integration) |
| `pytest_report_header` | Display SuperClaude version |

### Markers

| Marker | Purpose |
|--------|---------|
| `@pytest.mark.unit` | Auto-applied in tests/unit/ |
| `@pytest.mark.integration` | Auto-applied in tests/integration/ |
| `@pytest.mark.confidence_check` | Pre-execution assessment |
| `@pytest.mark.self_check` | Post-implementation validation |
| `@pytest.mark.reflexion` | Error learning |
| `@pytest.mark.complexity(level)` | Token budget (simple/medium/complex) |
| `@pytest.mark.hallucination` | Hallucination detection |
| `@pytest.mark.performance` | Benchmarks |

---

## Core Insights

### PM Agent ROI: 25-250x Token Savings

**Finding**: Pre-execution confidence checking has exceptional ROI.

- Spending 100-200 tokens on confidence check saves 5,000-50,000 tokens on wrong-direction work
- Real example: Checking for duplicate implementations before coding vs implementing duplicate feature

**When to use**: Unclear requirements, new codebase, complex features, bug fixes.
**When to skip**: Trivial changes, well-understood tasks, emergency hotfixes.

---

### Hallucination Detection: The Four Questions

The SelfCheckProtocol catches most AI hallucinations:

1. Are all tests passing? → REQUIRE actual output
2. Are all requirements met? → LIST each requirement
3. No assumptions without verification? → SHOW documentation
4. Is there evidence? → PROVIDE test results, code changes

**Bad**: "The API integration is complete and working correctly."
**Good**: "The API integration is complete. Test output: 3/3 tests passed in 1.2s."

---

### Parallel Execution: 3.5x Speedup

Wave → Checkpoint → Wave pattern:

```
Wave 1: Independent reads (parallel)   → ThreadPoolExecutor
Checkpoint: Analyze together            → Sequential
Wave 2: Independent edits (parallel)    → ThreadPoolExecutor
```

**Use for**: Multiple independent file reads, unrelated edits, parallel searches.
**Avoid for**: Operations with dependencies, sequential analysis, shared state mutations.

Performance diminishes after ~10 operations per wave.

---

## Common Pitfalls and Solutions

### Pitfall 1: Implementing Before Checking for Duplicates

**Problem**: Spent effort implementing feature that already exists.
**Solution**: Run `NoDuplicatesCheck` or search codebase first.
**Prevention**: `confidence_checker.assess()` before starting.

### Pitfall 2: Architecture Conflicts

**Problem**: Implemented custom API when project uses Supabase.
**Solution**: Read CLAUDE.md and check tech stack detection.
**Prevention**: `ArchitectureCheck` catches conflicts automatically.

### Pitfall 3: Skipping Test Output

**Problem**: Claimed tests passed but they were actually failing.
**Solution**: Always show actual `uv run pytest -v` output.
**Prevention**: `SelfCheckProtocol.validate()` requires evidence.

### Pitfall 4: UV Not Installed

**Problem**: Makefile requires `uv` but users don't have it.
**Solution**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS/Linux
pip install uv                                       # via pip
```

### Pitfall 5: Plugin Not Loaded

**Symptoms**: `fixture 'confidence_checker' not found`
**Solution**:
```bash
uv pip install -e ".[dev]"
uv run pytest --trace-config 2>&1 | grep superclaude
```

### Pitfall 6: ImportError in Tests

**Symptoms**: `ImportError: No module named 'superclaude'`
**Solution**: `uv pip install -e .` or use `uv run pytest` (creates venv automatically).

---

## Troubleshooting Guide

### Tests Not Found

```
ERROR: file or directory not found: tests/
```
**Fix**: `mkdir -p tests/unit tests/integration && touch tests/conftest.py`

### Fixtures Not Available

```
fixture 'confidence_checker' not found
```
**Fix**: Reinstall package: `uv pip install -e ".[dev]"`

### Hook Session Issues

**Symptoms**: `once: true` hooks re-executing every time
**Fix**: Check session ID resolution — ensure `CLAUDE_SESSION_ID` is set or cached file exists at `~/.claude/.superclaude_hooks/`.

### MCP Fallback Not Triggering

**Symptoms**: No fallback notification when MCP is unavailable
**Fix**: Check `~/.claude/.superclaude_hooks/mcp_fallbacks.json` — may have already notified (first-notification-only behavior). Delete the file to reset.

### Atomic Write Failures

**Symptoms**: `PermissionError` on hook state files
**Fix**: Check permissions on `~/.claude/.superclaude_hooks/` directory. The `atomic_write_json` function uses temp files + `os.replace()`, which requires write permissions in the target directory.

---

## Advanced Techniques

### Dynamic Fixture Configuration

```python
@pytest.fixture
def token_budget(request):
    """Adapts based on @pytest.mark.complexity marker"""
    marker = request.node.get_closest_marker("complexity")
    complexity = marker.args[0] if marker else "medium"
    return TokenBudgetManager(complexity=complexity)

@pytest.mark.complexity("simple")
def test_simple_feature(token_budget):
    assert token_budget.limit == 200
```

### Confidence-Driven Test Execution

```python
def pytest_runtest_setup(item):
    """Skip tests if confidence is too low"""
    marker = item.get_closest_marker("confidence_check")
    if marker:
        checker = ConfidenceChecker()
        context = build_context(item)
        confidence = checker.assess(context)
        if confidence < 0.7:
            pytest.skip(f"Confidence too low: {confidence:.0%}")
```

### Reflexion-Powered Error Learning

```python
def pytest_runtest_makereport(item, call):
    """Record failed tests for future learning"""
    if call.when == "call" and call.excinfo is not None:
        reflexion = ReflexionPattern()
        reflexion.record_error({
            "test_name": item.name,
            "error_type": type(call.excinfo.value).__name__,
            "error_message": str(call.excinfo.value),
        })
```

### Custom Confidence Checks

```python
class SecurityCheck:
    name = "security_audit"
    weight = 0.20

    def check(self, context):
        # Implements ConfidenceCheck protocol
        has_auth = "auth" in context.get("features", [])
        return CheckResult(passed=has_auth, message="Security reviewed")

checker = ConfidenceChecker()
checker.register(SecurityCheck())
```

---

## Token Usage Patterns

| Task Type | Typical Tokens | With PM Agent | Savings |
|-----------|---------------|---------------|---------|
| Typo fix | 200-500 | 200-300 | 40% |
| Bug fix | 2,000-5,000 | 1,000-2,000 | 50% |
| Feature | 10,000-50,000 | 5,000-15,000 | 60% |
| Wrong direction | 50,000+ | 100-200 (prevented) | 99%+ |

**Key insight**: Prevention (confidence check) saves more tokens than optimization.

### Index Performance

- **Before**: ~58,000 tokens (reading all files)
- **After**: ~3,000 tokens (reading PROJECT_INDEX)
- **Reduction**: 94%

---

## Framework Statistics (2026-01-27)

| Category | Count | Location |
|----------|-------|----------|
| Slash Commands | 30 | src/superclaude/commands/ |
| Agents | 20 | src/superclaude/agents/ |
| Modes | 7 (+INDEX) | src/superclaude/modes/ |
| MCP Servers | 10 | src/superclaude/mcp/configs/ |
| MCP Docs | 11 | src/superclaude/mcp/ |
| Core Configs | 7 | src/superclaude/core/ |
| Python Files | 44 | src/superclaude/ |
| Test Files | 14 | tests/ |
| Skills | 1 | src/superclaude/skills/ |
| CI Workflows | 4 | .github/workflows/ |

---

## Cross-Reference Index

| Need | File(s) |
|------|---------|
| CLI entry | cli/main.py |
| Pytest fixtures | pytest_plugin.py |
| Confidence assessment | pm_agent/confidence.py, skills/confidence-check/ |
| Post-validation | pm_agent/self_check.py |
| Error learning | pm_agent/reflexion.py |
| Token management | pm_agent/token_budget.py |
| Parallel execution | execution/parallel.py |
| Session tracking | hooks/hook_tracker.py |
| Frontmatter parsing | hooks/inline_hooks.py |
| MCP fallback | hooks/mcp_fallback.py |
| Shared utils | utils/__init__.py |
| Slash commands | commands/*.md |
| Agent definitions | agents/*.md |
| Mode behaviors | modes/*.md |
| MCP configs | mcp/configs/*.json |
| Core rules | core/RULES.md |
| Flag reference | core/FLAGS.md |

---

## Git Workflow

- **Branch**: `master` <- `integration` <- `feature/*`, `fix/*`, `docs/*`
- **Commits**: Conventional (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`)
- **Worktrees**: `git worktree add ../SuperClaude-feature feature/name`

---

## Lessons Learned

### Documentation Drift
README described features that didn't exist. **Fix**: Add warnings about planned vs implemented features; review docs during every release.

### Version Management
Multiple version numbers across files. **Fix**: Single source of truth in `pyproject.toml` (`__version__` in `__init__.py` mirrors it).

### Tests Are Non-Negotiable
Framework provided testing tools but initially had no tests itself. **Fix**: Comprehensive test suite (14 files) with CI/CD.

### Install Module Complexity
`install_commands.py` grew too large. **Fix**: Split into 4 focused modules (`install_mcp.py`, `install_paths.py`, `install_settings.py`, `install_components.py`).

### Thread Safety Matters
Hook state files corrupted under concurrent access. **Fix**: `atomic_write_json()` utility using temp files + `os.replace()`.

---

*This document grows with the project. Document solutions here when encountering and resolving problems.*

**Review frequency**: After major changes or quarterly
