# Session 2026-10-04/05 — plan: install without clone (uv tool CLI + sc plugin)

User request (exact): "superclaude를 설치하는 방법이 소스를 모두 받고 make deploy하는 방법이유일하다.이것을 plugin으로 설치가능하게 하는 방안". Deliverable ended up as a committed plan doc only (no implementation).

## Decided by the user (exact)
- Scope choice: "CLI 설치 + plugin 단계적" (over CLI-only Serena style and CLI-less standalone plugin).
- "ARCHIVE는 포크해왔던 superclaude framework이다. 그것과는다르다." → docs/archive/ (incl. the 2026-05-05 plugin discovery spec) is not evidence for the current code.
- "serena는 'uv tool install -p 3.13 serena-agent' 이 방법을 사용한다" → Serena install form used as the model for stage 1.
- After plan approval and a started stage-1 branch: "계획 문서만 작성하라" → implementation stopped; plan doc written instead.
- "계획에 빈틈 추가" → CI matrix lacks 3.13 while README would recommend `-p 3.13`; added as a plan step.
- "COMMIT AND PUSH" → done.

## Landed (verified)
- `docs/features/plugin-install/README.md` (phase: planning) + `05-plan.md` (status: draft). Commit 7f6ddc90, merge 9ce6c6df on master, pushed; CI Tests run 37214321459 success; suite 2861 passed, 1 skipped.
- Empty branch docs/uv-tool-install (created when implementation started) deleted; a stale 0-byte .git/index.lock (no git process running) removed to get back to master.

## Plan in one paragraph
Stage 1 = README only: `uv tool install -p 3.13 git+https://github.com/ajitta/superclaude.git` then `superclaude install`; verify first from git+file in scratch UV_TOOL_DIR/HOME; add "3.13" to .github/workflows/test.yml:17 matrix. Stage 2 = plugin root `src/superclaude` named `sc` (keeps `/sc:<cmd>`), entry added to existing marketplace `ajitta-socratic`; explicit commands/agents/outputStyles lists (exclude README.md); new `utils.plugin_root()` (CLAUDE_PLUGIN_ROOT + CLAUDE_SC.md check); new hook `core_inject` (forwarding, one hook per core file, `sys.stdout.buffer`, no-op without plugin root) on SessionStart `startup|clear|compact`; context_loader base path SUPERCLAUDE_PATH → plugin_root → claude_base; session_init plugin line + duplicate-install + version-skew warnings; release 4.21.0+ajitta.

## Facts established (sources)
- PyPI `superclaude` = upstream SuperClaude-Org, 4.3.0 uploaded 2026-03-22 (active). `superclaude-ajitta`, `ajitta-superclaude`, `superclaude-fork`, `sc-ajitta` were free (404) on 2026-10-05.
- CC plugins: root CLAUDE.md not loaded; SessionStart hook output capped 10,000 chars per string; core FLAGS+PRINCIPLES+RULES = 10,203 chars; plugin agents become `sc:<name>` and DO support `memory` (plugins/components doc line 739; a sub-agent claimed otherwise and was wrong); plugin and settings hooks are not deduplicated (hooks doc line 412); `once` honored only in skill frontmatter; `${CLAUDE_PLUGIN_ROOT}` substitutes inline in command/agent bodies; plugin settings.json honors only `agent`, `subagentStatusLine`.
- uv: lowercase `-p` = `--python`, uppercase `-P` = `--upgrade-package`. Dev .venv and installed superclaude tool both CPython 3.13.7; CI matrix 3.10/3.11/3.12 only.
- uv `--index` + default first-index strategy would let `uv tool install superclaude --index <url>` install the fork without upstream mixing (uv docs concepts/indexes.md:116-121); tool upgrade retains install settings (concepts/tools.md:144), index retention unverified.
- doctor finds the pytest plugin by entry point value, not dist name (cli/doctor.py:88) → renaming the distribution would not break code.

## Discussed, not added to the plan
- Name-only install like Serena requires PyPI under a new name (recommended A: `superclaude-ajitta`, version without `+ajitta`, restore publish workflow cut in over-engineering-audit D08) or a self-hosted PEP 503 index (B: keeps `superclaude` + `+ajitta`, needs `--index` forever). Recommendation given: A, as a later phase after stage 1. User has not decided.

## Open
- Plan not started. Next: user picks when to implement stage 1 (docs/uv-tool-install) and whether to add a PyPI phase.
- Concurrent work on master: db9218be (socratic Pages guide 14-pages-guide.md) references this draft plan because `sc` joins the same marketplace.
