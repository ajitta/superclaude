---
status: reviewed
revised: 2026-04-04
---

# ast-grep MCP Integration — Implementation Plan

**Goal:** Add ast-grep MCP as 9th managed server with install, flags, docs, and rules integration
**Architecture:** Registry entry + JSON config (reference) + MCP doc + context_loader triggers
**Spec:** `docs/specs/ast-grep-mcp-integration-discovery-chosh1179-2026-04-04.md`
**Review:** self-review + simplicity-guide applied — agent updates (Tasks 8-10) deferred to post-usage

---

## Phase 1: Infrastructure (install flow)

### Task 1: Create config file
**Files:** Create: `src/superclaude/mcp/configs/ast-grep.json`
- [ ] Create `ast-grep.json` following `serena.json` pattern (uvx + git+ URL)
- [ ] Content: `{"ast-grep": {"command": "uvx", "args": ["--from", "git+https://github.com/ast-grep/ast-grep-mcp", "ast-grep-server"]}}`
- [ ] Note: configs/ JSON is reference-only — actual registry is inline `MCP_SERVERS` dict in `install_mcp.py`

### Task 2: Add registry entry + prereq check
**Files:** Modify: `src/superclaude/cli/install_mcp.py`
- [ ] Add `"ast-grep"` entry to `MCP_SERVERS` dict (before closing `}` at line 86):
  ```python
  "ast-grep": {
      "name": "ast-grep",
      "description": "Structural AST pattern search and code analysis using tree-sitter",
      "transport": "stdio",
      "command": "uvx --from git+https://github.com/ast-grep/ast-grep-mcp ast-grep-server",
      "required": False,
  },
  ```
- [ ] Add ast-grep binary prereq check in `check_prerequisites()` (after uv check, line ~186). Check both `sg` (canonical) and `ast-grep` (alias):
  ```python
  # Check ast-grep binary for AST-based MCP server (optional)
  _ast_grep_found = False
  for binary in ["sg", "ast-grep"]:
      try:
          result = _run_command(
              [binary, "--version"], capture_output=True, text=True, timeout=10
          )
          if result.returncode == 0:
              _ast_grep_found = True
              break
      except (subprocess.TimeoutExpired, FileNotFoundError):
          continue
  if not _ast_grep_found:
      click.echo("⚠️  ast-grep not found - required for ast-grep MCP server", err=True)
      click.echo("   Install: brew install ast-grep (macOS) | cargo install ast-grep --locked | npm i -g @ast-grep/cli", err=True)
  ```
- [ ] Verify: `uv run python -c "from superclaude.cli.install_mcp import MCP_SERVERS; assert 'ast-grep' in MCP_SERVERS; print(f'Registry: {len(MCP_SERVERS)} servers')"` → should print 9

---

## Phase 2: Documentation

### Task 3: Create MCP documentation
**Files:** Create: `src/superclaude/mcp/MCP_AstGrep.md`
- [ ] Follow `MCP_Morphllm.md` pattern: `<component name="ast-grep" type="mcp">`
- [ ] Include: role/mission, choose (use/avoid), decision rule table (ast-grep vs Serena vs Grep), workflow (dump → test → find), integration patterns, examples, bounds, handoff
- [ ] Key decision rule: structural patterns → ast-grep, symbol navigation → Serena, text search → Grep
- [ ] Target size: ~50-70 lines (Morphllm is 69 lines)

### Task 4: Update MCP README
**Files:** Modify: `src/superclaude/mcp/README.md`
- [ ] Add ast-grep row to "Available MCP Servers" table (after Morphllm, line ~21): `| ast-grep | \`--sg\` | Structural AST pattern search via tree-sitter |`
- [ ] Add coordination matrix entries (line ~43):
  - `Serena → ast-grep | Symbol context → structural pattern validation`
  - `ast-grep → Morphllm | Patterns found → bulk transformations executed`

---

## Phase 3: Flag System

### Task 5: Update FLAGS.md
**Files:** Modify: `src/superclaude/core/FLAGS.md`
- [ ] Add `--sg|--ast-grep` line in `<mcp>` section (after `--tvly` line 25, before `--frontend-verify`):
  ```
  --sg|--ast-grep: structural patterns, AST search, anti-patterns → ast-grep tree-sitter code analysis
  ```

### Task 6: Update context_loader.py
**Files:** Modify: `src/superclaude/scripts/context_loader.py`
- [ ] Add TRIGGER_MAP entry (after morphllm entry, line ~109):
  ```python
  (r"(--sg|--ast-grep|ast.?grep|syntax.?tree|structural.?pattern|structural.?search)", "mcp/MCP_AstGrep.md", 2),
  ```
- [ ] Add TIER_0_MAP entry (after morphllm entry, line ~181):
  ```python
  "mcp/MCP_AstGrep.md": "ast-grep: structural AST search. dump_syntax_tree → test_match_code_rule → find_code. Use for code patterns beyond text grep.",
  ```
- [ ] Add to `--all-mcp` COMPOSITE_FLAGS (line ~144):
  ```python
  ("mcp/MCP_AstGrep.md", 2),
  ```
- [ ] Add FLAG_ALIASES entry (line ~209):
  ```python
  "astgrep": ["ast-grep"],
  ```
- [ ] **Add to VALID_FLAGS set** (line ~238-246): add `"sg"`, `"ast-grep"` to the set

---

## Phase 4: Rules

### Task 7: Update RULES.md [R17]
**Files:** Modify: `src/superclaude/core/RULES.md`
- [ ] Line 43 (the [R17] line): Change `(if configured)` → remove parenthetical, add role clarification:
  - Find: `ast-grep MCP (if configured) — structural AST search fallback`
  - Replace: `ast-grep MCP — structural AST search fallback; primary for pattern matching`

---

## Deferred (post-usage)

Agent tool_guidance updates for refactoring-expert, quality-engineer, security-engineer — add `<mcp servers="sg"/>` and ast-grep directives when usage patterns emerge. Per simplicity review: no agents currently have `<mcp>` tags; no failure scenario without them; trivially addable later (2-line edit per agent).

---

## Verification

```bash
# Phase 1 — registry
uv run python -c "from superclaude.cli.install_mcp import MCP_SERVERS; assert 'ast-grep' in MCP_SERVERS; print(f'Registry: {len(MCP_SERVERS)} servers')"

# Phase 2 — files exist
ls src/superclaude/mcp/MCP_AstGrep.md src/superclaude/mcp/configs/ast-grep.json

# Phase 3 — context_loader loads without error + VALID_FLAGS includes new flags
uv run python -c "from superclaude.scripts.context_loader import TRIGGER_MAP, TIER_0_MAP, COMPOSITE_FLAGS, VALID_FLAGS; assert 'sg' in VALID_FLAGS; assert 'ast-grep' in VALID_FLAGS; print('context_loader OK')"

# Phase 3 — content structure validation
uv run pytest tests/unit/test_content_structure.py -v -k "mcp" --tb=short

# Full test suite baseline
uv run pytest tests/unit/ --tb=no -q
```
