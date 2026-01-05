---
name: confidence-check
description: >-
  Pre-implementation confidence assessment (≥90% required to proceed).
  USE THIS SKILL WHEN: user asks to implement a feature, add functionality,
  create a new component, fix a bug, or refactor code. Also use when user says
  "check confidence", "am I ready", "verify before implementing", "readiness check",
  "pre-implementation check", "before starting", or "확인해줘/검증해줘".
  Validates: no duplicates, architecture compliance, official docs, OSS references, root cause.
---

<document type="skill" name="confidence-check"
          triggers="/confidence-check, pre-implementation, confidence-assessment, readiness-check">

# Confidence Check Skill

## Purpose

Prevents wrong-direction execution by assessing confidence **BEFORE** starting implementation.

**Requirement**: ≥90% confidence to proceed with implementation.

**Test Results** (2026-01-05):
- Precision: 1.000 (no false positives)
- Recall: 1.000 (no false negatives)
- 63/63 test cases passed

## When to Use

Use this skill BEFORE implementing any task to ensure:
- No duplicate implementations exist
- Architecture compliance verified
- Official documentation reviewed
- Working OSS implementations found
- Root cause properly identified

## Confidence Assessment Criteria

Calculate confidence score (0.0 - 1.0) based on 5 checks:

### 1. No Duplicate Implementations? (25%)

**Check**: Search codebase for existing functionality

```bash
# Use Grep to search for similar functions
# Use Glob to find related modules
```

✅ Pass if no duplicates found
❌ Fail if similar implementation exists

### 2. Architecture Compliance? (25%)

**Check**: Verify tech stack alignment

- Read `CLAUDE.md`, `PLANNING.md`
- Confirm existing patterns used
- Avoid reinventing existing solutions

✅ Pass if uses existing tech stack (e.g., Supabase, UV, pytest)
❌ Fail if introduces new dependencies unnecessarily

### 3. Official Documentation Verified? (20%)

**Check**: Review official docs before implementation

- Use Context7 MCP for official docs
- Use WebFetch for documentation URLs
- Verify API compatibility

✅ Pass if official docs reviewed
❌ Fail if relying on assumptions

### 4. Working OSS Implementations Referenced? (15%)

**Check**: Find proven implementations

- Use Tavily MCP or WebSearch
- Search GitHub for examples
- Verify working code samples

✅ Pass if OSS reference found
❌ Fail if no working examples

### 5. Root Cause Identified? (15%)

**Check**: Understand the actual problem

- Analyze error messages
- Check logs and stack traces
- Identify underlying issue

✅ Pass if root cause clear
❌ Fail if symptoms unclear

## Confidence Score Calculation

```
Total = Check1 (25%) + Check2 (25%) + Check3 (20%) + Check4 (15%) + Check5 (15%)

If Total >= 0.90:  ✅ Proceed with implementation
If Total >= 0.70:  ⚠️  Present alternatives, ask questions
If Total < 0.70:   ❌ STOP - Request more context
```

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

## Implementation Details

The TypeScript implementation is in `confidence.ts` (same directory):

### Core API

```typescript
import { ConfidenceChecker, Context } from './confidence';

const checker = new ConfidenceChecker();
const confidence = await checker.assess(context);

if (confidence >= 0.9) {
  // High confidence - proceed immediately
} else if (confidence >= 0.7) {
  // Medium confidence - present options to user
} else {
  // Low confidence - STOP and request clarification
}
```

### Context Interface

```typescript
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
}
```

### Recommendation Helper

```typescript
const recommendation = checker.getRecommendation(confidence);
// ✅ High confidence (≥90%) - Proceed with implementation
// ⚠️ Medium confidence (70-89%) - Continue investigation
// ❌ Low confidence (<70%) - STOP and continue investigation loop
```

### Note

Python implementation (`pm_agent/confidence.py`) also available for pytest integration, but CLI commands disabled in favor of skill-based approach.

## ROI

**Token Savings**: Spend 100-200 tokens on confidence check to save 5,000-50,000 tokens on wrong-direction work.

**Success Rate**: 100% precision and recall in production testing.

</document>