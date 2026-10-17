# 03e — Phase 2 content value classification: commands (first half)

> Split by size into 3 files (part 1 of 3): [part 2](./03e-analysis-commands-first-2.md) · [part 3](./03e-analysis-commands-first-3.md). Section boundaries and content unchanged.

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
