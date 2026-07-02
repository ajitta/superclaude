---
description: Promote standalone docs sharing a slug into a feature folder per doc-convention-v2. Use ONLY when user explicitly types `/sc:promote-feature <slug>` to consolidate scattered standalone docs (`docs/specs/`, `docs/plans/`, etc.) into `docs/features/<slug>/`. Manual gate per Q2 policy — never auto-migrates without user confirm. NOT auto-trigger when /sc:cleanup --type docs surfaces "consider promotion" suggestion — that's detection, this is action.
---
<component name="promote-feature" type="command">

  <role command="/sc:promote-feature">
    <mission>Promote standalone docs sharing slug into feature folder per doc-convention-v2 R4</mission>
  </role>

  <syntax>/sc:promote-feature &lt;slug&gt; [--dry-run|--apply] [--from docs/specs/...]</syntax>

  <flow>
  1. Scan: Glob `docs/{specs,plans,research,analysis}/*<slug>*.md` — collect candidate files; extract slug from each filename per core/rules/RULES_DOCS.md standalone pattern (`<slug>-<suffix?>-<username>-YYYY-MM-DD.md` → strip suffix/username/date)
  2. Match: filter candidates whose extracted slug equals `<slug>` (exact); show partial-match candidates separately (suffix or username differs)
  3. Confirm: present match set as table to user — `[file path] → [target phase-prefix path]`. Default `--dry-run` exits here with summary. `--apply` proceeds.
  4. Create: ensure `docs/features/<slug>/` does NOT exist (abort with error if it does — slug collision); `mkdir` it.
  5. Move: `git mv` each match to target phase-prefix name per core/rules/RULES_DOCS.md type→phase mapping (brainstorm/discovery→01-discovery.md, research→02-research.md, analyze→03-analysis.md, design→04-design.md, plan/workflow→05-plan.md or 05a-plan-workflow.md if both); preserve frontmatter; on multi-of-same-phase use NNa suffix per format spec
  6. Scaffold: write `docs/features/<slug>/README.md` with frontmatter (`feature: <slug>, phase: discovery, owner: <git user>, created: <today>, updated: <today>`) + Purpose stub + Documents index listing moved files
  7. Warn: grep repo for inbound paths matching old standalone names (`docs/specs/<slug>-*`, etc.); emit warning list of files holding stale links — user fixes manually (no auto-rewrite per R-3 mitigation, avoids silent breakage)
  8. Report: print summary — N files moved, N inbound warnings, feature folder path
  </flow>

  <outputs>
  | Artifact | Purpose |
  |---|---|
  | `docs/features/<slug>/` | New feature folder containing moved + renamed files |
  | `docs/features/<slug>/README.md` | Scaffolded index w/ frontmatter + Documents list |
  | Inbound link warning report | Console list of files holding stale paths to old standalone names |
  | Dry-run plan (default) | Console table of intended moves without filesystem change |
  </outputs>

  <tools>
  - Glob: Find candidate standalone files by slug pattern
  - Grep: Detect inbound stale references after move
  - Read: Inspect candidate frontmatter for type confirmation
  - Bash: `git mv` for tracked rename; `mkdir` for folder creation
  - Write: New README.md scaffold
  </tools>

  <patterns>
    - Manual gate: dry-run default, --apply explicit for any FS change
    - Type→phase mapping: filename suffix determines target phase prefix per core/rules/RULES_DOCS.md
    - Multi-of-same-phase: append letter suffix per `NNa-<phase>-<distinguisher>` when two files target same slot
    - No auto-rewrite: inbound link warnings list-only, user fixes manually
  </patterns>

  <examples>
  | Input | Output |
  |---|---|
  | `/sc:promote-feature auth-refactor` | Dry-run: list candidate files + intended target paths |
  | `/sc:promote-feature auth-refactor --apply` | Move files, scaffold README, emit inbound warnings |
  | `/sc:promote-feature payment-api --from docs/specs/payment-api-design-ajitta-2026-04-10.md` | Promote single explicit file as primary `04-design.md` |

  <example name="slug-collision" type="error-path">
    - Input: /sc:promote-feature auth-refactor --apply (when docs/features/auth-refactor/ already exists)
    - Why wrong: Promotion creates new feature folder; existing one would be silently overwritten or mis-merged.
    - Correct: Abort with error. User must either pick different slug, manually merge existing folder, or move existing folder to archive first.
  </example>

  <example name="partial-match-ambiguity" type="error-path">
    - Input: /sc:promote-feature auth (matches auth-refactor + auth-rework + authentication)
    - Why wrong: Promoting all 3 sets into single folder mixes unrelated work.
    - Correct: Surface partial-match list, prompt user to pick exact slug or run multiple invocations.
  </example>
  </examples>

  <gotchas>
  - slug-collision: Abort if `docs/features/<slug>/` exists. Never silently overwrite. User must resolve manually (different slug, merge, or archive existing).
  - partial-match: Glob `*<slug>*` catches over-broad matches (e.g., `auth` matches `auth-refactor` + `authentication`). Show partial-match group separately, require exact slug confirmation before move.
  - cross-link-blast: Inbound link rewrite NOT automatic. Grep + warn only. Auto-rewrite would risk silently breaking commit messages, PR descriptions, external chats. User decides per case.
  - multi-of-same-phase: When 2 candidates map to same phase (e.g., 2 design files), target NNa names per format spec — first→`04-design.md`, second→`04a-design-<distinguisher>.md` (distinguisher from filename suffix or date).
  - frontmatter-preserve: `git mv` preserves file content + git history. Do NOT rewrite frontmatter except to ADD `status:` + `revised:` if absent (per core/rules/RULES_DOCS.md phase-doc frontmatter rule).
  </gotchas>

  <bounds>
    <does>scan standalone candidates, confirm move set, create feature folder + scaffold README, move files w/ git mv, emit inbound link warnings.</does>
    <never>auto-rewrite inbound links, overwrite existing feature folder, run without explicit --apply flag, move docs outside the named slug, modify frontmatter beyond status/revised add.</never>
    <fallback>Ask user when slug match is ambiguous, when feature folder exists, or when type→phase mapping unclear for non-standard filename pattern.</fallback>
  </bounds>

  <handoff next="/sc:cleanup /sc:design /sc:plan"/>
</component>
