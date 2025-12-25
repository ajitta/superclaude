---
description: Repository indexing with 94% token reduction (58K → 3K)
---
<component name="index-repo" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="low"/>

  <role>
    /sc:index-repo
    <mission>Repository indexing with 94% token reduction (58K → 3K)</mission>
  </role>

  <syntax>/sc:index-repo [mode=create|update|quick]</syntax>

  <triggers>
    <t>Repository indexing requests</t>
    <t>Token reduction needs</t>
    <t>Project structure documentation</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Repo structure (5 parallel Glob)</s>
    <s n="2">Extract: Entry points + modules + APIs + deps</s>
    <s n="3">Generate: PROJECT_INDEX.md + .json</s>
    <s n="4">Validate: Completeness + size &lt;5KB</s>
  </flow>

  <tools>
    <t n="Glob">Parallel structure scan (code|docs|config|tests|scripts)</t>
    <t n="Read">Metadata extraction</t>
    <t n="Write">Index generation</t>
  </tools>

  <patterns>
    <p n="Structure">src/**/*.{ts,py,js} | docs/**/*.md | *.toml | tests/**/*</p>
    <p n="Output">PROJECT_INDEX.md (3KB) + PROJECT_INDEX.json (10KB)</p>
  </patterns>

  <roi>
    <metric n="creation">2K tokens (one-time)</metric>
    <metric n="reading">3K tokens (per session)</metric>
    <metric n="full-read">58K tokens (per session)</metric>
    <metric n="breakeven">1 session</metric>
    <metric n="10-sessions">550K tokens saved</metric>
  </roi>

  <examples>
    <ex i="/index-repo" o="Create full index"/>
    <ex i="mode=update" o="Update existing"/>
    <ex i="mode=quick" o="Skip tests"/>
  </examples>

  <bounds will="94% token reduction|parallel analysis|human-readable output" wont="modify source|exceed 5KB"/>
</component>
