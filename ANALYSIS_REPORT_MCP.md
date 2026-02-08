# MCP Directory Analysis Report

**Target:** `src/superclaude/mcp/`
**Date:** 2026-02-07
**Flags:** `--seq --effort max --tavily --c7 --orchestrate`

---

## Executive Summary

The `src/superclaude/mcp/` directory contains MCP server documentation (10 .md files) and configuration templates (11 .json files). Analysis reveals **2 critical issues**, **4 high-priority issues**, and **7 medium/low findings**.

| Domain | Findings | Critical | High | Medium | Low |
|--------|----------|----------|------|--------|-----|
| Security | 2 | 1 | 1 | 0 | 0 |
| Architecture | 4 | 1 | 2 | 1 | 0 |
| Quality | 6 | 0 | 1 | 3 | 2 |
| Performance | 2 | 0 | 0 | 1 | 1 |
| **Total** | **14** | **2** | **4** | **5** | **3** |

---

## Critical Findings (P0)

### SEC-001: API Key Exposed in URL
**Severity:** 🔴 Critical | **File:** `mcp/configs/tavily.json`, `cli/install_mcp.py`

**Issue:** Tavily API key is embedded in URL query parameter:
```json
"https://mcp.tavily.com/mcp/?tavilyApiKey=${TAVILY_API_KEY}"
```

**Risk:**
- API keys in URLs can be logged by proxies, load balancers, and server access logs
- Browser history, referrer headers may leak credentials
- Violates OWASP API Security guidelines

**Current Behavior (install_mcp.py:269-275):**
```python
if api_key and server_info.get("api_key_in_url"):
    url_param = server_info.get("api_key_url_param", api_key_env)
    if "?" in command:
        command = f"{command}&{url_param}={api_key}"
    else:
        command = f"{command}?{url_param}={api_key}"
```

**Recommendation:** Tavily MCP now supports OAuth and header-based authentication. Update to use:
1. OAuth flow (preferred for user-facing)
2. Header-based auth via `x-mcp-auth` or `Authorization` header
3. At minimum, document the risk and provide env-var-only guidance

---

### ARCH-001: Dual Source of Truth Creates Drift
**Severity:** 🔴 Critical | **Files:** `mcp/configs/*.json`, `cli/install_mcp.py`

**Issue:** MCP server definitions exist in two locations with inconsistencies:

| Server | mcp/configs/*.json | cli/install_mcp.py MCP_SERVERS |
|--------|-------------------|-------------------------------|
| context7 | `@upstash/context7-mcp@latest` | `@upstash/context7-mcp` (no @latest) |
| serena | Uses uvx + git URL | Same but different flags |
| serena-docker | ✅ Exists | ❌ Missing |
| airis-agent | ✅ Exists (deprecated) | ❌ Missing |
| mindbase | ✅ Exists (deprecated) | ❌ Missing |

**Evidence:** `mcp/configs/*.json` files are **not imported** anywhere in the codebase - `install_mcp.py` uses hardcoded `MCP_SERVERS` dict.

**Recommendation:**
1. **Option A (Preferred):** Delete `mcp/configs/` directory entirely; use `MCP_SERVERS` as single source
2. **Option B:** Generate `MCP_SERVERS` from JSON configs at build time
3. **Option C:** Move configs to single `mcp_registry.json` and have install_mcp.py read it

---

## High Priority Findings (P1)

### QUAL-001: Deprecated Files Still Shipped
**Severity:** 🟡 High | **Files:** `MCP_Airis-Agent.md`, `MCP_Mindbase.md`, `configs/airis-agent.json`, `configs/mindbase.json`

**Issue:** Files explicitly marked deprecated still included in package distribution:
```xml
<deprecated>Standalone airis-agent is deprecated. Use airis-mcp-gateway instead...</deprecated>
```

**Impact:**
- Token waste when loaded (~75 lines total)
- User confusion
- Maintenance burden

**Recommendation:** Move to `mcp/deprecated/` or remove entirely with migration note in CHANGELOG.

---

### ARCH-002: JSON Configs Appear Unused (Dead Code)
**Severity:** 🟡 High | **Directory:** `mcp/configs/`

**Evidence:**
- No imports of `mcp/configs/*.json` found in codebase
- `cli/install_mcp.py` defines servers inline
- `configs/__init__.py` is empty

**Impact:** 11 JSON files (~200 lines) with no functional purpose.

**Recommendation:** Remove directory if Option A chosen in ARCH-001.

---

### ARCH-003: Inconsistent Naming Across Components
**Severity:** 🟡 High | **Multiple Files**

| Component | Name Used |
|-----------|-----------|
| JSON config | `morphllm-fast-apply` |
| install_mcp.py | `morphllm-fast-apply` |
| FLAGS.md | `--morph\|--morphllm` |
| mcp_fallback.py | `morphllm` |
| context_loader.py | Special mapping needed |

Similar issues with `sequential-thinking` vs `sequential` vs `--seq`.

**Recommendation:** Standardize on canonical names; create mapping layer in one place.

---

### SEC-002: No Dependency Version Pinning
**Severity:** 🟡 High | **File:** `cli/install_mcp.py`

**Issue:** MCP servers installed via `npx -y` pull latest versions:
```python
"command": "npx -y @playwright/mcp@latest",
"command": "npx -y @21st-dev/magic",  # No version at all
```

**Risk:** Supply chain attacks, breaking changes in dependencies.

**Recommendation:**
1. Pin to specific versions: `@playwright/mcp@1.2.3`
2. Document version compatibility matrix
3. Add `--integrity` checks where supported

---

## Medium Priority Findings (P2)

### QUAL-002: Inconsistent Documentation Structure
**Severity:** 🟢 Medium | **Files:** All `MCP_*.md`

| File | Lines | Sections |
|------|-------|----------|
| MCP_Tavily.md | 87 | choose, capabilities, synergy, tools, patterns, flows, strategies, errors, examples |
| MCP_Context7.md | 30 | choose, synergy, examples |
| MCP_Sequential.md | 35 | choose, synergy, examples |

**Recommendation:** Define standard template with required sections (choose, synergy, tools, errors, examples).

---

### QUAL-003: JSON Schema Missing
**Severity:** 🟢 Medium | **Directory:** `mcp/configs/`

**Issue:** No JSON schema for config validation. Inconsistent fields:
- `magic.json` has `"type": "stdio"` field
- Others lack `type` field
- Inconsistent env var patterns: `"${VAR}"` vs `""`

**Recommendation:** If keeping JSON configs, add `mcp-config.schema.json`.

---

### QUAL-004: Syntax/Formatting Issues
**Severity:** 🟢 Medium | **File:** `mcp/configs/serena.json`

```json
{
  "serena": {
      "command": "uvx",
      "args": [...]
    }  // Inconsistent indentation
  }

```
Trailing newline and inconsistent indentation.

---

### PERF-001: Platform-Specific Path
**Severity:** 🟢 Medium | **File:** `mcp/configs/morphllm.json`

```json
"args": ["@morph-llm/morph-fast-apply", "/home/"]
```

Hardcoded Unix path; won't work on Windows.

---

### ARCH-004: Complex Indirection Chain
**Severity:** 🟢 Medium | **Multiple Files**

Flag → trigger → context_loader → mcp_fallback → actual tool requires understanding 4+ files.

**Observation:** Design is sound for maintainability but increases cognitive load. Document the flow.

---

## Low Priority Findings (P3)

### QUAL-005: Variable Documentation Depth
**Severity:** 🟢 Low

MCP_Tavily.md is exemplary; others could benefit from similar depth.

### PERF-002: No Package Integrity Verification
**Severity:** 🟢 Low

`npx -y` installs packages without checksum verification.

### QUAL-006: Chrome-DevTools Unique <flags> Tag
**Severity:** 🟢 Low | **File:** `MCP_Chrome-DevTools.md`

Only file with `<flags>` in `<role>` section. Inconsistent but harmless.

---

## Recommendations Summary

| Priority | Action | Impact | Effort |
|----------|--------|--------|--------|
| P0 | Migrate Tavily to header-based auth | Security | Medium |
| P0 | Unify server definitions (remove mcp/configs/) | Maintainability | Low |
| P1 | Remove/archive deprecated files | Token savings | Low |
| P1 | Standardize naming (mapping layer) | Developer experience | Medium |
| P1 | Pin dependency versions | Security | Low |
| P2 | Create MCP doc template | Consistency | Low |
| P2 | Add JSON schema if keeping configs | Validation | Low |

---

## Appendix: File Inventory

### Markdown Documentation (10 files)
| File | Lines | Status |
|------|-------|--------|
| MCP_Context7.md | 30 | Active |
| MCP_Magic.md | 33 | Active |
| MCP_Morphllm.md | 34 | Active |
| MCP_Playwright.md | 34 | Active |
| MCP_Serena.md | 34 | Active |
| MCP_Chrome-DevTools.md | 39 | Active |
| MCP_Sequential.md | 35 | Active |
| MCP_Tavily.md | 87 | Active |
| MCP_Airis-Agent.md | 31 | Deprecated |
| MCP_Mindbase.md | 37 | Deprecated |

### JSON Configs (11 files)
| File | Status | Used By |
|------|--------|---------|
| context7.json | Active | None (unused) |
| magic.json | Active | None |
| morphllm.json | Active | None |
| playwright.json | Active | None |
| serena.json | Active | None |
| serena-docker.json | Active | None |
| sequential.json | Active | None |
| tavily.json | Active | None |
| chrome-devtools.json | Active | None |
| airis-agent.json | Deprecated | None |
| mindbase.json | Deprecated | None |

---

## Handoff

For implementing fixes:
- **Quality improvements:** `/sc:improve mcp/ --focus quality`
- **Dead code removal:** `/sc:cleanup mcp/configs/`
- **Security fixes:** `/sc:implement --feature "Tavily header auth migration"`

---

*Generated by /sc:analyze with --seq --effort max --tavily --c7 --orchestrate*
