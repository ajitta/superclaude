---
status: draft
revised: 2026-10-05
---

# 14 — Plugin install guide on the GitHub Pages site

Proposal to add a section to https://ajitta.github.io/superclaude/ that explains these three commands:

```
/plugin marketplace add ajitta/superclaude
/plugin install socratic-brainstorm@ajitta-socratic
/plugin install socratic-elenchus@ajitta-socratic
```

Not applied yet. §5 is the drop-in HTML.

## 1. What was checked (2026-10-05)

- **Site source:** GitHub Pages serves `docs/index.html` from `master` (`gh api repos/ajitta/superclaude/pages` → `"branch":"master","path":"/docs"`). One file, no build step. No test reads it.
- **Marketplace:** `.claude-plugin/marketplace.json` is named `ajitta-socratic`, and its two entries point at `./portable-skills/plugins/<skill>`. `claude plugin validate .` → "✔ Validation passed".
- **Manifests:** `portable-skills/plugins/*/.claude-plugin/plugin.json` equal `portable-skills/plugin-manifests/*.json` (brainstorm 3.2.0, elenchus 1.2.0).
- **Remote:** `git diff origin/master -- .claude-plugin portable-skills/plugins` is empty, so the marketplace users add today is the checked one.
- **End-to-end install:** verified on 2026-10-03 ([13](./13-review.md) §7). Not repeated here: this machine has both skills from claude.ai sync (`claude plugin list` → `socratic-brainstorm@synced`, `socratic-elenchus@synced`).

## 2. What the guide must say

Each point answers a likely misreading.

1. **Separate from the framework.** No clone, no `make deploy`, no `superclaude` CLI. The Install section right above starts with `git clone`, so this needs saying first.
2. **The marketplace name differs from the repository name.** You add `ajitta/superclaude` and install from `@ajitta-socratic`. The first command only registers the marketplace and installs nothing.
3. **Which one to pick.** brainstorm to leave with options and a plan; elenchus to test what a key word means. Both is fine; elenchus first, then brainstorm.
4. **Invocation name.** Installed as a plugin, the slash command repeats the name (`/socratic-brainstorm:socratic-brainstorm`). Asking in words also works.
5. **Not `/sc:brainstorm`.** The "Try a command" section above lists `/sc:brainstorm`, which writes requirement docs; these skills only ask questions and never implement.
6. **Cloud sessions.** Plugins installed from user settings do not load there. claude.ai and Codex routes are in `portable-skills/README.md`; link to it instead of repeating them.

## 3. Naming

Plugin and skill names are the same string on every layer:

| Layer | brainstorm | elenchus |
|---|---|---|
| Source folder, zip folder | `socratic-brainstorm` | `socratic-elenchus` |
| SKILL.md `name` | `socratic-brainstorm` | `socratic-elenchus` |
| plugin.json `name` | `socratic-brainstorm` | `socratic-elenchus` |
| Codex | `$socratic-brainstorm` | `$socratic-elenchus` |
| Display name (plugin.json, openai.yaml, SKILL.md H1) | Socratic Brainstorm | Socratic Elenchus |

Three things look inconsistent from outside that table:

| Looks inconsistent | Cause | Decision |
|---|---|---|
| `@ajitta-socratic` in the install command | marketplace.json `name` differs from the repository name `superclaude` | Keep; explain in the guide |
| `/socratic-brainstorm:socratic-brainstorm` | Claude Code names a plugin's skill `plugin:skill`; one plugin holds one skill of the same name, so the name repeats (same as `ponytail:ponytail`) | Keep; explain in the guide |
| "skill" and "plugin" used for the same thing | The first draft of §5 said "Install one skill or both" under `/plugin install`, with a "Skills" nav link | Fixed in §5 |

### Why keep the marketplace name

`ajitta-socratic` says the marketplace does not install the framework; its description states "The SuperClaude framework itself is installed with the superclaude CLI, not from this marketplace". Renamed to `superclaude`, `@superclaude` would read as the framework. Anyone who added the marketplace since 2026-10-03 has plugin IDs ending in `@ajitta-socratic` and might have to reinstall after a rename. How Claude Code matches a renamed marketplace to existing installs was not checked.

