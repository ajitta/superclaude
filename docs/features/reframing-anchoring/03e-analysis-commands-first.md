# 03e — Phase 2 content value classification: commands (first half)

Branch `feature/reframing-anchoring`. Read-only audit of 19 command files under `src/superclaude/commands/`. Judged only from file text plus `ARCHITECTURE.md` (delivery: commands are CC-native `/sc:*` slash commands, body loaded on user invocation only).

## 1. Scope and files read

| File | Bytes |
|---|---|
| commands/agent.md | 3294 |
| commands/analyze.md | 5359 |
| commands/auto-improve.md | 5595 |
| commands/brainstorm.md | 6197 |
| commands/build.md | 2970 |
| commands/business-panel.md | 3333 |
| commands/cleanup.md | 6819 |
| commands/design.md | 4528 |
| commands/document.md | 3144 |
| commands/estimate.md | 2736 |
| commands/explain.md | 2617 |
| commands/git.md | 4115 |
| commands/help.md | 4223 |
| commands/implement.md | 4904 |
| commands/improve.md | 2313 |
| commands/index.md | 3246 |
| commands/index-repo.md | 2617 |
| commands/init.md | 6923 |
| commands/insight.md | 8202 |
| **Total** | **83135** |

Also read (allowed): `src/superclaude/ARCHITECTURE.md` (delivery mechanism only).

Method: every top-level XML element plus the frontmatter description was classified; `<flow>`, `<flags>`, `<gotchas>` and `<examples>` were split into sub-rows where classes differ. Bytes are measured per element (sub-row bytes are estimates). Class legend: A = model already does it, B = structural remedy, C = project fact, D = other (exhortation, duplicate, persona, leak).

## 2. Classification table

