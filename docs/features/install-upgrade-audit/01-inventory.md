---
feature: install-upgrade-audit
phase: inventory
status: complete
created: 2026-10-19
revised: 2026-10-19
---

# 01. Inventory — what every era wrote, and what the current code does with it

P1 of [05-plan.md](./05-plan.md). Base `master` @ 1dd9622c (v4.29.6). Sources are `<sha>:<path>:<line>`, `<sha> <date> <subject>`, or a current `file:line`; counts are not copied (`stale-number-copies`): re-derive them from the source cited. Hook history, runtime state and the shipped-names history are in [01a-inventory-history.md](./01a-inventory-history.md).

Scopes: **U** user `~/.claude`, **P** project `./.claude` (committed), **L** local `./.claude` personal + `./CLAUDE.local.md`. `<base>` is the scope's `.claude`.

## 1. Era map

| Era | Commits | pyproject | Installer code | Scopes |
|---|---|---|---|---|
| E0 upstream `setup/` | v4.0.3 `8605ef06` … v4.1.6 `7c14a31b` | 4.0.3–4.1.6 | `v4.0.9:setup/components/*.py`, `setup/services/{claude_md,settings}.py` | U |
| E1 upstream pip CLI | v4.1.7 `16caa494` … v4.1.9 `43ca81d1` (fork root) | 4.1.7–4.1.9 | `v4.1.9:src/superclaude/cli/{main,install_commands,install_skill,install_mcp}.py` | U |
| E2 fork "install all" | `981a49c9` 2025-12-25 … `7a20835d` 2025-12-26 | 4.1.9 | `src/superclaude/cli/install_commands.py` | U; P from `7a20835d` |
| E3 hooks into `<base>/hooks/`, wholesale settings write | `e18757c1` 2026-01-01 … `19091b37` 2026-01-02 | 4.1.9 | same, `install_hooks_and_scripts()` | U P |
| E4 hooks.json only | `c8e64bac` … `702dc25f` 2026-01-02 | 4.1.9 | same | U P |
| E5 templated paths, marker merge | `49286ed4` 2026-01-03 … `77b5821c` 2026-04-19 (split into `install_*.py` at `337e2c27`) | 4.1.9 … 4.4.x | `src/superclaude/cli/install_*.py` | U P |
| E6 `{{PYTHON_BIN}}`, local scope | `77b5821c` … `19575ac4` 2026-09-05 | 4.4.1 … 4.9.0 | + `install_gitignore.py` (`bd356afa`) → `install_git_exclude.py` (`b85651c0`) | U P L |
| E7 console entry | `19575ac4` … now (first fork tag v4.20.1 `97e6f724`) | 4.9.0 … 4.29.6 | + `cli/entry.py`, `cli/hook_dispatch.py` | U P L |

v4.2.0 (`1bd92c91`) and v4.3.0 (`af3a965d`) are upstream tags that are not ancestors of master (`git merge-base --is-ancestor`), so they are off the upgrade path (Q1). The fork has no version stamp on disk: no installer era writes one (`git log -G` over the install code), so an upgrade cannot know which era it is upgrading from; every handler below recognises its era by content.

## 2. What the current version writes (E7, `install_all`, install_components.py:477-635)

| Artifact | U | P | L | Ownership; what uninstall does | Source |
|---|---|---|---|---|---|
| `commands/sc/*.md` | ✓ | ✓ | ✓ | SC-only dir; `find_unshipped` prunes; uninstall rmtrees | install_paths.py:31, 238-267; install_inventory.py:320-347 |
| `superclaude/{CLAUDE_SC.md,core,core/rules,modes,mcp,templates}` | ✓ | ✓ | ✓ | SC-only; pruned; rmtree | install_paths.py:34-41; install_components.py:285-313; install_inventory.py:298-318 |
| `agents/*.md` (`memory:` rewritten to the scope) | ✓ | ✓ | ✓ | shared dir; shipped names + `RETIRED_AGENT_FILES` | install_components.py:45-55, 216-221; install_paths.py:233-235 |
| `output-styles/*.md`, `skills/<sc-*>/` | ✓ | ✓ | ✓ | shared dir; shipped names + `LEGACY_SKILL_NAMES` | install_paths.py:49, 224-230 |
| `hooks/hooks.json` (verbatim, every run) | ✓ | ✓ | ✓ | removed; `hooks/` rmdir'd only if empty | install_components.py:365-380; install_inventory.py:405-425 |
| hook merge | `settings.json` | `settings.json` | `settings.local.json` | per inner hook; user hooks kept in place | install_settings.py:350-453, 456-525; utils/__init__.py:461-476 |
| CLAUDE import | `~/.claude/CLAUDE.md`, created with `# Claude Code Configuration` if absent | `./.claude/CLAUDE.md` | `./CLAUDE.local.md` | `# superclaude` block stripped; file kept at U, removed at P/L only if nothing but the SC heading is left | install_settings.py:528-674 |
| agent memory store | `agent-memory/` | `agent-memory/` | `agent-memory-local/` | created by install (`b408eab0`); never removed | install_components.py:58-64, 135-158 |
| `.git/info/exclude` block | — | runtime state only | full list | marker-keyed; one block per clone (common dir) | install_git_exclude.py:91-134, 276-365 |
| hook state `<claude_base>/.superclaude_hooks/` | ✓ | ✓ | ✓ | rmtree on uninstall | utils/__init__.py:479-489; install_inventory.py:427-443 |
| `insights.pending.jsonl` | every project's `.claude/` (no exclude at U) | excluded | excluded | never removed (no `pending` in install_inventory.py) | scripts/insight_writer.py:64; install_git_exclude.py:93, 127 |
| `insights.jsonl` | project `.claude/` | ✓ | ✓ | durable user data, kept | scripts/insight_writer.py:59 |
| MCP (`superclaude mcp`) | `~/.claude.json` `mcpServers` | `./.mcp.json` | `~/.claude.json` `projects[root]` | `--remove-mcp` matches by name only | install_mcp.py:195-213, 583-656 |

