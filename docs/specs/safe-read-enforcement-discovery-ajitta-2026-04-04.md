---
status: draft
revised: 2026-04-04
---

# Safe Read Enforcement — Discovery Spec

## Problem

Token explosion observed during sessions, suspected Claude bug causing full file reads without pagination. Current safeguards are insufficient:

- **file_size_guard.py** only blocks >80KB — too late, tokens already wasted on 30-70KB files
- **R16 (Safe Read)** is a soft guideline (🟡) — model often ignores it
- **R17 (Serena-First)** is 🟢 priority — not strong enough to prevent unnecessary full reads of code files

## Solution: 3-Layer Enforcement

### Layer 1: Hook (Hard Block) — file_size_guard.py

**Change:** Lower threshold from 80KB to 30KB. Rationale change: 30KB is a proactive token conservation threshold, not a safety buffer against CC's 25K token hard limit.

| Parameter | Before | After |
|-----------|--------|-------|
| `SIZE_THRESHOLD` | 80,000 (80KB) | 30,000 (30KB) |
| Bypass | `limit` parameter present | `limit` parameter present |
| Bypass | *(none)* | **`pages` parameter present** (PDF pagination) |
| Bypass | Binary extensions | Binary extensions |
| Bypass | *(none)* | **File <5KB** |
| Bypass | *(none)* | **Config extensions <30KB** (`.json`, `.yaml`, `.yml`, `.toml`, `.cfg`, `.ini`, `.env`) |

**Behavior:** Read call without `limit`/`pages` on a file >30KB (and not exempt) → block with context-aware suggestion:
- Code files (`.py`, `.ts`, `.js`, etc.): suggest `limit=500` or Grep
- JSON/data files (`.json`): suggest `jq` for field queries, `limit` for pagination
- Other: suggest `limit=500` or Grep

**Block message examples:**
```
# Code file
File is 45KB (.py) — use limit parameter (e.g., limit=500) or Grep to search for specific content.

# JSON file
File is 250KB (.json) — use jq to query specific fields (e.g., jq '.key' file.json) or Read with limit parameter (e.g., limit=500).
```

**5-30KB code file gap (intentional):** Code files between 5-30KB are blocked without `limit`. This is by design — the goal is to push the model toward Serena symbolic tools or Grep for code exploration. The `limit` parameter is always available as an escape hatch.

### Layer 2: Rule (Soft Guide) — R16 Strengthening

**Before:**
```
[R16 Safe Read] Safe Read 🟡: files of unknown size → use limit parameter or check wc -c first;
logs, transcripts, changelogs (>80KB) → prefer Grep or Bash over Read;
plan files → keep under 15KB, split into phases for large implementations
```

**After:**
```
[R16 Safe Read] Safe Read 🟡: always use limit parameter for files of unknown size (hook blocks >30KB without limit);
small files (<5KB) auto-exempt; config formats (.json, .yaml, .yml, .toml, .cfg, .ini, .env) exempt <30KB;
large JSON/data files → use jq for field queries instead of Read;
logs, transcripts, changelogs → prefer Grep over Read;
plan files → keep under 15KB, split into phases for large implementations
```

Key changes:
- Threshold reference updated: 80KB → 30KB
- "prefer Grep or Bash" → "prefer Grep" (Bash read is also wasteful)
- Config exemption documented with full extension list
- Hook enforcement referenced (model knows the hook exists)
- Large JSON guidance: `jq` for field queries added

### Layer 3: Serena-First Upgrade — R17

**Before:**
```
[R17 Symbolic-First] Serena-First 🟢: code exploration → prefer Serena symbolic tools ...
```

**After:**
```
[R17 Symbolic-First] Serena-First 🟡: code exploration fallback chain:
  1. Serena symbolic tools (get_symbols_overview, find_symbol) — primary
  2. Grep with targeted patterns — fallback for structural/text patterns
  reserve Read for non-code files, unknown formats, or when all above insufficient
```

Key changes:
- 🟢 → 🟡 (optimization → strong preference)
- Explicit fallback chain: Serena → Grep

## Exemption Design

```
EXEMPT if ANY:
  1. limit parameter already set
  2. pages parameter already set (PDF pagination)
  3. binary extension (existing logic)
  4. file_size < 5,000 bytes (5KB)
  5. config extension AND file_size < 30,000 bytes (30KB)
     extensions: {.json, .yaml, .yml, .toml, .cfg, .ini, .env}
```

Rationale: Small files (<5KB) and small config files (<30KB) are legitimately read in full. Large config files (e.g., `package-lock.json` at several MB) must still use `limit`. Code files >5KB should use Serena, Grep, or Read with `limit`.

## Files to Modify

| File | Change |
|------|--------|
| `src/superclaude/scripts/file_size_guard.py` | Threshold 80K→30K, add pages bypass, <5KB + config exemptions, context-aware block messages |
| `src/superclaude/core/RULES.md` | R16 text update, R17 🟢→🟡 |
| `src/superclaude/hooks/hooks.json` | Update `_comment`: 80KB→30KB, rationale: token conservation (not CC hard limit) |
| `tests/unit/test_file_size_guard.py` | **New file** — unit tests for all exemption paths and block messages |

## Test Plan — test_file_size_guard.py

| Test | Input | Expected |
|------|-------|----------|
| Code file >30KB, no limit | 35KB `.py` file | block with code suggestion |
| JSON file >30KB, no limit | 35KB `.json` file | block with jq suggestion |
| Code file >30KB, with limit | 35KB `.py`, limit=500 | approve |
| PDF >30KB, with pages | 35KB `.pdf`, pages="1-5" | approve |
| Small file, no limit | 3KB `.py` file | approve (small file exempt) |
| Config <30KB, no limit | 20KB `.yaml` file | approve (config exempt) |
| Config >30KB, no limit | 500KB `.json` (package-lock) | block |
| Binary file | 1MB `.png` file | approve (binary exempt) |
| Env var disabled | SUPERCLAUDE_SIZE_GUARD=0 | approve |
| No file_path | empty input | approve (fail open) |

## Risks

- **5-30KB code file friction (intentional):** Code files in this range are blocked without `limit`. This is the desired behavior — pushes model toward Serena/Grep. The `limit` parameter is the escape hatch.
- **Serena unavailable:** R17 has explicit fallback chain (Grep). No gap.
- **Large config files:** Config extensions are only exempt below 30KB. Files like `package-lock.json` (several MB) are correctly blocked.
- **Config false negatives:** Non-standard config extensions (`.conf`, `.properties`) not exempt. Can add later if needed.

## Verification

```bash
# Unit tests (new)
uv run python -m pytest tests/unit/test_file_size_guard.py -v

# Existing tests (regression check)
uv run python -m pytest tests/unit/test_install_settings.py -v

# Manual verification
# Read a 35KB .py file without limit → should block (code suggestion)
# Read a 35KB .json file without limit → should block (jq suggestion)
# Read a 3KB file without limit → should pass (small file exempt)
# Read a 20KB .yaml file without limit → should pass (config exempt <30KB)
# Read a 35KB .py file with limit=500 → should pass
# Read a 35KB .pdf file with pages="1-5" → should pass
```
