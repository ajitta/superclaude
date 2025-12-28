---
description: Execute tests with coverage analysis and automated quality reporting
---
<component name="test" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="medium"/>

  <role>
    /sc:test
    <mission>Execute tests with coverage analysis and automated quality reporting</mission>
  </role>

  <syntax>/sc:test [target] [--type unit|integration|e2e|all] [--coverage] [--watch] [--fix]</syntax>

  <triggers>
    - Test execution requests
    - Coverage analysis needs
    - Continuous testing + watch mode
    - Test failure analysis
  </triggers>

  <flow>
    1. **Discover**: Categorize tests via runner patterns
    2. **Configure**: Environment + execution params
    3. **Execute**: Run + real-time progress
    4. **Analyze**: Coverage reports + failure diagnostics
    5. **Report**: Actionable recs + quality metrics
  </flow>

  <mcp servers="play:e2e"/>
  <personas p="qa-specialist"/>

  <tools>
    - **Bash**: Test runner execution
    - **Glob**: Test discovery + patterns
    - **Grep**: Result parsing + failure analysis
    - **Write**: Coverage reports + summaries
  </tools>

  <patterns>
    - **Discovery**: Pattern categorization → runner selection
    - **Coverage**: Metrics → comprehensive reporting
    - **E2E**: Browser automation → cross-platform validation
    - **Watch**: File monitoring → continuous execution
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `/sc:test` | All tests + basic coverage |
| `src/components --type unit --coverage` | Targeted coverage |
| `--type e2e` | Playwright browser testing |
| `--watch --fix` | Continuous + auto-fix |

  </examples>

  <bounds will="execute existing tests|coverage reports|failure analysis" wont="generate test cases|modify framework config|destructive changes"/>
</component>