`get_base_path("user")` is `Path.home()/".claude"` (install_paths.py:105-108) and ignores `CLAUDE_CONFIG_DIR`; Claude Code's settings page (fetched 2026-10-19) says that with it set "Claude Code then stores your settings, session history, and plugins there instead". X7 reproduces the gap ([02a](./02a-scenarios-edge.md)).

## 3. What older eras wrote, and the current handling

| Era artifact | Scope | Introduced → retired | Current handling | Matrix / status |
|---|---|---|---|---|
| E0 root `~/.claude/{FLAGS,PRINCIPLES,RULES,BUSINESS_*,RESEARCH_CONFIG}.md`, `MODE_*.md`, `MCP_*.md` | U | v4.0.3 → v4.1.6 (`v4.0.9:setup/components/core.py:18`, `modes.py:18`, `mcp_docs.py:25-32,63`) | nothing in `src/` names them | out of scope (Q1 a); backlog |
| E0 CLAUDE.md block `# SuperClaude Framework Components` with root `@FLAGS.md` imports; heading `# SuperClaude Entry Point` | U | `v4.0.9:setup/services/claude_md.py:81-117,245-251` | not recognised; uninstall's strip only matches `@superclaude/…` (install_settings.py:644-651), so both framework generations load after a fork install (inference, not run) | out of scope (Q1 a) |
| E0 `.superclaude-metadata.json`, `backups/`, `logs/`, `.update_check`, `.npm_update_check`, `superclaude_env_vars.json`; shell-rc API-key exports, `~/restore_superclaude_env.*` | U, $HOME | `v4.0.9:setup/services/settings.py:27`; `setup/utils/environment.py:17-22,86-185,340-364` | not recognised | out of scope (Q1 a) |
| E1 `commands/sc/*.md`, `skills/confidence-check/` (`install-skill`) | U | `v4.1.9:src/superclaude/cli/install_commands.py:92-110`, `install_skill.py:58-90` | pruned (`find_unshipped`; `LEGACY_SKILL_NAMES`) | U10 PASS (nothing foreign deleted) |
| E2 `<base>/superclaude/agents/`, `<base>/superclaude/skills/` | U | `981a49c9` → `7a20835d` (≈1 h) | not a component target, so not pruned; removed by uninstall's rmtree of `superclaude/` | note |
| E3 `<base>/hooks/*.py,*.sh` copies; settings `python .claude/hooks/<x>.py`, `.claude/hooks/<x>.sh`, inline jq prettier | U P | `e18757c1` → `c8e64bac` (`19091b37:src/superclaude/hooks/hooks.json`) | not SC by any current marker (`12cbcb4f` anchored them; utils/__init__.py:251-319); `update` appends console `session_init` beside it; uninstall leaves the commands and the copies (`hooks/` not empty) | U6-19091b37; **C-16** (Q14 b) |
| E4 `<base>/hooks/hooks.json` with no settings write (hooks never active: `49286ed4` body) | U P | `c8e64bac` → `49286ed4` | overwritten each install, removed by uninstall | no defect |
| `<base>/superclaude/scripts/*.py,*.sh` | U P L | `c8e64bac` → `19575ac4` | never deleted by install, ℹ️ notice keyed on still-referencing commands (install_components.py:402-406, 444-474); removed by uninstall's rmtree | U4, D1 |
| `{{SCRIPTS_PATH}}`, `python3 …`, `{{PYTHON_BIN}} $CLAUDE_PROJECT_DIR/.claude/superclaude/scripts/x.py` (uvx archive interpreter baked in) | U P L | `702dc25f` → `19575ac4` (`77b5821c:src/superclaude/cli/install_components.py:230-282`) | rewritten by `_migrate_legacy_commands` (install_settings.py:300-347) when a shipped replacement exists | U5, U6 PASS on the rewrite |
| Retired events `Setup` (last `19716a42`), `TeammateIdle`/`TaskCompleted` (last `b348e247`) | U P | `d174e600` → `66b37a7e` / `d7fd7850` | only `--force` strips SC hooks there (install_settings.py:404-417); uninstall strips marked ones | U11; **C-09** (Q13) |
| Unmarked `[experimental]` echo hooks on those events (`_comment` without `[superclaude]`) | U P | `d174e600` → `42218e97` | not SC (utils/__init__.py:304-319): survive `--force`, `update`, uninstall | U11-d174e600-user; **C-09** |
| Retired entry points `skill_activator` (last `66b37a7e`), `insight_writer pending-count` (last `79032ccc`) | U P L | → `bd683233`, `12cbcb4f` | no shipped replacement id, so never rewritten (install_settings.py:333-340); non-force keeps them | U11; **C-09** |
| Inline jq blocker `… 'BLOCKED: destructive …' && exit 2` | U P L | `66b37a7e` → `79032ccc` | identified (marker), kept by non-force beside `destructive_guard`, also in a committed project settings.json | U6, U8; **C-09** |
| `memory: user` in every shipped agent | U P | `d174e600` 2026-02-06 → `df5b8a35` 2026-02-24 | at P, `find_agent_memory_conflict` refuses and advises `--scope user` (install_components.py:103-132) | U11-d174e600-project; **C-06** |
| `memory: project` at U/L | U L | `df5b8a35` → `385baaf2` 2026-04-19 | accepted when untracked (install_components.py:84-88); non-force keeps the value | U9; **C-10** |
| Legacy skills (5) | U P L | `c733413d`… → `910eabdd` | `LEGACY_SKILL_NAMES` | tested |
| 11 process skills (`b933fd65^:src/superclaude/cli/install_paths.py:18`; on master for seconds: `b933fd65` and its parent share a timestamp) | U P | `1777f095`/`3e352fbd`/… → `b933fd65` | not listed; install and uninstall keep them | U8; **C-08** |
| `pm-agent.md`, `deep-research-agent.md` (also upstream v4.1.5/v4.1.6) | U P L | → `4c5f3d84`, `e4d86aa7` 2026-03-19 | not in `RETIRED_AGENT_FILES` (install_paths.py:235) | U8, U6-19091b37; **C-08** |
| `deep-research.md`; unshipped commands, modes, MCP docs, core | — | various (01a §4) | listed / `find_unshipped` (`67dba6e9` v4.27.1) | U10, T1 |
| L/P hook state in `~/.claude/.superclaude_hooks/` | U (from L/P) | `bd356afa` → `52b5517e` 2026-07-25 | unreachable by a L/P uninstall; nothing reports it | U4; **C-17** |
| `.gitignore` block, `(local scope)` markers | L | `bd356afa` → `b85651c0` / `59ff8803` | migrated to `info/exclude` (install_git_exclude.py:66-68, 250-274) | U7 PASS |
| Per-worktree `<gitdir>/worktrees/<n>/info/exclude` | L | `b85651c0` → `f61dd8f9` | not cleaned (dead file git never reads) | note |
| `# SuperClaude Framework` CLAUDE heading | U P L | `82f43f2e` → `15d86d54` (v4.27.2) | stripped on uninstall (install_settings.py:644-647) | T1 ✓ |
| Unparsable settings replaced by the hooks section alone | U P L | before `04327343` (v4.28.0) | now refused (install_settings.py:65-85) — past loss, nothing to clean | note |
| Old-registry MCP servers (`sequential-thinking`, `context7`, `magic`, `ast-grep`, `morphllm-fast-apply`, `serena`) | U P L | registry history in `install_mcp.py` at `0a37af8f`, `9c0412b5`, `e18212fc`, `d0d9dfa4`, `04c8dd88` | kept by design; `--remove-mcp` cannot reach them | note (Q3) |

## 4. Must survive (A2)

Non-`hooks` settings keys; user hooks (own entries, entries shared with an SC hook, order, matcher, timeout); formatting; user agents, styles, skills, commands; CLAUDE file text; non-SC exclude and `.gitignore` lines; agent memory; both insights files; user MCP servers (a user `playwright` too); pinned console commands. The matrix checks each (`c_intact` in the harness); the breaks are C-07, C-12, C-13, C-20, C-21 in [03-findings.md](./03-findings.md).
