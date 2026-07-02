---
description: Clean code systematic, kill dead code, optimize project structure. Use ONLY when user type `/sc:cleanup` explicit — do systematic delete + structural change, need explicit OK. NO auto-trigger on "clean up this function", "remove this import", or any single-file tidy — those direct edit.
---
<component name="cleanup" type="command">

  <role command="/sc:cleanup">
    <mission>Clean code systematic, kill dead code, optimize project structure</mission>
  </role>

  <syntax>/sc:cleanup [target] [--type code|imports|files|docs|all] [--safe|--aggressive] [--interactive] [--dry-run|--apply]</syntax>

  <flow>
  1. Analyze: cleanup chance + safety check
  2. Plan: pick approach + delegate agent
  3. Execute: systematic clean per --type. For --type docs, run validator checks sequentially per `<validator_checks>` below (R1 post-cutoff non-v2, R2 cross-feature `[[...]]` flag, R3 slug-overlap promotion-suggest, plus existing slug-duplicate lint + README index regen).
  4. Validate: no function loss (tests pass)
  5. Report: summary + maintain rec
  </flow>

  <outputs note="Per --type flag">
| Type | Actions | Report |
|---|---|---|
| code | Remove dead code | Console: removed items + line count |
| imports | Remove unused imports | Console: removed imports per file |
| files | Remove orphan files | Console: deleted file list |
| docs | R1-R3 validator (post-cutoff non-v2, cross-link form, slug-overlap) + transform naming + README index regen + slug-duplicate lint | Console: violations + promotion candidates + renamed/moved files |
| all | All above | Console: combined summary |
  </outputs>


  <tools>
  - Read/Grep/Glob: analyze + pattern detect
  - Edit: safe modify
  - TaskCreate/TaskUpdate: progress track
  - Task: big-scale delegate
  </tools>

  <patterns>
    - DeadCode: usage analyze → safe remove
    - Imports: dep analyze → optimize
    - Structure: arch analyze → modular gain
    - Docs: convention check → rename + move (--dry-run supported)
    - Safety: pre/during/post check
  </patterns>

  <validator_checks note="--type docs only — per doc-convention-v2 01b-discovery-open-decisions.md R1-R3">
    - R1-post-cutoff-non-v2: For each standalone doc in `docs/{specs,plans,research,analysis}/`, read frontmatter or filename date; if date > 2026-05-18 cutoff AND no companion `docs/features/<slug>/` folder, surface warning "v2 non-compliant — consider /sc:promote-feature <slug>". Pre-cutoff legacy explicitly skipped.
    - R2-cross-feature-link-form: Grep `\[\[[a-z0-9-]+\]\]` pattern across `docs/features/*/*.md` (skip fenced code blocks to avoid false positives on syntax examples). Each match = warning "use relative path per core/rules/RULES_DOCS.md cross-links rule (`../<other-slug>/NN-<phase>.md`); slug refs not supported". Standalone-doc matches not flagged (legacy tolerated).
    - R3-slug-overlap: Build slug set from (a) `docs/features/<slug>/` dir names + (b) standalone filename slugs (extract per `<slug>-<suffix?>-<username>-YYYY-MM-DD.md` pattern, strip suffix/username/date). Any slug appearing in ≥2 places = "consider promotion" suggestion per Q5 auto-detect mechanism — surface as "candidate: /sc:promote-feature <slug>". Suggestion-only per Q2 manual policy; never auto-migrate.
    - R-existing-slug-lint: Pre-existing per core/rules/RULES_DOCS.md `<doc_output_convention>` formatter mention. Detects same slug used by two standalone docs of same type.
    - R-existing-readme-regen: Auto-regenerate `docs/features/*/README.md` `## Documents` section from current file list when running with `--apply` flag. Read-only with `--dry-run`.
  </validator_checks>

  <examples>

| Input | Output |
|---|---|
| `src/ --type code --safe` | Conservative cleanup |
| `--type imports --safe` | Unused import analysis |
| `--type all --interactive` | Multi-domain with guidance |
| `components/ --aggressive` | Thorough cleanup |
| `--type docs --dry-run` | Preview doc naming fixes |
| `--type docs` | Auto-fix doc naming convention |

  <example name="aggressive-without-review" type="error-path">
    - Input: /sc:cleanup --type all --aggressive (on unfamiliar codebase)
    - Why wrong: aggressive clean w/o understand codebase risk kill code that look unused but dynamic referenced.
    - Correct: /sc:cleanup --type all --dry-run first, review result, then /sc:cleanup --type all --safe
  </example>

  </examples>


  <gotchas>
  - scope-check: only clean files in asked scope. No touch adjacent dirs
  - verify-unused: confirm files truly unused (grep for refs) before delete
  - date-parse-fallback: R1 date check pulls from frontmatter `created:`/`revised:` first, falls back to filename `-YYYY-MM-DD` suffix, then mtime. mtime can drift after git rename and produce false positives; prefer frontmatter when present.
  - code-block-false-positive: R2 `[[...]]` pattern matches markdown wiki-syntax but also literal `[[...]]` examples inside fenced code blocks; pre-filter ` ``` ` blocks before matching to avoid noise.
  - slug-overlap-noise: R3 may flag legitimately distinct features sharing kebab prefix (e.g., `auth-flow` vs `auth-v2`). Output is suggestion-only per Q2 policy; user judges per case. False positives are tolerable.
  - manual-gate: --type docs validator never auto-migrates per Q2 policy. `--apply` only runs low-risk transforms (frontmatter shape fix, README index regen). Bulk promotion is /sc:promote-feature scope.
  </gotchas>

  <bounds>
    <does>systematic clean, safety check, smart algo.</does>
    <never>remove w/o analyze, override exclusion, break function.</never>
    <fallback>Ask user guidance when unsure.</fallback>
  </bounds>

  <auto_fix_threshold>
    <safe>Unused imports, dead variables, empty files</safe>
    <approval_required>Exported functions, config files, shared modules</approval_required>
  </auto_fix_threshold>

  <handoff next="/sc:test /sc:build"/>
</component>