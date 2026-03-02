<component name="morphllm" type="mcp">
  <role>
    <mission>Pattern-based code editing engine with token optimization for bulk transformations</mission>
  </role>

  <choose>
Use:
- Pattern-based edits: For bulk ops, not symbol ops (use Serena)
- Bulk operations: Style enforcement, framework updates, text replacements
- Token efficiency: Fast Apply with compression (30-50% gains)
- Moderate complexity: <10 files, straightforward transformations

Avoid:
- Semantic operations: Symbol renames, dependency tracking, LSP
  </choose>

  <examples>
| Input | Output | Reason |
|-------|--------|--------|
| update React class to hooks | Morphllm | pattern transformation |
| enforce ESLint rules | Morphllm | style guide application |
| replace console.log with logger | Morphllm | bulk text replacement |
| rename getUserData everywhere | Serena | symbol operation |
| analyze code architecture | Sequential | complex analysis |
  </examples>

  <workflows>
    <bulk_rename_pattern>
1. Identify text pattern to replace (regex or literal)
2. Scope target files: glob pattern or directory boundary
3. Apply with Morphllm Fast Apply → review diff for unintended matches
4. Validate: run tests or linter to confirm no breakage
Note: for symbol-aware renames (respecting scope), use Serena instead
    </bulk_rename_pattern>
    <api_migration>
1. Map old API signatures to new signatures
2. Define transformation pattern: old call shape → new call shape
3. Apply across target files (<10 per batch for reliability)
4. Handle edge cases: optional params, overloaded signatures
5. Run type checker or tests to verify completeness
    </api_migration>
  </workflows>

  <scenarios>
    <cross_file_refactoring>
Scenario: migrate from axios to fetch across service layer
1. axios.get(url, config) → fetch(url, { method: 'GET', ...config })
2. axios.post(url, data) → fetch(url, { method: 'POST', body: JSON.stringify(data) })
3. response.data → response.json() with await
4. Scope: src/services/**/*.ts (keep test mocks unchanged)
5. Apply each pattern as separate pass; run integration tests
    </cross_file_refactoring>
  </scenarios>

  <tool_guide>
- Best for: text-level patterns where semantic context is unnecessary
- Batch size: under 10 files per operation for reliable output
- Token efficiency: Fast Apply compresses diffs for 30-50% savings
- Boundary: Serena for symbol renames, Morphllm for text patterns
- Combine with --seq for planning multi-step migrations before execution
  </tool_guide>
</component>
