# Project Gotchas — General
# Last reviewed: 2026-05-14
# Claude가 실수할 때마다 여기에 한 줄씩 추가됩니다.
# 기존에 알려진 프로젝트 트랩이 있으면 직접 추가 가능 (R19 자동 캡처와 병행).

- context-leak: No Read sub-agent output files (*.output) — pollute main context with tool noise. Treat returned summary as advisory, not authoritative: require cite {files inspected, commands run, exact evidence, assumptions, residual risks}, revalidate cited file:line (re-grep, re-read specific lines) before edit or report based on it. Token-save by trust summary blindly = failure mode
- compaction-drift: Rules from session start degrade after ~50 turns auto-compaction. Long session, re-read critical rules if behavior drift
- rule-tag-vs-concept: When count rule occurrences, grep exact tag (e.g., \bR18\b), not concept name. "Verification" appear broadly but R15 appear once
- hypothesis-before-fix: Before propose bug fix, state top hypothesis AND specific evidence (file:line, command output, reproduction) that confirm it. No guess from symptom shape. Past miss: Service Worker blamed for URL issue (real: CloudFront stale bundle), Go scientific notation blamed (real: normalizeString asymmetry)
- find-all-copies-first: Before edit file that may have duplicates (minified bundles, generated artifacts, vendored libs), grep full basename across repo and confirm copy count. Past miss: only updated 1 of 3 oasisw-stable.min.js files
- scripts-path-template: `{{SCRIPTS_PATH}}` = SC install-time template (NOT CC-native). Resolve to `~/.claude/superclaude/scripts/`, never `~/.claude/scripts/`. Source tree show template; installed tree show absolute path. When invoke direct, use resolved path or `ls ~/.claude/superclaude/scripts/` to confirm
- askuserquestion-rejection-fallback: When user reject AskUserQuestion tool call, no re-ask + no stall. State top assumption explicit ("Assuming X because Y → proceeding with bounded change") + execute minimal reversible action + surface diff so user redirect if wrong. Past miss: /sc:brainstorm AskUserQuestion 거부 → session stall, 0 requirements elicit. Trigger: any AskUserQuestion denial w/o explicit redirect msg