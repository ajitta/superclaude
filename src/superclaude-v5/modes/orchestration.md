---
name: orchestration
type: mode
priority: high
triggers: [multi-tool, parallel, optimize, performance, batch]
---

<document type="mode" name="orchestration">

# Orchestration Mode

## Activation Conditions
| Condition | Example |
|---|---|
| 3+ files simultaneously | Multi-file refactor |
| Multi-tool combination | MCP + native mix |
| Performance constraints | Token/time limits |
| Batch processing | Bulk edits |

## Tool Selection Matrix

| Task | Best Choice | Alternative | Avoid |
|---|---|---|---|
| UI components | Magic MCP | Manual coding | - |
| Deep analysis | Sequential MCP | Extended thinking | Shallow reasoning |
| Pattern edits | Morphllm MCP | Regex + sed | Manual repetition |
| Documentation | Context7 MCP | Web search | Guessing |
| Browser test | Playwright MCP | Unit tests | Screenshots |
| Symbol navigation | Serena MCP | grep + find | Full file reads |

## Tool Search (PRD §4.3)

| Step | Action | Effect |
|---|---|---|
| 1 | Demand-based tool discovery | Avoid unnecessary loads |
| 2 | Cache tool summaries | Reduce token cost |
| 3 | Prefer MCP when fit | Align MCP-first policy |

## Resource Management

| Zone | Threshold | Action |
|---|---|---|
| Green | 0-75% | Full capabilities |
| Yellow | 75-85% | Concise output, defer extras |
| Red | 85%+ | Essential ops only |

## Chain of Draft Integration

```xml
<draft>
step1: identify files -> 5 targets
step2: select tool -> Morphllm MCP
step3: pattern -> rename func
result: batch execute
</draft>
<action>[Morphllm MCP call]</action>
```

## Parallel Execution Rules

| Condition | Action |
|---|---|
| 3+ independent files | Suggest parallel reads |
| Multiple directories | Delegation mode |
| Sequential dependency | Chain execution |
| MCP + native mix | MCP first |

## Example

<example>
  <input>Rename a function across 5 files</input>
  <output>
    <draft>
    step1: scope -> 5 files
    step2: tool -> Morphllm MCP
    step3: pattern -> funcA->funcB
    result: parallel batch
    </draft>
    <action>
    1. Morphllm MCP pattern edit
    2. Run related tests in parallel
    3. Verify results
    </action>
  </output>
</example>

</document>
