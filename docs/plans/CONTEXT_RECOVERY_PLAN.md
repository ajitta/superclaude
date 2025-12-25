# Context Recovery System - Implementation Plan

**Based on**: "LLMs Get Lost in Multi-Turn Conversation" (arXiv:2505.06120)
**Created**: 2025-12-25
**Status**: Planning Complete, Pending Implementation

---

## Problem Statement

| User Pain | Research Root Cause | Detection Signal |
|-----------|--------------------|--------------------|
| Over-engineering | Self-Reinforcement Bias | Complexity ratio > 2.0 |
| Context exhaustion | Early Assumption Making | Context usage > 75% |
| Scope creep | Premature Solution Attempts | Files created > requested |

**Key Insight**: Over-engineering → Context bloat → "Context window exhaustion" 체감

---

## Research Summary

### Core Finding
- **39% performance degradation** in multi-turn vs single-turn
- All models affected equally (GPT-4, Claude, Gemini, small models)
- Degradation is **deterministic**, not random

### Best Mitigation
- **CONCAT-AND-RETRY**: ~80%+ recovery rate
- Convert multi-turn → single-turn with consolidated context
- Manager-Worker architecture with fresh contexts

---

## Solution Design

### Architecture: Skill-Based (Not Python Package)

**Rationale**:
| Python Package | Claude Skill |
|---------------|--------------|
| 설치 필요 | ~/.claude/commands/ 복사만 |
| 의존성 관리 | 없음 |
| 업데이트 복잡 | 파일 교체 |
| 별도 런타임 | Claude 내장 기능 활용 |

### File Structure

```
src/superclaude/skills/
├── sc-context-check.md      # /sc:context-check
├── sc-context-restart.md    # /sc:context-restart
└── sc-context-status.md     # /sc:context-status

~/.claude/ (installed via superclaude install)
├── commands/
│   ├── sc-context-check.md
│   ├── sc-context-restart.md
│   └── sc-context-status.md
└── MODE_Context_Recovery.md
```

---

## Skill Specifications

### 1. /sc:context-check (Primary)

**Purpose**: Analyze current conversation health + auto-suggest

**Functions**:
- Complexity ratio calculation (conversation analysis)
- Context usage estimation
- Turn count tracking
- 🟢/🟡/🔴 status display
- Warning → restart suggestion

**Complexity Ratio Formula**:
```
Input Score = task_words × scope_weight × requirement_count
Output Score = LOC + (files × 10) + (abstractions × 15) + (deps × 5)

Ratio = Output / Input

🟢 < 2.0: Normal
🟡 2.0-3.0: Warning (auto-suggest)
🔴 > 3.0: Critical (strong suggest)
```

**Output Format**:
```
┌──────────────────────────────────────────┐
│ ⚠️ Context Health Warning                 │
├──────────────────────────────────────────┤
│ Complexity: 2.8x │ Context: 68% │ Turn: 5│
│ Trend: ↗️ rising                          │
├──────────────────────────────────────────┤
│ 💡 Restart recommended (~45% savings)    │
│ [Continue] [Restart] [Details]           │
└──────────────────────────────────────────┘
```

### 2. /sc:context-restart

**Purpose**: Execute CONCAT-AND-RETRY pattern

**Functions**:
- Extract requirements from current conversation
- Generate high-signal summary
- Output "Copy this to new conversation" format

**Output Format**:
```markdown
## Task Summary (CONCAT-AND-RETRY)

**Original Request**: [extracted]
**Confirmed Requirements**: [bullet list]
**Current State**: [file state summary]
**Blockers/Issues**: [if any]

---
Copy above to new conversation for fresh context.
```

### 3. /sc:context-status

**Purpose**: Quick inline status check

**Functions**:
- Lightweight health indicator
- No detailed analysis
- For frequent monitoring

**Output**: Single line status
```
Context: 🟢 Healthy | Turn: 2 | Complexity: 1.2x
```

### 4. MODE_Context_Recovery.md

**Purpose**: Automatic monitoring activation

**Triggers**:
- Turn 3+ → auto context check consideration
- Over-engineering pattern detection → warning
- Context 75%+ → notification

**Behavioral Changes**:
- Inject context awareness into responses
- Self-check before complex implementations
- Suggest restart when thresholds exceeded

---

## Detection Heuristics

### Over-Engineering Signals (Behavioral)

```yaml
complexity_indicators:
  abstraction_creep:
    - Creating base classes for single implementations
    - Factory patterns for 1-2 variants
    - Dependency injection for simple functions
    - Generic types where concrete suffices

  scope_expansion:
    - "for future extensibility"
    - "in case we need"
    - "might want to later"
    - Adding config options not requested

  file_explosion:
    - Helper files not in original scope
    - Utility modules for one-time use
    - Separate files for small functions

  pattern_overuse:
    - Strategy pattern for 2 strategies
    - Observer for single subscriber
    - Abstract factory for concrete needs
```

### Context Health Thresholds

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| Complexity Ratio | < 2.0 | 2.0-3.0 | > 3.0 |
| Turn Count | 1-2 | 3-4 | 5+ |
| Context Usage | < 60% | 60-75% | > 75% |

---

## Implementation Phases

| Phase | Content | Files |
|-------|---------|-------|
| 1 | /sc:context-check skill | sc-context-check.md |
| 2 | /sc:context-restart skill | sc-context-restart.md |
| 3 | /sc:context-status skill | sc-context-status.md |
| 4 | MODE_Context_Recovery.md | MODE_Context_Recovery.md |
| 5 | Integration + install script update | install.sh, Makefile |

---

## User Configuration

**~/.claude/settings.json additions**:
```json
{
  "context_recovery": {
    "enabled": true,
    "complexity_threshold": 2.0,
    "turn_warning": 3,
    "turn_critical": 5,
    "context_warning_percent": 75,
    "auto_suggest": true
  }
}
```

---

## Integration Points

1. **Serena MCP**: Persist context state via write_memory/read_memory
2. **TodoWrite**: Track recovery checkpoints
3. **Existing Skills**: /sc:implement, /sc:analyze can call context-check
4. **PM Agent**: Extend ConfidenceChecker with context health consideration

---

## Success Criteria

1. **Detection Rate**: Catch >80% of over-engineering before context exhaustion
2. **False Positive Rate**: <20% unnecessary restart suggestions
3. **Recovery Effectiveness**: CONCAT summaries enable successful restarts
4. **User Adoption**: Natural integration into workflow

---

## References

1. Laban, P., et al. "LLMs Get Lost In Multi-Turn Conversation." arXiv:2505.06120. May 2025.
2. /Users/chosh/Repos/ajitta/claude-wsl/docs/research/LOST_IN_CONVERSATION.md
3. Anthropic. "Effective Context Engineering for AI Agents." Sep 2025.

---

## Next Steps

1. [ ] Create sc-context-check.md skill
2. [ ] Create sc-context-restart.md skill
3. [ ] Create sc-context-status.md skill
4. [ ] Create MODE_Context_Recovery.md
5. [ ] Update superclaude install to include new skills
6. [ ] Test in real conversations
7. [ ] Iterate based on feedback
