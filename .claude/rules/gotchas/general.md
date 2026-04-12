# Project Gotchas — General
# Last reviewed: 2026-04-12
# Claude가 실수할 때마다 여기에 한 줄씩 추가됩니다.
# 기존에 알려진 프로젝트 트랩이 있으면 직접 추가 가능 (R19 자동 캡처와 병행).

- context-leak: Do not Read sub-agent output files (*.output) — wait for returned summary. Reading transcripts pollutes main context with tool noise
- compaction-drift: Rules from session start may degrade after ~50 turns of auto-compaction. For long sessions, re-read critical rules if behavior drifts
- rule-tag-vs-concept: When counting rule occurrences, grep for exact tag (e.g., \bR18\b), not concept name. "Verification" appears broadly but R15 appears once
- hypothesis-before-fix: Before proposing a bug fix, state the top hypothesis AND the specific evidence (file:line, command output, reproduction) that confirms it. No guessing from symptom shape. Past misses: Service Worker blamed for URL issue (real: CloudFront stale bundle), Go scientific notation blamed (real: normalizeString asymmetry)
- find-all-copies-first: Before editing a file that may have duplicates (minified bundles, generated artifacts, vendored libs), grep the full basename across the repo and confirm copy count. Past miss: only updated 1 of 3 oasisw-stable.min.js files
