<component name="rules-delegation" type="core-module">
  <role>
    <mission>Sub-agent delegation + agent routing rule detail — on-demand module of core/RULES.md kernel</mission>
    <loading>Injected by context_loader on delegation contexts (--delegate, sub-agent work, orchestration commands); Read explicitly before spawning agents outside those triggers</loading>
  </role>

  <intent_propagation>
When delegate sub-agent, include user request verbatim — sub-agent no re-interpret intent
  </intent_propagation>

  <sub_agent_decision>
  Axis: this section governs the single-delegate primitive (one Agent-tool subagent — whether/with-what-intent to spawn). Authoring a multi-subagent Workflow (`parallel`/`pipeline` fan-out) is the orthogonal harness EXECUTION layer: SC decides whether to fan out, the Workflow tool executes it. Both axes apply together; neither overrides the other.
  Direct work: single file edit, <3 steps, sequential dep, simple search, context already loaded
  Sub-agent: 3+ independent parallel streams, different expertise domains, >20K tokens exploration, isolated failure OK
  Never sub-agent: task need recent convo context, sequential A→B, doable <30s direct
  Model note: recent Opus models may not auto-spawn subagents even when Sub-agent criteria met — prefer explicit invocation (direct Agent tool call or `--delegate auto`) not assume auto-spawn. Opus 4.8 improved tool triggering vs 4.7; subagent-spawn eagerness under 4.8 not yet measured, threshold numbers unchanged pending eval.
  Worktree-parallel: when user wait on long in-progress iteration (spec authoring, deep research, multi-phase plan), propose worktree-isolated agent (EnterWorktree) for independent side-work — e.g., review project own framework/config, draft follow-up tickets. Split file-edit surfaces so two streams no conflict on merge. Decline split when side-work need current convo state or main iteration finish <5 minutes.
  Delegate packet (IN): prompt must carry user_request_verbatim, allowed_scope, forbidden_changes, files_or_areas_of_interest, required_evidence_format, stop_condition, active_mode_directives (copy operative directives of any active mode into the prompt — sub-agents never receive context_loader/UserPromptSubmit injections, so mode context that must govern the sub-agent travels only if copied; omit when no mode active). Sub-agent summary (OUT) advisory — revalidate cited file:line before act (re-grep / re-read the specific lines to confirm the summary's claims before editing or reporting). Via a Workflow `agent(prompt, opts)` the seven fields pack into the one free-form prompt argument (many-to-one); allowed_scope/forbidden_changes have no `opts` counterpart and stay prose discipline. `opts.schema`/StructuredOutput hardens return shape only — a well-typed citation can be fabricated, so the cited-file:line re-grep stays mandatory; cached/replayed results (Workflow resume-from-cache) may cite stale state and MUST be re-validated against current repo before act (R15 gates resume).
  Workflow fan-out (OUT): every `parallel()` under SC governance must `log()` dropped/null thunks before `filter(Boolean)` — silent filtering makes the main loop synthesize from a silently-incomplete set, an R15 'claimed done on partial evidence' risk.
  <examples>
  | Task | Decision | Why |
  |---|---|---|
  | "Find where UserAuth is defined" | Direct grep | Single search, instant |
  | "Audit security + performance + a11y" | 3 sub-agents | Independent domains, parallel |
  | "Read this file then edit line 42" | Direct | Sequential dependency |
  | "Research React 19 + Vue 4 + Svelte 5" | 3 sub-agents | Independent, context-isolating |
  | "Run tests and check results" | Direct | Fast, needs main context |
  | "Refactor 2 functions in one file" | Direct | Small scope, even though parallel-capable |
  | Waiting 10min on doc generation, want own harness reviewed | Worktree-isolated agent | Two file surfaces, no merge conflict |
  </examples>
  </sub_agent_decision>

  <agent_routing note="Single-trigger only — compound requests route via <sub_agent_decision>">
  When agent overlap on a single verb, prefer agent whose description matches explicit evidence in request (cited metric, named library, stated scope). When unresolved, state options + 1-line rationale and pick.
  Research SC-norm: repo-before-web — try Grep/Serena before delegating to deep-researcher; deep-researcher only for external knowledge not in repo.
  </agent_routing>
</component>
