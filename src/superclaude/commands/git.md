---
description: Git operations with intelligent commit messages and workflow optimization
---
<component name="git" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="low"/>

  <role>
    /sc:git
    <mission>Git operations with intelligent commit messages and workflow optimization</mission>
  </role>

  <syntax>/sc:git [operation] [args] [--smart-commit] [--interactive]</syntax>

  <triggers>
    <t>Git ops: status, add, commit, push, pull, branch</t>
    <t>Intelligent commit message generation</t>
    <t>Repository workflow optimization</t>
    <t>Branch management + merges</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Repo state + changes</s>
    <s n="2">Validate: Operation appropriateness</s>
    <s n="3">Execute: Git command + automation</s>
    <s n="4">Optimize: Smart commits + patterns</s>
    <s n="5">Report: Status + next steps</s>
  </flow>

  <tools>
    <t n="Bash">Git command execution</t>
    <t n="Read">Repo state analysis</t>
    <t n="Grep">Log parsing + status</t>
    <t n="Write">Commit message generation</t>
  </tools>

  <patterns>
    <p n="SmartCommit">Analyze changes → conventional message</p>
    <p n="Status">Repo state → actionable recs</p>
    <p n="Branch">Consistent naming + workflow</p>
    <p n="Recovery">Conflict resolution + restoration</p>
  </patterns>

  <examples>
    <ex i="status" o="State analysis + recommendations"/>
    <ex i="commit --smart-commit" o="Conventional commit"/>
    <ex i="merge feature-branch --interactive" o="Guided merge"/>
  </examples>

  <bounds will="intelligent git ops|conventional commits|workflow guidance" wont="modify config without auth|destructive without confirm|complex merges requiring manual"/>
</component>
