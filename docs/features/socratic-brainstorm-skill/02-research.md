---
status: complete
revised: 2026-10-02
---

# 02 — Research: Socratic brainstorming, in this repo and as published skills

> **Historical (one-skill era).** Written when the plan was a single `socratic-brainstorm` skill. §1-2 (repo inventory, published skills) still hold. In §3 the claude.ai install path is outdated: uploads go through Customize › Plugins and need `.claude-plugin/plugin.json` (see [11](./11-plugin-upload.md)). The current state is in [README](./README.md).

Goal of the feature: one portable skill that runs Socratic brainstorming in Claude (chat, Claude Code, cloud sessions) and Codex, including from the phone.

Method: grep of `src/superclaude` at `16b8fbd` (4.18.1+ajitta); external skills downloaded raw from GitHub and read in full; platform facts from official docs fetched as Markdown on 2026-10-02. Tags: **OFFICIAL** = vendor docs, **REPO** = this repo, **COMMUNITY** = third-party repos/forums, **INFERRED** = this document's reasoning.

## 1. What this repo already has (REPO)

Socratic questioning appears in 14 files under `src/superclaude`. Five carry real behavior:

| Surface | File | What it contributes | Portable today? |
|---|---|---|---|
| `/sc:brainstorm` command | `commands/brainstorm.md` (82 lines) | 8-step flow: explore → analyze → validate → specify → approve → self-review gate → decision-mode tags → handoff. `confirmed` vs `delegated` decision tagging (L33-38). Gotchas: evidence-fabrication, analysis-loop, skip-review (L64-68). `--vs` perspectives. | No. Needs `/sc:review`, `/sc:plan`, `RULES_DOCS.md` doc convention, TaskCreate, Serena; installed as a Claude Code command only. |
| Brainstorming mode | `modes/MODE_Brainstorming.md` (38 lines) | Mindset: diverge→converge, quantity→quality, build→judge, edges→center (L7-11). Communication: ask > tell, "what if" / "how might we" (L13). Never prescribe solutions (L33). | Partly. Loaded by `context_loader.py:148` on `--brainstorm`; meaningless without the hook. |
| `socratic-mentor` agent | `agents/socratic-mentor.md` (78 lines) | Leveled questions observation → pattern → principle → application; name the concept only after the learner states it (L14-28); "if you catch yourself explaining, convert it into a question" (L68). | No. Subagent: a subagent cannot hold a multi-turn dialogue with the user, so the Socratic loop must run in the main conversation. |
| `requirements-analyst` agent | `agents/requirements-analyst.md` (81 lines) | "Ask why before how" (L12); necessity gate R18 "is the system broken without this?" (L68); measurability-first acceptance criteria (L70); scope anchoring (L69). | Same subagent limit. |
| Panel `socratic` modes | `commands/spec-panel.md` L33, `commands/business-panel.md` L24, `agents/business-panel-experts.md` L28 | Questions asked *through expert lenses* (Nygard "what happens at 3AM?", Drucker "which assumptions are fragile?", Taleb "what breaks first?"). | No. Bound to the panel commands. |

Supporting pieces: `core/FLAGS.md:7` (`--brainstorm` flag), `modes/MODE_Verbalized_Sampling.md` (k perspectives with probabilities, used by `/sc:brainstorm --vs`).

**The repo ships no skills.** Commit `910eabd` (2026-08-31) deleted the 5-skill layer because commands already carried the same frontmatter features; `cli/install_paths.py:183-209` prunes those legacy names on install. So a new skill must not be re-introduced into `src/superclaude/skills/` without reopening that decision (see 04-design D1).

**Upstream** (SuperClaude-Org/SuperClaude_Framework, ★23.9k) still ships `plugins/superclaude/skills/brainstorm/SKILL.md`: 44 lines, five generic questions, and an output template that ends in `## Recommendation`. That last part contradicts the Socratic stance (the model decides for the user).

### Gaps that block the stated goal

1. Everything is Claude Code-only. Nothing runs in claude.ai chat, the Claude mobile app, or Codex.
2. The Socratic method is spread across a command, a mode and three agents; no single file states the dialogue rules (one question per turn, steelman, contradiction surfacing, honest verdict).
3. The question discipline is thin: `MODE_Brainstorming.md` lists four example questions; there is no question taxonomy, no stop rule, and no verdict when the idea does not survive.
4. Output is a file under `docs/features/` — wrong for a phone chat with no repository.