| File | Section | Class | ~Bytes | Reason | Failure (B) | Mechanism/exhortation (B) | Quote |
|---|---|---|---|---|---|---|---|
| agent | description | C | 329 | Routing: when to use vs Agent tool / /sc:pm / /sc:task |  |  | `Not for one sub-agent task — call the Agent tool directly` |
| agent | role/mission | D | 148 | Duplicates description |  |  | `Session controller that orchestrates investigation` |
| agent | syntax | C | 45 | Command syntax |  |  | `/sc:agent [task-description]` |
| agent | flow | A | 303 | Generic parse→delegate→monitor→deliver; model does this unprompted. Note: 'identify the task type' frames before purpose |  |  | `identify the task type, complexity and required expertise` |
| agent | startup | D | 300 | Ritual (git status emoji, /context reminder); only 'Core services: deep research, repo index' is a routing fact (C, ~60 B) |  |  | `Remind: 💡 Use /context to confirm token budget` |
| agent | task_protocol Phase 1+3 | B | 330 | Only I0-adjacent gate in scope: success criteria + acceptance checks must exist before implementation. Weak: criterion is CONFIRMED with the user, not inferred by the model; no 'state the purpose' step | I0 (partial) | mechanism — ordering gate; but criterion is user-supplied, not model-derived | `no implementation until Phase 1 scope, success criteria and acceptance checks are confirmed` |
| agent | task_protocol Phase 2,4,5 | C/A | 322 | Phase 2 service list (@deep-researcher/@repo-index) is C; Phase 4 'run tests after' and Phase 5 'report residual risks' are A |  |  | `@repo-index (structure + file shortlist)` |
| agent | guidance | C | 218 | '@repo-index on first task per session' is routing; 'repo before web' and MCP fallback are A |  |  | `@repo-index on first task per session` |
| agent | token_discipline | D | 220 | Tone/format persona (emoji status); unmeasurable |  |  | `Short status: 🔄 Investigating…, ✅ Tests: 42/42` |
| agent | examples agent-wrong-type | C | 365 | Agent routing fact (frontend-architect vs backend-architect) |  |  | `delegate to backend-architect, or to performance-engineer` |
| agent | gotchas context-pollution | B | 348 | Isolation + pre-commitment: write the check BEFORE dispatch, judge delegate summary against it, do not read delegate output files. Real mechanism against delegate-result anchoring. Tail cites RULES_DELEGATION.md (repo pointer, D) | A4/A3 (delegate result as anchor) | mechanism — ordering (criterion precedes result) + isolation | `Judge the returned summary against the check written before dispatch` |
| agent | bounds | D | 225 | Restates task_protocol gate and 'speculates without research' |  |  | `implements before scope and success criteria are confirmed` |
| agent | handoff | C | 44 | Routing |  |  | `/sc:implement /sc:research` |
| analyze | description | C | 321 | Routing vs /sc:review / direct read |  |  | `Not for one diff, PR, plan or spec — /sc:review` |
| analyze | role/mission | D | 135 | Duplicates description |  |  | `Code analysis across quality, security, performance` |
| analyze | syntax | C | 142 | Flag enumeration |  |  | `--focus perf\|security\|quality\|arch\|a11y\|testing\|rules` |
| analyze | flow 1-4 | A | 330 | Generic discover/scan/evaluate/recommend; severity rating is default behaviour. Scan is 'per --focus' = inside the user's frame |  |  | `Scan: Domain-specific analysis per --focus` |
| analyze | flow 5-6 Report/Bridge | C | 380 | Output paths, slug default, README update, /sc:plan bridge |  |  | `docs/features/<slug>/03-analysis.md` |
| analyze | flags | C | 419 | Flag semantics (quick vs deep, rules focus) |  |  | `deep covers the whole target and ties every finding` |
| analyze | outputs | C | 638 | Path routing table; duplicates flow step 5 (~40% redundant) |  |  | `docs/analysis/<target>-<username>-YYYY-MM-DD.json` |
| analyze | tools | A | 175 | Model knows Glob/Grep/Read |  |  | `Glob: File discovery` |
| analyze | focus_agent_mapping | C | 304 | Agent routing by focus |  |  | `security → @security-engineer \| perf → @performance-engineer` |
| analyze | rules_analysis | C | 843 | Project-specific audit procedure (R01–R21 table, violated_rule grep, maturity stages); could be shortened |  |  | `grep `violated_rule: "[RNN Name]"` → heatmap` |
| analyze | examples table | D | 450 | Usage illustrations; adds nothing beyond flags |  |  | ``--focus rules` \| Rule heatmap + maturity label` |
| analyze | examples invalid-focus | D | 350 | Duplicates the flag enum |  |  | `'everything' not valid` |
| analyze | gotchas evidence-fabrication | D | 200 | Exhortation ('evidence must precede proposals'); names an ordering but installs no gate or output slot. Targets A1/A3 but is not B | (A1/A3 — exhortation, not B) | exhortation | `Evidence (code, config, measurements) must precede proposals` |
| analyze | gotchas analysis-loop | D | 142 | Unmeasurable self-monitoring instruction |  |  | `same conclusion twice on the same question` |
| analyze | bounds | D | 361 | Mostly restates; 'delegate narrative to /sc:reflect' is a small routing fact |  |  | `delegate that to /sc:reflect` |
| analyze | handoff | C | 64 | Routing |  |  | `/sc:plan /sc:improve /sc:cleanup /sc:implement` |
| auto-improve | description | C | 320 | Routing vs plain 'improve this' |  |  | `Not for "improve this" or "optimize this" — edit directly` |
| auto-improve | role/mission | D | 258 | Duplicates description |  |  | `Karpathy AutoResearch pattern` |
| auto-improve | syntax | C | 194 | Flag list |  |  | `--eval-cmd [sh] --metric [jmespath]` |
| auto-improve | flow | C | 709 | Operational facts: unsandboxed confirm, exact spawn command, Start-Job kills worker, PID file |  |  | `never PowerShell `Start-Job`, measured to kill the worker` |
| auto-improve | flags | C | 948 | Flag semantics and defaults |  |  | `--budget <dur>: wall-clock limit for the whole loop (default 8h)` |
| auto-improve | outputs | C | 371 | Artifact paths and TSV schema |  |  | `8-column lineage (cycle_id, timestamp, commit_hash` |
| auto-improve | tools | A | 117 | Trivial |  |  | `Bash: spawn Python worker subprocess` |
| auto-improve | gotchas | C | 1621 | All project facts: session-end survival unverified, mutator tool surface, model billing, never-bare-python. Longest section; could be trimmed ~30% |  |  | `worker import `superclaude.scripts.auto_improve.*`, absent from the install tree` |
| auto-improve | examples | C | 538 | Shows argument shapes incl. --dry-run JSON escaping |  |  | `--eval-cmd "echo '{\"x\":1}'" --metric 'x' --dry-run` |
| auto-improve | bounds | D | 365 | Restates flow and gotchas |  |  | `skip the Phase 0 confirm step` |
| auto-improve | handoff | C | 54 | Routing |  |  | `/sc:auto-improve --status /sc:review` |
| brainstorm | description | C | 298 | Routing |  |  | `Not for routine questions or casual "what should we do about X"` |
| brainstorm | role/mission | D | 150 | Duplicates description |  |  | `Socratic dialogue + systematic exploration` |
| brainstorm | syntax | C | 156 | Flags; --vs and --delegate appear here but are never defined in <flags> |  |  | `[--vs [standard\|cot\|multi]] [--delegate]` |
| brainstorm | flow 1 Explore / intent read | B | 330 | Ordering: read 00-intent.md before analysis and map discovery back to its five fields (coverage table). Keeps the requester's purpose visible (I0). Caveat: 'keep its wording as the anchor' forbids questioning the premise — hardens R1 | I0 (purpose carried); worsens R1 | mechanism — ordering + required coverage table | `read it first and keep its wording as the anchor` |
| brainstorm | flow 2-3 Analyze/Validate | D | 250 | 'multi-agent coordination with domain expertise', --vs k perspectives with probabilities: undefined feature (VS) referenced; exhortative |  |  | `generate k perspectives with probabilities and a landscape synthesis` |
| brainstorm | flow 4 Specify | C | 230 | Output paths and slug default |  |  | `docs/features/<slug>/01-discovery.md` |
| brainstorm | flow 5 Approve | A | 90 | Model shows the spec before proceeding anyway |  |  | `no proceed without confirm` |
| brainstorm | flow 6 Self-review gate | B | 260 | Isolation: author does not review own spec; spec stays draft until /sc:review. Real gate, but /sc:review runs in the same session context, so the isolation is procedural, not informational | A3 (self-anchor) | mechanism — gate + handoff; isolation weak (same context) | `Claude does not review the spec itself in place of /sc:review` |
| brainstorm | flow 7-8 Decision tag / Handoff | B | 260 | Tags each decision confirmed vs delegated and forces --audit-delegated. Output-shape rule that catches accepted defaults | R3 (default acceptance) | mechanism — classification + routed audit | `With delegated decisions, add --audit-delegated` |
| brainstorm | flags | C | 351 | Strategy semantics |  |  | `agile splits the work into parallel streams` |
| brainstorm | self_review | B/D | 459 | Same gate as flow 6 with rationale; ~60% duplicate. Keep one copy | A3 | mechanism (duplicate of flow 6) | `A direct route to /sc:plan from the Approve step is forbidden` |
| brainstorm | decision_modes | B | 584 | Operational definition of 'delegated' (bare yes, silent accept of ★) — the only text in scope that names the starred-default failure and acts on it | R3 | mechanism — detection rule + mandatory audit phrase | `bare "yes", "proceed", "looks good", or silent accept of ★` |
| brainstorm | outputs | C | 366 | Path table; duplicates flow 4 |  |  | `docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md` |
| brainstorm | tools | A | 254 | Trivial |  |  | `Read/Write/Edit: requirements docs` |
| brainstorm | examples table | D | 780 | Seven rows; --vs/k/tau examples reference an undefined feature (leak); 'Cross-session via /sc:save' unexplained |  |  | `'API design' --vs cot [k:3] [tau:0.20]` |
| brainstorm | examples brainstorm-then-implement | D | 350 | Restates bounds; model does not code during a discovery dialogue |  |  | `Brainstorm = discovery-only` |
| brainstorm | gotchas evidence-fabrication/analysis-loop | D | 300 | Verbatim duplicates of analyze.md gotchas; exhortations | (A1/A3 — exhortation) | exhortation | `kill that line of analysis + move to next topic` |
| brainstorm | gotchas skip-review | D | 190 | Third statement of the self-review gate |  |  | `The gate is hard, not advisory` |
| brainstorm | bounds | D | 372 | Restates flow |  |  | `routes directly to /sc:plan without /sc:review` |
| brainstorm | handoff | C | 61 | Routing |  |  | `/sc:review /sc:plan /sc:design /sc:research` |
| build | description | C | 252 | Routing vs plain Bash |  |  | `Not for a single build command (npm run build` |
| build | role/mission | D | 132 | Duplicate |  |  | `Build, compile and package projects` |
| build | syntax | C | 93 | Flags |  |  | `[--type dev\|prod\|test] [--clean]` |
| build | flow | A | 348 | Read config → validate → run → report: default behaviour |  |  | `run the build and watch its output` |
| build | flags | C | 466 | --clean policy (only config-named outDir, never git clean) is a project rule |  |  | `never git clean` |
| build | outputs | D | 450 | Three rows saying 'tool-generated output directory'; no information |  |  | `output directory named in the build config (tool-generated)` |
| build | tools | A | 122 | Trivial |  |  | `Bash: run the build` |
| build | examples table | D | 330 | Usage illustrations |  |  | ``frontend --verbose` \| Detailed component build` |
| build | examples build-failure-retry | C | 420 | Carries the policy 'never installs dependencies'; could move to bounds and drop the example |  |  | `/sc:build never installs dependencies` |
| build | bounds | C | 222 | Policy the model cannot know (no config edits, no installs, no deploy, no report file) |  |  | `modifies build config, installs dependencies, deploys` |
| build | handoff | C | 43 | Routing |  |  | `/sc:test /sc:troubleshoot` |
| business-panel | description | C | 254 | Routing |  |  | `Not for a single-perspective business question` |
| business-panel | role/mission | D | 119 | Duplicate |  |  | `Multi-expert business analysis with adaptive modes` |
| business-panel | syntax | C | 181 | Flags |  |  | `[--mode discussion\|debate\|socratic\|adaptive]` |
| business-panel | flow | D | 393 | Generic route/analyze/synthesize/present; '2-3 by default' is a small C fact |  |  | `apply the selected experts' frameworks (2-3 by default` |
| business-panel | flags | C | 625 | Flag semantics; --focus collision with global flag |  |  | `unrelated to the global --focus` |
| business-panel | experts | C | 208 | Surname list + SSOT pointer |  |  | `christensen, porter, drucker, godin, kim-mauborgne` |
| business-panel | modes | C | 218 | Mode definitions (short) |  |  | `adaptive: System picks by content` |
| business-panel | examples table | D | 400 | Usage illustrations |  |  | ``startup-pitch.md --mode socratic --all-experts`` |
| business-panel | examples panel-technical-question | C | 370 | Routing to /sc:troubleshoot or /sc:explain; could be one line |  |  | `Wrong tool for code` |
| business-panel | gotchas | D | 242 | single-framework duplicates flow; 'label which framework' is default attribution behaviour |  |  | `Never present opinions as consensus` |
| business-panel | bounds | D | 174 | Boilerplate |  |  | `replaces professional advice or decides for the user` |
| business-panel | handoff | C | 43 | Routing |  |  | `/sc:brainstorm /sc:design` |
| cleanup | description | C | 233 | Routing |  |  | `Not for tidying one function or import` |
| cleanup | role/mission | D | 136 | Duplicate |  |  | `Clean code systematically` |
| cleanup | syntax | C | 132 | Flags |  |  | `[--safe\|--aggressive] [--interactive] [--dry-run\|--apply]` |
| cleanup | flow 1,2,4,5 | A | 300 | Find candidates, check safety, run tests, report: default |  |  | `confirm no functionality was lost (tests pass)` |
| cleanup | flow 3 Execute (--type docs order) | C | 223 | Validator check order for --type docs |  |  | `cross-link-form flags `[[...]]` links, slug-overlap suggests promotions` |
| cleanup | flags | C | 1171 | Safe/aggressive tiers, --apply requirement, dynamic-reference search; long but factual |  |  | `remove code with no static reference only after a search for dynamic references` |
| cleanup | outputs | C | 625 | Per-type action table; ~50% duplicates flags |  |  | `delete each batch after the user confirms it` |
| cleanup | tools | A | 220 | Trivial |  |  | `Edit: apply safe changes` |
| cleanup | validator_checks | C | 1279 | Project-specific lint rules (regex, slug patterns, README regen) |  |  | `Grep `\[\[[a-z0-9-]+\]\]` pattern across `docs/features/*/*.md`` |
| cleanup | examples table | D | 500 | Usage illustrations; three --type docs rows restate flags |  |  | ``--type docs --dry-run` \| Preview what --apply would change` |
| cleanup | examples aggressive-without-review | D | 420 | Dry-run before aggressive: model does this given the flags |  |  | `risks removing code that looks unused but is referenced dynamically` |
| cleanup | gotchas scope-check / verify-unused | A | 230 | Scope discipline and grep-before-delete are default |  |  | `confirm a file is truly unused (grep for references)` |
| cleanup | gotchas code-block-false-positive / slug-overlap-noise / manual-gate | D | 688 | Each duplicates a validator_checks or flags statement |  |  | `pre-filter ` ``` ` blocks before matching` |
| cleanup | bounds | D | 252 | Boilerplate |  |  | `overrides exclusions, or breaks functionality` |
| cleanup | auto_fix_threshold | C | 268 | Policy tiers; duplicates --safe/--aggressive flag text (keep one) |  |  | `File deletions (empty or orphan files: list the paths, one confirmation per batch)` |
| cleanup | handoff | C | 36 | Routing |  |  | `/sc:test /sc:build` |
| design | description | C | 284 | Routing |  |  | `Not for structuring one function or a small sketch` |
| design | role/mission | D | 140 | Duplicate |  |  | `Design system architecture, APIs, component interfaces` |
| design | syntax | C | 156 | Flags |  |  | `[--from docs/features/<slug>/01-discovery.md]` |
| design | flow 1 Analyze | C | 160 | Which prior docs to read (00-intent, 01-discovery). Receives documents with no purpose step before them |  |  | `read the `--from` doc, or the slug folder's `00-intent.md`` |
| design | flow 2-5 Plan/Design/Constraints/Necessity | D | 420 | Generic; Constraints is good practice; Necessity cites [R18] (rule living elsewhere; exhortation) |  |  | `apply [R18 Necessity Test] — defer components lacking` |
| design | flow 6 Concerns | B | 230 | Required output slot for constraint conflicts and 'design cannot satisfy the intent', owner resolves before plan. Surfaces frame/intent mismatch instead of silently solving inside it | R2/R1 (frame vs intent); I0 | mechanism — mandatory output section ('or none') | `where the design cannot satisfy the intent — the owner resolves these` |
| design | flow 7 Validate coverage | B | 200 | Requirement-by-section coverage list; uncovered requirements forced into Areas of concern. Post-hoc check against the input, counters drift from the design the model settled on | A3 (self-anchor), I0 criterion | mechanism — required coverage table (after design, not before) | `a requirement no section covers goes under Areas of concern` |
| design | flow 8 Document | C | 204 | Output paths |  |  | `docs/features/<slug>/04-design.md` |
| design | flags | C | 348 | Flag semantics |  |  | `code: interface definitions (types, signatures) with no implementation` |
| design | outputs | C | 740 | Paths, sections per type, required Areas of concern |  |  | `Required in every type: an "Areas of concern" section` |
| design | tools | A | 160 | Trivial |  |  | `Write: Design documentation` |
| design | examples table | D | 330 | Usage illustrations |  |  | ``payment-api --type api --format spec` \| API specification` |
| design | examples design-without-requirements | C | 400 | Routes to /sc:brainstorm first; one line would do |  |  | `/sc:brainstorm 'payment system requirements' first` |
| design | gotchas over-architect / existing-check | D | 190 | R18 duplicate; 'check existing doc' is default |  |  | `Only design what needed now` |
| design | gotchas workflow-fanout | C | 216 | Delegation fact: subagent writes are discarded, main loop writes |  |  | `fan-out subagents RETURN design markdown — subprocess writes discarded` |
| design | bounds | D | 202 | Boilerplate |  |  | `generates implementation code, modifies the existing architecture` |
| design | handoff | C | 52 | Routing |  |  | `/sc:plan /sc:implement /sc:roadmap` |
| document | description | C | 285 | Routing |  |  | `Not for one docstring, comment or README line` |
| document | role/mission | D | 129 | Duplicate |  |  | `Generate focused docs for components` |
| document | syntax | C | 98 | Flags |  |  | `[--type inline\|external\|api\|guide]` |
| document | flow | A | 302 | Analyze/audience/generate/format/integrate: default. Step 2 'name the audience and what it needs' is the nearest thing to a purpose step, but no criterion |  |  | `Identify: name the audience and what it needs` |
| document | flags | C | 238 | brief vs detailed definition |  |  | `detailed: adds parameters, return values, errors and examples` |
| document | outputs | C | 616 | Living-doc paths, shared API.md with /sc:index, metrics |  |  | `shared with /sc:index --type api, so an existing file is updated in place` |
| document | tools | A | 206 | Trivial |  |  | `Grep: Ref extraction` |
| document | examples | D | 624 | Illustrations; 'don't document mid-refactor' is judgement the model has |  |  | `documenting code mid-refactor leaves the docs stale` |
| document | gotchas | D | 280 | no-unsolicited is default; naming duplicates outputs |  |  | `UPPER_SNAKE in docs/reports/, no date/username` |
| document | bounds | D | 226 | Boilerplate |  |  | `exposes sensitive details` |
| document | handoff | C | 43 | Routing |  |  | `/sc:implement /sc:improve` |
| estimate | description | C | 251 | Routing |  |  | `Not for a quick "is this hard?" — answer in one line` |
| estimate | role/mission | D | 158 | Duplicate |  |  | `Give development estimates for tasks` |
| estimate | syntax | C | 79 | Flags |  |  | `[--type effort\|complexity] [--breakdown]` |
| estimate | flow | A | 345 | Analyze/calculate/validate/present with confidence: default. No step isolates the model from a prior number in the request |  |  | `give the breakdown, a confidence level with the assumption it rests on` |
| estimate | flags | C | 256 | Flag semantics (S/M/L/XL) |  |  | `effort: relative size (S/M/L/XL) with a confidence level` |
| estimate | tools | A | 210 | Trivial |  |  | `Agent: Multi-domain estimation delegation` |
| estimate | examples | D | 691 | Illustrations; 'make it better' has no scope — model already asks |  |  | `there is no measurable scope` |
| estimate | gotchas relative-size | B | 260 | Output-shape rule that refuses the unit the question imposes (hours/days) and states what would calibrate it. Resists a frame carried in the request | R3/R2 (question's unit frames the answer) | mechanism — fixed output shape + calibration ask | `When the user asks for hours or days, say why, then give the size` |
| estimate | gotchas scope-assumptions | D | 99 | 'make assumptions explicit before estimating' — exhortation | (R1 — exhortation) | exhortation | `make scope assumptions explicit before estimating` |
| estimate | bounds | D | 252 | Restates relative-size |  |  | `presents a relative size as a deadline` |
| estimate | handoff | C | 43 | Routing |  |  | `/sc:roadmap /sc:implement` |
| explain | description | C | 256 | Routing |  |  | `Not for "what does this function do?"` |
| explain | role/mission | D | 148 | Duplicate |  |  | `educational clarity` |
| explain | syntax | C | 131 | Flags |  |  | `[--level basic\|intermediate\|advanced]` |
| explain | flow | A | 202 | Analyze/assess/structure/generate/validate: default |  |  | `Structure: Progressive complexity` |
| explain | flags | C | 493 | interactive format definition is the only non-obvious fact |  |  | `one comprehension question between steps` |
| explain | tools | A | 152 | Trivial |  |  | `Agent: Complex explain delegate` |
| explain | examples | D | 658 | Illustrations; 'C7 patterns' is unexplained jargon |  |  | ``react-hooks --level intermediate --context react` \| C7 patterns` |
| explain | gotchas | D | 231 | symbolic-first and 'check memory for expertise' are generic |  |  | `Check user context/memory for expertise level` |
| explain | bounds | D | 198 | Boilerplate |  |  | `reveals sensitive information` |
| explain | handoff | C | 56 | Routing |  |  | `/sc:implement /sc:improve /sc:document` |
| git | description | C | 302 | Routing + which ops need confirmation |  |  | `push --force, reset --hard and rebase each still need their own confirmation` |
| git | role/mission | D | 121 | Duplicate |  |  | `smart commit messages and workflow guidance` |
| git | syntax | C | 110 | Flags |  |  | `[--pr-status] [--from-pr PR#\|URL]` |
| git | flow | A | 289 | Analyze state/validate/execute/report: default |  |  | `read the repo state and pending changes` |
| git | flags | C | 566 | --from-pr procedure incl. stash question |  |  | `with uncommitted changes, first ask whether to stash them or stop` |
| git | tools | A | 119 | Trivial |  |  | `Bash: run git and gh commands` |
| git | pr_status_integration | C | 496 | gh json fields; state→dot mapping is D tone. Shorten to the command line |  |  | `gh pr view --json state,reviewDecision,isDraft` |
| git | from_pr | C | 444 | 'claude --from-pr is a start-up option; never run from Bash' is the one fact; rest duplicates flags |  |  | `never run it from Bash` |
| git | examples | A | 603 | Force-push to main refusal is default Claude Code behaviour |  |  | `force-pushing main/master destroys teammates' work` |
| git | gotchas | A | 374 | never amend / retest after merge / confirm base branch: default |  |  | `make new commits; never amend unless asked` |
| git | bounds | D | 282 | Boilerplate |  |  | `resolves complex merges that need manual review` |
| git | safety_rules | C | 273 | Which ops skip the second confirm (project policy); partially duplicates description |  |  | `the op the user typed into /sc:git; no second confirm` |
| git | handoff | C | 36 | Routing |  |  | `/sc:test /sc:build` |
| help | description | C | 179 | Routing |  |  | `Not for "help me" with a task` |
| help | role/mission | D | 103 | Duplicate |  |  | `List all /sc commands` |
| help | syntax | C | 50 | Flags |  |  | `/sc:help [command-name] [--flags]` |
| help | flow | C | 264 | What to display per argument |  |  | `a command-name → that command's syntax, its flags, and the "Not for" line` |
| help | flags | C | 232 | Where flags live; effort levels native |  |  | `Effort levels are Claude Code native, not managed by superclaude` |
| help | commands | C | 1945 | The deliverable itself: 35-line routing list |  |  | `intent: capture a request in the requester's own words before analysis` |
| help | scope_map | C | 620 | Disambiguation between overlapping commands — highest-value routing text in scope |  |  | `analyze (static quality metrics) \| review (PR/diff-level) \| reflect (post-impl self-check)` |
| help | examples | A | 301 | 'help does not execute' is obvious |  |  | `help reference-only. Shows info, no exec` |
| help | gotchas | D | 185 | stale-list refers to commands/sc/ (install path, fine) but is self-doubt; flag-docs duplicates flags |  |  | `cmd list may go stale` |
| help | bounds | D | 207 | Boilerplate |  |  | `executes commands, creates files, activates modes` |
| help | handoff | C | 45 | Routing |  |  | `/sc:recommend /sc:[command]` |
| implement | description | C | 254 | Routing |  |  | `Not for a routine function, bug fix or single-file edit` |
| implement | role/mission | D | 137 | Duplicate |  |  | `agent delegation and MCP integration` |
| implement | syntax | C | 159 | Flags |  |  | `[--plan docs/plans/...] [--safe] [--with-tests]` |
| implement | flow 1 Load | C | 300 | Split-plan index/phase file reading order |  |  | `a split plan's index is read here and each phase file it links when that phase starts` |
| implement | flow 2 Plan | D | 180 | 'verify simplest viable approach' is exhortation; 'follow the plan's task order exactly' HARDENS A3 (prior plan becomes law before any evidence check) | (A3 — anti-pattern) | exhortation / anchor-hardening | `with --plan, follow the plan's task order exactly` |
| implement | flow 3 Checkpoint | C | 280 | >3-file approval gate and 'plan invocation is the approval' — project policy; 'ask only before departing from the plan' is the only re-plan permission |  |  | `ask only before departing from the plan` |
| implement | flow 4 Execute | A | 150 | Write code following conventions |  |  | `write the code following the framework's conventions` |
| implement | flow 5 Phase Gate | B | 190 | Re-plan trigger after each phase: build+run, then ask whether the next phase is already solved. Only explicit re-evaluation of a prior plan against evidence in scope. Narrow (only 'skip', never 'change') | A3 (re-plan trigger) | mechanism — checkpoint after each phase | `"Does this already solve the next phase's problem?" If yes, skip with reason` |
| implement | flow 6 Validate | A | 90 | Run checks and verify commands |  |  | `run each task's verify command` |
| implement | flow 7 Integrate | C | 680 | Deviations heading, checkbox/status semantics, README phase: — project conventions. Dense; could be a table |  |  | ``status: complete` with an open box is a defect` |
| implement | flags | C | 804 | Flag semantics incl. collision with global --plan and --safe-mode |  |  | `unrelated to the global --plan, whose 5-line-plan directive does not apply` |
| implement | tools | A | 159 | Trivial |  |  | `Write/Edit: Code gen` |
| implement | examples table | D | 330 | Illustrations; 'C7 Vue patterns' jargon |  |  | ``dashboard widget --framework vue` \| C7 Vue patterns` |
| implement | examples scope-creep | A | 430 | Not refactoring adjacent code is default |  |  | `"Add logout button" does not authorize refactoring adjacent code` |
| implement | gotchas status-check / scope-discipline | D | 200 | [R02] pointer to a rule elsewhere; scope discipline is A |  |  | `Run [R02 Status Check] pre-impl` |
| implement | gotchas workflow-fanout | C | 209 | Subagent writes discarded; main loop applies and runs checkpoint |  |  | `fan-out subagents RETURN code/results — subprocess writes discarded` |
| implement | bounds | D | 219 | Boilerplate |  |  | `conflicts with security, or overrides safety` |
| implement | handoff | C | 36 | Routing |  |  | `/sc:test /sc:build` |
| improve | description | C | 261 | Routing |  |  | `Not for one function or a small refactor` |
| improve | role/mission | D | 141 | Duplicate |  |  | `systematic improvements to code quality` |
| improve | syntax | C | 113 | Flags |  |  | `[--type quality\|performance\|maintainability\|style]` |
| improve | flow | A | 241 | Analyze/plan/execute/validate/document: default |  |  | `Validate: Functionality preserved` |
| improve | flags --type performance baseline | B | 200 | Hard stop: no performance work without a measured baseline; routes to /sc:analyze. Gate that keeps a prompt-supplied 'it is slow because X' from being acted on before measurement | A1/R1 (suspected cause in prompt) | mechanism — stop + reroute (performance type only) | `performance needs a measured baseline first, else stop` |
| improve | flags --safe / --interactive | C | 282 | Flag semantics |  |  | `changes to exported functions, config files or shared modules are listed as proposals` |
| improve | examples | D | 273 | Illustrations; row 3 duplicates the baseline flag |  |  | `Error: run /sc:analyze --focus perf first` |
| improve | gotchas | D | 408 | R18 pointer + exhortation; halo-improvement is scope discipline (A) |  |  | `"safer/better" alone insufficient justification` |
| improve | bounds | D | 268 | Boilerplate; fallback 'ask when scope exceeds target' is A |  |  | `Ask user when improvement scope exceeds target boundary` |
| improve | handoff | C | 38 | Routing |  |  | `/sc:test /sc:analyze` |
| index | description | C | 237 | Routing |  |  | `Not for documenting one file — use /sc:document` |
| index | role/mission | D | 131 | Duplicate |  |  | `knowledge base under docs/reports/` |
| index | syntax | C | 94 | Flags |  |  | `[--type docs\|api\|structure\|readme] [--format md\|json\|yaml]` |
| index | flow | A | 333 | Generic; step 5 MANUAL-marker preservation is a C fact (~60 B) |  |  | `preserve sections marked <!-- MANUAL -->` |
| index | flags | C | 265 | Format semantics |  |  | `json or yaml writes the same stem with that extension` |
| index | outputs | C | 554 | Output files, in-place update rules, metrics |  |  | `in an existing README edit only the install, usage and api sections` |
| index | distinction | C | 196 | Routing vs index-repo |  |  | `index-repo: Minimal index (~3KB), token-efficient` |
| index | tools | A | 274 | Trivial |  |  | `Write: Doc creation + cross-referencing` |
| index | examples | D | 598 | Illustrations; monorepo example routes to index-repo (duplicate of distinction) |  |  | `Indexing entire large monorepo in one pass exhausts context` |
| index | gotchas | D | 193 | living-doc duplicates outputs; token-budget is A |  |  | `Use structural reading, not full file reads` |
| index | bounds | D | 230 | Boilerplate |  |  | `override manual docs, generate without analysis, bypass standards` |
| index | handoff | C | 43 | Routing |  |  | `/sc:implement /sc:improve` |
| index-repo | description | C | 232 | Routing |  |  | `Not for a routine code lookup — use Glob or Grep` |
| index-repo | role/mission | D | 125 | Duplicate |  |  | `compact repo index (~3KB)` |
| index-repo | syntax | C | 58 | Modes |  |  | `[mode=create\|update\|quick]` |
| index-repo | flow | C | 453 | Output paths and 5KB validation |  |  | `confirm both files exist and each is under 5KB` |
| index-repo | tools | A | 217 | Trivial; 'files changed since last index' is a small C fact |  |  | `files changed since the last index (mode=update)` |
| index-repo | patterns | D | 482 | Entry-file globs the model knows; output lines duplicate flow |  |  | `Entry: pyproject.toml \| package.json \| Cargo.toml` |
| index-repo | examples | D | 462 | Illustrations; 'needs a git repo' restates tools |  |  | `the repo index needs a git repo` |
| index-repo | gotchas | C | 237 | structure-only (no file content) is a real output constraint; token-target duplicates flow |  |  | `output the file structure and each file's role, not file content` |
| index-repo | bounds | D | 217 | Boilerplate |  |  | `writes an index file over 5KB` |
| index-repo | handoff | C | 39 | Routing |  |  | `/sc:analyze /sc:index` |
| init | description | C | 244 | Routing |  |  | `Not for "set this up" on entering a repo — ask what to set up` |
| init | role/mission | D | 152 | Duplicate |  |  | `selectable init tasks for first-session onboarding` |
| init | syntax | C | 52 | Flags |  |  | `/sc:init [tasks] [--quick] [--full]` |
| init | flow | C | 698 | Menu-driven procedure; dependency batching; 'not saved' reporting when auto memory off |  |  | `memory entries stored (or listed as not saved when auto memory is off)` |
| init | flags | D | 157 | Two lines pointing elsewhere |  |  | `preset, defined in the Select step and the menu section` |
| init | menu | C | 1026 | Task letters, dependencies, presets — the UI |  |  | `Presets: --quick (a,b) \| --full (a,b,c,d,e,f,g,h,i)` |
| init | dependency_graph | C | 212 | Batch order; partially duplicates menu '(requires a)' |  |  | `Batch 2 (wait for prereq): b←a, d←c, g←a` |
| init | task_outputs | C | 635 | Artifact locations per task |  |  | `adr/0001-*.md, UI-GUIDE.md \| docs/ (project root)` |
| init | safety_rules | C | 1571 | Template source path, memory layout, auto-memory-off rule, idempotence. 'show diff before editing CLAUDE.md' and 'confirm before install' are A (~250 B) |  |  | `from ~/.claude/superclaude/templates/docs-scaffold/` |
| init | outputs | D | 323 | Duplicates task_outputs |  |  | `PROJECT_INDEX.md \| Project structure map (task a)` |
| init | tools | A | 268 | Trivial; Agent(repo-index) routing is C (~40 B) |  |  | `Agent(repo-index): Delegate structure analysis for task (a)` |
| init | examples | D | 868 | Six usage rows + missing-prerequisite example restating dependency_graph |  |  | `Task (d) requires (c). Add dependency check?` |
| init | gotchas | A | 129 | Do not overwrite user config: default |  |  | `Verify files do not already exist before creating` |
| init | bounds | D | 430 | Restates flow and safety_rules |  |  | `auto-executes tasks the user did not select` |
| init | handoff | C | 49 | Routing |  |  | `/sc:load /sc:implement /sc:test` |
| insight | description | C | 258 | Routing |  |  | `Not for "let me note this" in passing — write no entry` |
| insight | role/mission | D | 146 | Duplicate |  |  | `per-project JSONL for human and tool analysis` |
| insight | syntax | C | 85 | Flags |  |  | `[--list] [--query key=value] [--stats] [--review]` |
| insight | flow | C | 1189 | Modes, dedup command, CLI-only append, review/promote/discard procedure |  |  | `run `superclaude insight list --limit 20` to check recent entries` |
| insight | flags | D | 255 | Four lines pointing back to flow |  |  | `read mode, defined in the Read modes step` |
| insight | outputs | C | 344 | Per-mode output |  |  | ``--list` \| Formatted recent insights (last 20)` |
| insight | storage files + memory link | C | 400 | File paths; memory vs insight distinction |  |  | `Memory = LLM read. Insight = human/tool query` |
| insight | storage Auto-produce / Auto-harvest | D | 1313 | Hook internals (Stop fingerprint, SessionEnd/PreCompact harvest, sidechain skip, ledger). The command executor never runs these; repo/maintainer leak |  |  | `the gate compare a `SessionStart` tree fingerprint against the current one` |
| insight | schema | C | 881 | Required/optional fields, type taxonomy |  |  | `annotation: relevance link to existing insight (need ref_ts` |
| insight | tools | C | 157 | All I/O through the CLI |  |  | `All file I/O on insights.jsonl go through this CLI` |
| insight | script_reference | C | 774 | CLI invocations; ~40% duplicates flow |  |  | `superclaude insight discard --index 0,1,2      # one call, indices no shift` |
| insight | examples | D | 590 | Illustrations duplicating flow/outputs |  |  | ``/sc:insight --stats` \| Type counts` |
| insight | gotchas | C | 1301 | never-bare-python, discard-is-final + batch indices, promote-descending-indices are real facts; script-only-writes and review-requires-classification duplicate flow (~450 B D) |  |  | `go highest index first (`cmd_promote` pop by index)` |
| insight | bounds | D | 365 | Restates flow |  |  | `hand-edits insights.jsonl` |
| insight | handoff | C | 38 | Routing |  |  | `/sc:save /sc:analyze` |

## 3. Anchor-point map

| File | Moment | What arrives | B step before it? |
|---|---|---|---|
| agent | flow 1 Parse | task-description (action instruction) | none before Parse — 'identify the task type' frames first; task_protocol Phase 1 'Confirm scope, success criteria, blockers, acceptance tests' comes after and confirms with the user rather than inferring purpose |
| agent | flow 3 Monitor | delegate results | yes — gotchas: 'Judge the returned summary against the check written before dispatch' |
| agent | task_protocol Phase 4 | own Phase 2 plan | none — no re-plan trigger between Plan and Implement; 'escalate if stalled' only |
| analyze | flow 1-2 Discover/Scan | target + --focus (frame) + code comments/README read during scan | none — scan is 'per --focus'; evidence-fabrication gotcha is exhortation |
| analyze | rules_analysis | memory files with violated_rule tags (prior AI output) | none |
| auto-improve | flow 1 Parse | --eval-cmd / --metric (user-chosen objective = frame) | none — Phase 0 confirm is safety only; by design the metric is accepted as given |
| brainstorm | flow 1 Explore | topic (action instruction) | none — Socratic dialogue is where purpose could emerge, but no step says 'state the purpose and criterion' |
| brainstorm | flow 1 Explore | 00-intent.md (prior document) | partial — read first and mapped via coverage table (I0), but 'keep its wording as the anchor' forbids questioning it (R1 hardened) |
| brainstorm | flow 1-5 dialogue | user answers to option lists / ★ defaults | yes, post hoc — decision_modes: 'silent accept of ★' → delegated → mandatory audit. Nothing stops the ★ being offered |
| brainstorm | flow 5-6 Approve | own spec | yes — self_review: 'Claude does not review the spec itself in place of /sc:review' |
| build | flow 3 Execute | build error output | none (low anchor risk); error-path says stop and report |
| business-panel | flow 1-2 | market-analysis.md / pitch doc (document anchor; its premise) | none — experts apply frameworks to the doc as given; no premise check before Analyze |
| cleanup | flow 1 Analyze | target + --type (frame: user says 'dead code') | none |
| cleanup | flow 2 Plan → 3 Execute | own cleanup plan | none — no re-plan trigger; Validate is post hoc tests |
| design | flow 1 Analyze | --from / 01-discovery / 00-intent (document + prior plan) | none before; after: flow 6 'where the design cannot satisfy the intent' and flow 7 coverage table (post hoc B) |
| design | flow 2 Plan → 3 Design | own design approach | partial — flow 7 'a requirement no section covers goes under Areas of concern' re-checks after the fact |
| document | flow 1 Analyze | target + existing docs | none — flow 2 'name the audience and what it needs' is audience, not purpose/criterion |
| estimate | flow 1 Analyze | target, often with a prior number ('I think 2 days') — A1 | none — no step sizes before reading the user's number; relative-size gotcha only resists the unit (hours/days) |
| explain | flow 1-2 | target + --level | none (low stakes) |
| git | flow 1-3 | operation + --from-pr body/comments (document) | none — safety_rules gate destructive ops only; PR body is loaded as context with no check |
| help | flow 1 | command-name | n/a |
| implement | flow 1 Load | --plan doc (prior plan A3 + document A2) | none — and flow 2 'follow the plan's task order exactly' hardens it; flow 3 'ask only before departing from the plan' is the only exit |
| implement | flow 5 Phase Gate | own progress vs remaining plan | yes — 'Does this already solve the next phase's problem? If yes, skip with reason' (skip-only re-plan) |
| implement | flow 2 Plan (delegation) | subagent code/results | none — workflow-fanout says main loop applies; no pre-dispatch check like agent.md's |
| improve | flow 1 Analyze | target + --type (user's diagnosis: 'performance') | yes for performance only — 'performance needs a measured baseline first, else stop'; none for quality/maintainability/style |
| index | flow 1 Analyze | existing README/API.md | none (edits in place; MANUAL sections preserved — not an anchor issue) |
| index-repo | flow 1-3 | entry files | n/a |
| init | flow 1-2 | existing CLAUDE.md / config | none needed — safety_rules show diff before applying |
| insight | flow 7 Review | harvested INSIGHT: markers (prior AI/user output) | none — review-requires-classification only forces a type label, not a truth check |

**I0 check (purpose + success criterion stated before acting):**

- agent.md is the only file with a criterion gate: `Phase 1 - Clarify: Confirm scope, success criteria, blockers, acceptance tests` and `Phase 3 - Iterate: no implementation until Phase 1 scope, success criteria and acceptance checks are confirmed`. It asks the user to confirm a criterion; it does not make the model infer the unstated purpose or look beyond the named target, and flow step 1 (`identify the task type`) frames before it runs.
- brainstorm.md carries purpose only when a prior `00-intent.md` exists (`read it first and keep its wording as the anchor`), and then forbids questioning it.
- design.md checks intent only after the design exists (`where the design cannot satisfy the intent`).
- The other 16 files have no purpose or criterion step. implement, analyze, estimate, cleanup, improve, document, business-panel all begin by analyzing the named target inside the frame the request supplies.

## 4. Totals per class

| Class | Rows | ~Bytes | Share |
|---|---|---|---|
| A | 34 | 8204 | 10% |
| B | 12 | 3421 | 4% |
| C | 126 | 44557 | 55% |
| D | 82 | 25078 | 31% |
| Total classified | 252 | 81261 | 100% |

Notes on the totals:
- Mixed rows (`C/A`, `B/D`) were split half-and-half.
- C is inflated by internal duplication: paths and flag semantics are typically stated two or three times per file (flow step, `<flags>`, `<outputs>`, `<gotchas>`, `<examples>`). Reducing each C fact to one statement would cut C by roughly 30% (≈13 KB) without losing a fact.
- Every file carries ~0.5 KB of fixed boilerplate that is A or D: `<role>` (duplicate of description), `<tools>`, `<bounds>`, and the usage-example table. Across 19 files that is ≈10 KB.
- B is 11 rows / ≈3.4 KB (4%), concentrated in brainstorm (4), design (2), agent (2), implement (1), improve (1), estimate (1). None of them is a purpose-inference step; the closest is agent.md's user-confirmed success criterion.

## 5. Top 10 findings (ranked)

1. **No file makes the model infer the purpose before acting (I0 gap, all 19).** The action instruction / target / plan arrives at step 1 of every flow and the first verb is Analyze/Parse/Discover/Load. agent.md's `Confirm scope, success criteria` is the only criterion gate and it is user-confirmed, not model-derived. A single shared step — 'before reading the target, state the purpose this serves and one observable success criterion; list files outside the named target that bear on it' — would do more than all current B rows combined.
2. **implement.md hardens the prior-plan anchor (A3).** `with --plan, follow the plan's task order exactly` and `invoking on that plan is the approval: proceed` make the plan law before any evidence check; the Phase Gate re-plan trigger allows only *skip*, never *change*, and runs after the first phase is already built. Replace 'exactly' with a re-entry rule: re-derive the criterion from the plan's purpose section, then check task 1 against it.
3. **brainstorm.md step 1 instructs anchoring (R1).** `read it first and keep its wording as the anchor` turns the requester's framing into a fixed point for the whole discovery. The intent-coverage table (I0) is good; the no-questioning clause should go, or be replaced with 'map coverage, and record where discovery found the intent's premise wrong'.
4. **Deletion: per-file boilerplate ≈10 KB (A/D).** `<role>` duplicates the description in all 19 files (≈2.6 KB); `<tools>` lists Read/Grep/Glob/Write (≈3.4 KB, A); `<bounds>` restates the flow (≈5 KB, D); usage-example tables add nothing beyond `<flags>`. Keep `<bounds>` only where it carries a policy (build.md 'never installs dependencies').
5. **Deletion: insight.md Auto-produce/Auto-harvest ≈1.3 KB (D leak).** Hook fingerprinting, sidechain skipping and the harvest ledger are maintainer internals; the command executor only needs the file paths and the CLI.
6. **Deletion: triplicated self-review gate in brainstorm.md.** flow 6, `<self_review>`, gotcha `skip-review` and `<bounds>` state the same rule four times (≈1 KB redundant). Keep `<self_review>` (it has the rationale) and the flow line.
7. **Exhortations posing as remedies (D, not B).** analyze/brainstorm `evidence-fabrication` ('Evidence must precede proposals'), estimate `scope-assumptions`, design/improve `[R18 Necessity Test]`, implement `verify simplest viable approach`. They name the right ordering but install no gate, slot or isolation; a bare model reads them as 'be careful'. Either convert to an output slot (e.g. 'Evidence:' line required before each 'Recommendation:') or delete.
8. **Document anchors with no pre-step (A2): design.md and business-panel.md.** design reads `--from`/01-discovery and starts designing; business-panel applies expert frameworks to the supplied doc's premise. Neither has a 'what does this document assume, and is it so?' step before Analyze. implement.md loads the plan the same way.
9. **Delegate-result isolation exists once and is not reused.** agent.md `Judge the returned summary against the check written before dispatch` is the best mechanism in scope (criterion before result). implement/design/cleanup `workflow-fanout` gotchas only say 'main loop writes' — they should inherit the same pre-dispatch check rather than pointing to RULES_DELEGATION.md.
10. **Working B that deserves to be kept and generalised (R3): brainstorm `decision_modes`.** `bare "yes", "proceed", "looks good", or silent accept of ★` → delegated → mandatory audit is the only text in scope that names starred-default acceptance and acts on it. estimate `relative-size` (refuses the hours/days unit) and improve `performance needs a measured baseline first, else stop` are the other two genuine gates; all three are command-local and could be lifted to a shared rule.

## 6. Not read

- `~/.claude/`, repo `.claude/`, `docs/` (other than writing this report), `CHANGELOG.md`, `README.md`, `src/superclaude/commands/README.md`, all other commands (intent, load, plan, pm, promote-feature, recommend, reflect, research, review, roadmap, save, sc, select-tool, spec-panel, task, test, troubleshoot), `core/`, `agents/`, `modes/`, `mcp/`, `scripts/context_loader.py` (not needed: ARCHITECTURE.md answered the delivery question), tests, evals. No web search.
- Cross-references cited by the files (RULES_DOCS.md, RULES_DELEGATION.md, RULES_QUALITY.md R01–R21, R02/R14/R18, FLAGS.md, BUSINESS_SYMBOLS.md, business-panel-experts.md) were NOT opened; rows that lean on them are classified on the pointer alone.
