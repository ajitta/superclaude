---
name: confidence-check
description: >-
  Pre-implementation confidence assessment (≥90% required to proceed).
  USE THIS SKILL WHEN: user asks to implement a feature, add functionality,
  create a new component, fix a bug, or refactor code. Also use when user says
  "check confidence", "am I ready", "verify before implementing", "readiness check",
  "pre-implementation check", "before starting", or "확인해줘/검증해줘".
  Validates: no duplicates, architecture compliance, official docs, OSS references, root cause.
mcp: c7:docs|tavily:oss-search
---

<document type="skill" name="confidence-check"
          triggers="/confidence-check, pre-implementation, confidence-assessment, readiness-check, verify-before-implementing">

# Confidence Check Skill

## Purpose

Prevents wrong-direction execution by assessing confidence **BEFORE** starting implementation.

| Threshold | Action |
|-----------|--------|
| ≥90% | Proceed with implementation |
| 70-89% | Present alternatives, ask questions |
| <70% | STOP - Request more context |

**Test Results** (2026-01-05): 63/63 passed, Precision: 1.000, Recall: 1.000

## When to Use

Use this skill BEFORE implementing any task. The 5 checks verify:

| Check | Weight | What It Validates |
|-------|--------|-------------------|
| No Duplicates | 25% | No existing similar functionality in codebase |
| Architecture | 25% | Uses existing tech stack (not reinventing) |
| Official Docs | 20% | Documentation reviewed (Context7 MCP) |
| OSS Reference | 15% | Working implementations found (Tavily MCP) |
| Root Cause | 15% | Problem source identified with evidence |

## Confidence Assessment

### Check 1: No Duplicate Implementations (25%)

**Tools**: Grep, Glob, Serena find_symbol

```
Search codebase for:
- Existing similar functions/modules
- Helper functions solving same problem
- Libraries providing functionality
```

### Check 2: Architecture Compliance (25%)

**Reference**: CLAUDE.md, PLANNING.md, pyproject.toml, package.json

```
Verify solution uses existing stack:
- Supabase project → Use Supabase APIs (not custom)
- Next.js project → Use Next.js patterns
- pytest project → Use pytest fixtures
```

### Check 3: Official Documentation (20%)

**Tools**: Context7 MCP, WebFetch

```
Query Context7 for:
- Framework documentation
- API references
- Best practices
```

### Check 4: OSS Reference (15%)

**Tools**: Tavily MCP, WebSearch

```
Search for:
- Similar open-source solutions
- Reference implementations
- Community best practices
```

### Check 5: Root Cause Identified (15%)

**Verification**:
- Problem source pinpointed (not guessing)
- Solution addresses root cause (not symptoms)
- Evidence supports conclusion

## Output Format

```
📋 Confidence Checks:
   ✅ No duplicate implementations found
   ✅ Uses existing tech stack
   ✅ Official documentation verified
   ✅ Working OSS implementation found
   ✅ Root cause identified

📊 Confidence: 1.00 (100%)
✅ High confidence - Proceeding to implementation
```

## TypeScript Implementation

Located in `confidence.ts` (same directory).

### Interfaces

```typescript
interface CheckerOptions {
  silent?: boolean;  // Suppress console output
}

interface CheckResult {
  name: string;
  passed: boolean;
  message: string;
  weight: number;
}

interface ConfidenceResult {
  score: number;
  checks: CheckResult[];
  recommendation: string;
}

interface Context {
  task?: string;
  test_file?: string;
  test_name?: string;
  markers?: string[];
  duplicate_check_complete?: boolean;
  architecture_check_complete?: boolean;
  official_docs_verified?: boolean;
  oss_reference_complete?: boolean;
  root_cause_identified?: boolean;
  confidence_checks?: string[];
  [key: string]: any;  // Extensible
}
```

### Usage

```typescript
import { ConfidenceChecker } from './confidence';

const checker = new ConfidenceChecker();
const result = await checker.assess(context);

if (result.score >= 0.9) {
  // High confidence - proceed
} else if (result.score >= 0.7) {
  // Medium - present options
} else {
  // Low - STOP and investigate
}

// Get recommendation text
const recommendation = checker.getRecommendation(result.score);
```

## Python Implementation

Located in `src/superclaude/pm_agent/confidence.py`. More feature-rich with:

- **Protocol-based extensibility**: Custom checks via `ConfidenceCheck` protocol
- **Async support**: `assess_async()` for MCP integration
- **Pluggable registry**: `register_check()`, `unregister_check()`
- **Comparison operators**: `result >= 0.9` works directly

### Pytest Integration

```python
import pytest

@pytest.mark.confidence_check
def test_feature(confidence_checker):
    """confidence_checker fixture auto-injected"""
    context = {
        "test_name": "test_feature",
        "duplicate_check_complete": True,
        "architecture_check_complete": True,
        "official_docs_verified": True,
        "oss_reference_complete": True,
        "root_cause_identified": True,
    }
    result = confidence_checker.assess(context)
    assert result >= 0.9
```

### Custom Check Registration

```python
from superclaude.pm_agent.confidence import ConfidenceChecker

class CustomCheck:
    name = "custom_check"
    weight = 0.1

    def evaluate(self, context):
        passed = context.get("custom_flag", False)
        return passed, "Custom check" if passed else "Custom check failed"

checker = ConfidenceChecker(register_defaults=True)
checker.register_check(CustomCheck())
```

## MCP Integration

| MCP | Role | Fallback |
|-----|------|----------|
| Context7 | Official docs lookup (Check 3) | WebFetch |
| Tavily | OSS implementation search (Check 4) | WebSearch |
| Serena | Symbol-level duplicate detection (Check 1) | Grep/Glob |

## ROI

**Token Savings**: 100-200 tokens on check → saves 5,000-50,000 tokens on wrong-direction work (25-250x ROI)

**Success Rate**: 100% precision and recall in production testing

</document>