## 2. Published skills that implement the technique (COMMUNITY)

Stars and push dates read from the GitHub API on 2026-10-02.

| Skill | Repo (★, last push) | Core mechanics worth taking | Weak points |
|---|---|---|---|
| `brainstorming` | obra/superpowers (★294k, 2026-09-27) | Classify request first (spike / bounded / architectural) and say it out loud; **one question per message, multiple choice preferred**; write back understanding, separating what the user said from assumptions; propose 2-3 approaches with a recommendation; `<HARD-GATE>` against implementation before approval; "a reply approves the stage actually presented". | Design-to-code pipeline; not a questioning method. Auto-fires on any creative work. |
| `socratic-method` | grammy-jiang/socratic-method (★0, 2026-09-07; most rigorous) | Six question types (clarification, assumptions, evidence, viewpoints, implications, questioning-the-question); **steelman the thesis and confirm it before probing**; tactics: counterexample, contradiction surfacing by verbatim quote, definition pressure, concreteness pull, falsification pull; modes `stress`/`develop`, depths `quick`/`standard`/`deep`; **verdicts sharpened / aporia / refuted / accepted-as-is**; refute only out of the user's own quoted words; instant stop on soft stop signals; quotes must be verbatim. Ships to Claude Code, Codex (`agents/openai.yaml`), Copilot. | 420-line SKILL.md; uses `disable-model-invocation`, which claude.ai upload rejects (§3). No idea generation at all — it is elenchus only. |
| `socrates` | MoYeRanqianzhi/Socrates.SKILL (★7) | Thesis → antithesis → synthesis rounds; **mutation guard**: if a round's synthesis only rephrases the thesis, switch question type; two dry rounds → "epistemic boundary reached", user decides. Red-flag table ("this is obvious" = unexamined). | Runs until interrupted; model-centric monologue rather than dialogue. |
| `brainstorm` | gupsammy/Claudest (★274) | Domain calibration (adversarial for strategy, gentle for personal); **saturation detection** (4 rounds without a new theme → propose closure); `--grill` mode: one question, each with a recommended answer, explore the codebase before asking. | Uses `AskUserQuestion` heavily (Claude Code only). |
| `brainstorm` | mhylle/claude-skills-collection (★19) | Idea-type classification → pick 1-2 frameworks (SCAMPER, Six Hats, premortem) instead of all; **parking lot** for tangents; continuation check after each round. | 2-4 questions per round (bundling). Spawns research subagents. |
| `socratic-ideation-tree` | majiayu000/claude-skill-registry (★660 registry) | Abstract → specific → tasks tree; intent questions (vision, values, context, motivation, scope). | Writes a directory tree of files; decomposition rather than dialogue. |
| `project-brainstorming` | athola/claude-night-market (★342) | Socratic → validated brief with a spec-review loop. | Many non-standard frontmatter keys (`model`, `dependencies`, …). |
| `brainstorming` | a-ariff/ariff-claude-plugins (★14) | Compact obra derivative: one question at a time, 2-3 approaches, "going backwards is fine". | Thin. |

### Convergent pattern across the good ones

- One question per turn, adaptive to the last answer (obra, socratic-method, gupsammy grill).
- Restate before probing (obra write-back, socratic-method steelman, Socrates proposition anchor).
- A named question taxonomy, rotated when answers stop moving (socratic-method six types, Socrates mutation guard, gupsammy rotation).
- Explicit end condition: user stop, budget, or saturation (all).
- A written artifact separating decisions, assumptions and open questions (all).
- The honest-failure outcome — **aporia** as a finding — exists only in socratic-method. Every other skill always ends in a recommendation.

### Gap none of them fills

None combines **elenchus** (testing the idea) with **generative brainstorming** (growing options) while keeping the user as the author of the ideas. socratic-method forbids any contribution before synthesis; obra/upstream jump to model-proposed approaches. The maieutic middle — ask the user to generate first, then add model options labeled as such — is the open slot. SuperClaude's own `MODE_Brainstorming` (diverge → converge, build → judge) plus `socratic-mentor` (name it only after the user states it) already describe that middle.

## 3. Platform facts that constrain a portable skill (OFFICIAL)

### Format