**Open dependency:** the draft plan `docs/features/plugin-install/05-plan.md` (2026-10-05, uncommitted when this was written) adds an `sc` plugin to this same marketplace and rewrites its description. If it ships, the first reason above no longer holds and `sc@ajitta-socratic` widens the mismatch. That plan also keeps the name, for the same reinstall reason. Settle the name there before either change ships.

### Why keep the repeated name

Removing it means one `socratic` plugin with two skills, `brainstorm` and `elenchus`. The Agent Skills spec requires a skill's name to match its folder, so the skill names themselves become `brainstorm` and `elenchus`:

- Codex becomes `$brainstorm`, and on claude.ai the name collides with other brainstorm skills (this machine already has `sc:brainstorm` and `unknowns:brainstorm`).
- The one-zip-per-skill claude.ai upload route would need rebuilding.

That cost is too high for one repeated word.

### Terminology rule for the guide

Install steps say **plugin**; what runs says **skill**. State once that each plugin holds one skill with the same name, which also explains the two kept names above.

## 4. Placement

- New section `id="skills"` between `#commands` and the `origin` section.
- Classes `content install` reuse the Install section's blue two-column layout, so it alternates with the white sections around it. No CSS changes.
- One nav link between Commands and GitHub.

## 5. Proposed HTML

The site is in English, so the copy is too.

Nav:

```html
        <a href="#skills">Plugins</a>
```

Section:

```html
    <section id="skills" class="content install">
      <div class="wrap">
        <div>
          <h2>Socratic plugins for Claude Code</h2>
          <p>Two plugins from this repository's marketplace. Each holds one skill with the same name. They are separate from the framework: no clone, no <code>make deploy</code>, no <code>superclaude</code> CLI.</p>
          <p>Not the same as <code>/sc:brainstorm</code>, which turns a feature request into requirements and writes docs. These skills only ask questions and never implement anything.</p>
          <a href="https://github.com/ajitta/superclaude/tree/master/portable-skills">Install on claude.ai or Codex ↗</a>
        </div>
        <div>
          <pre><code>/plugin marketplace add ajitta/superclaude
/plugin install socratic-brainstorm@ajitta-socratic
/plugin install socratic-elenchus@ajitta-socratic</code></pre>
          <p class="scope-strip">The first line registers the marketplace, named <code>ajitta-socratic</code>; it installs nothing by itself. Install one plugin or both.</p>
          <div class="example"><code>socratic-brainstorm</code><p>Tests your idea with one question at a time, draws out your options, adds up to three of its own, and ends with a verdict (sharpened, open, or refuted) and a short brief. Pick it when you want to leave with a plan.</p></div>
          <div class="example"><code>socratic-elenchus</code><p>The method of Plato's dialogues: "what is X?", premises you agree to, a contradiction built from them, and a definition you revise. No advice. Pick it to find out whether you know what you mean.</p></div>
          <p class="scope-strip">Claude Code names a plugin's skill <code>plugin:skill</code>, so the slash command repeats the name: <code>/socratic-brainstorm:socratic-brainstorm &lt;idea&gt;</code> or <code>/socratic-elenchus:socratic-elenchus &lt;idea&gt;</code>. Asking in words works too ("poke holes in this plan"). To use both, settle the key word with elenchus first, then brainstorm. Plugins installed from user settings do not load in cloud sessions.</p>
        </div>
      </div>
    </section>
```

The two `.example` labels stay as bare names: plugin and skill share them, so either reading is correct.

## 6. Left out

- **Hero copy and `<meta name="description">`:** unchanged. Add a phrase to the description if search results should mention the plugins.
- **Update instructions (`/plugin marketplace update`):** omitted; the default auto-update behavior for third-party marketplaces was not checked.
- **`portable-skills/README.md` line 51:** `/plugin install <skill>@ajitta-socratic` puts `<skill>` where the plugin name goes. The command works because the names are equal, so it is out of scope here.

## 7. Done when

- `uv run pytest` exits 0 (no test reads `docs/index.html`, but the project runs the suite for docs changes too).
- The section renders at phone width without horizontal scroll (the `@media (max-width: 760px)` rule already collapses `.install .wrap` to one column).
- After the push, https://ajitta.github.io/superclaude/#skills shows the section.
