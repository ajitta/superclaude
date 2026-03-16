<component name="morphllm" type="mcp">
  <role>
    <mission>Pattern-based code editing engine with token optimization for bulk transformations</mission>
  </role>

  ## Activation
  Not always active. When bulk code transformations are needed:
  1. `mcp-find("morphllm")` — locate in MCP Docker catalog
  2. `mcp-add("morphllm")` — activate for current session
  3. Provides Fast Apply with token compression (30-50% savings)

  <choose>
  Use:
  - Bulk text replacement: console.log → logger, require → import across files
  - Style enforcement: formatting rules, naming conventions across codebase
  - Framework migration: class components → hooks, Options API → Composition API
  - Pattern application: add error handling, add TypeScript types to JS files
  - Moderate scope: <10 files, straightforward text-level transformations

  Avoid:
  - Symbol-level operations: rename with reference tracking → Serena (--serena)
  - Single file edits: one change in one file → Edit tool
  - Semantic refactoring: extract method, move class → Serena (--serena)
  - Large-scale (>20 files): risk of unintended matches → manual review first
  </choose>

  ## Decision Rule: Morphllm vs Serena vs Edit
  | Scenario | Tool | Why |
  |----------|------|-----|
  | Replace `console.log` with `logger.info` in 8 files | Morphllm | Text pattern, bulk |
  | Rename `getUserData` and update all callers | Serena | Symbol-aware, reference tracking |
  | Fix one typo in a config file | Edit | Single change, single file |
  | Convert all `var` to `const`/`let` | Morphllm | Text pattern, bulk |
  | Extract shared logic into a utility | Serena | Semantic restructuring |
  | Add `"use strict"` to all JS files | Morphllm | Insertion pattern, bulk |

  ## Transformation Strategy
  - **Preview first**: check pattern matches before applying across files
  - **Scope control**: limit to specific directories or file patterns
  - **Incremental**: apply to 2-3 files first, verify, then expand
  - **Reversibility**: ensure changes are git-tracked before bulk transforms

  ## Token Efficiency
  Morphllm's Fast Apply compresses edit instructions, reducing token usage by 30-50% compared to
  sending full file contents through the Edit tool. Most effective when:
  - Same transformation applied to many files
  - Changes are pattern-based (regex-expressible)
  - File contents don't need full reading

  ## Integration Patterns
  - **Codebase cleanup**: Morphllm:bulk-fix → /sc:test → /sc:review
  - **Migration**: Context7:new-api → Morphllm:transform-patterns → /sc:test
  - **Style enforcement**: /sc:analyze --focus quality → Morphllm:apply-fixes → /sc:test
  - **Modernization**: Sequential:plan-transforms → Morphllm:execute → /sc:review

  <examples>
| Input | Action | Reason |
|-------|--------|--------|
| replace all console.log with logger | Morphllm: pattern replacement across files | Bulk text operation |
| convert React class to hooks | Morphllm: pattern transformation per component | Framework migration |
| enforce ESLint auto-fixable rules | Morphllm: style application | Bulk style enforcement |
| rename getUserData everywhere | Serena: rename_symbol (not Morphllm) | Needs symbol tracking |
| fix one import path | Edit tool (not Morphllm) | Single file, single change |
  </examples>

  <bounds will="pattern-based bulk edits|style enforcement|token-efficient transformations|framework migration patterns" wont="semantic symbol operations|single-file edits|dependency tracking|LSP-powered refactoring" fallback="Use Serena for symbol-level operations, Edit for single-file changes"/>

  <handoff next="/sc:improve /sc:cleanup /sc:implement"/>
</component>