- Agent Skills spec (agentskills.io/specification): a folder with `SKILL.md`; `name` ≤64 chars, `[a-z0-9-]`, no leading/trailing/double hyphen, **must match the folder name**; `description` ≤1024 chars; optional `license`, `compatibility` (≤500), `metadata` (string map), `allowed-tools`.
- Claude Code docs `skills.md` "Using skill frontmatter outside Claude Code": **claude.ai upload, the Skills API and `package_skill.py` accept only** `name, description, license, compatibility, metadata, allowed-tools`. Any other key (`argument-hint`, `disable-model-invocation`, `when_to_use`) is a hard error: `Unexpected key(s) in SKILL.md frontmatter`. Claude Code-only body features (`!` commands, `$ARGUMENTS`, `${CLAUDE_*}`) don't work in claude.ai chat or the API.
- Claude Code truncates `description` + `when_to_use` at 1,536 chars in the listing.
- Codex docs `skills.md`: same SKILL.md; required `name`, `description`; optional `agents/openai.yaml` with `policy.allow_implicit_invocation: false` to stop implicit firing while `$skill` still works. Initial skill list capped at ~2% of context / 8,000 chars; descriptions get shortened first, so front-load the trigger words.

### Where each product loads skills

| Surface | Loads from | Explicit invoke |
|---|---|---|
| Claude Code (terminal, desktop) | `~/.claude/skills/`, project `.claude/skills/`, plugins, **plus skills enabled on the claude.ai account** (synced into `~/.claude/skills/synced/`, v2.1.273+) | `/name` |
| Claude Code cloud sessions (claude.ai/code, the **Code tab of the iOS/Android app**) | claude.ai-account skills + repo `.claude/skills/`; **not** `~/.claude/skills`, not plugins from user settings | `/name` (but see below) |
| claude.ai chat — web, desktop, **mobile app** | skills uploaded as ZIP at Customize › Skills (needs Code execution enabled) | by description match / by name in prose |
| Codex CLI, IDE, ChatGPT desktop app | `$CWD/.agents/skills` up to repo root, `~/.agents/skills`, admin, system | `$name`, `/skills` |
| Codex cloud tasks (web, **ChatGPT mobile**) | repo checkout — `.agents/skills` in the repo (INFERRED from "Codex scans `.agents/skills` … up to the repository root"; not stated for cloud explicitly) | `$name` in the task prompt |
| ChatGPT Chat/Work on **mobile** | only skills **bundled in plugins** from the plugin directory; standalone skills are desktop/CLI/IDE only | `@` |

Mobile notes:

- `code.claude.com/docs/en/mobile`: "The Claude app for iOS and Android is a client for Claude Code sessions rather than a place where code runs." Terminal-only commands (`/plugin`, `/resume`) don't work from the app.
- anthropics/claude-code#48696 (iOS, 2026-04; Android re-report later; closed *not planned*): in the mobile harness, repo `.claude/skills/*` are **not registered as slash commands** and `Skill("name")` returns "Unknown skill"; the model can still Read the SKILL.md when asked in prose. (COMMUNITY bug report, not an official statement.)
- Reddit r/ClaudeAI (2026): the Skills upload screen is not in the mobile app; upload once from a (mobile) browser, then the skill is on the account. (COMMUNITY)

### Consequences (INFERRED)

1. **Frontmatter must be spec-only** (`name`, `description`, `license`, `metadata`, optionally `compatibility`). No `disable-model-invocation`, no `argument-hint`. Manual-only behavior has to come from the description wording on Claude, and from `agents/openai.yaml` on Codex.
2. **The single highest-reach install is a claude.ai upload**: it reaches chat (all clients incl. mobile), Cowork, cloud Code sessions (phone Code tab) and the terminal via sync. Repo `.claude/skills/` + `.agents/skills/` copies cover cloud sessions/cloud tasks for that repo only.
3. **The body must work when invoked in plain words**, not only via `/name`: on mobile cloud sessions the slash path may be absent. Don't parse `$ARGUMENTS`; read options from prose.
4. **No hard tool dependencies.** `AskUserQuestion` exists only in Claude Code; chat has no repo. Questions must be answerable by typing a digit or a few words on a phone keyboard. File output is optional.
5. ChatGPT mobile *chat* (not Codex) needs a published plugin — out of scope for v1 (see 04-design deferred).
