<component name="rules-delegation" type="core-module">
  <role>
    <mission>Sub-agent delegation + agent routing rule detail — on-demand module of core/RULES.md kernel</mission>
    <loading>Injected by context_loader on delegation contexts (--delegate, sub-agent work, orchestration commands); Read explicitly before spawning agents outside those triggers</loading>
  </role>

  <sub_agent_decision>
  Axis: this section governs the single-delegate primitive (one Agent-tool subagent — whether/with-what-intent to spawn). Authoring a multi-subagent Workflow (`parallel`/`pipeline` fan-out) is the orthogonal harness execution layer: SC decides whether to fan out, the Workflow tool executes it. Both axes apply together; neither overrides the other.
  - Direct work: single file edit, <3 steps, sequential dep, simple search, context already loaded
  - Sub-agent: 3+ independent parallel streams, different expertise domains, >20K tokens exploration, isolated failure OK
  - Never sub-agent: the task needs recent conversation context, the work is sequential (A→B), or it is doable directly in under 30s
  - Spawn discipline: work finishable in a handful of tool calls stays in the main loop. Never spawn a sub-agent unasked to verify or double-check work the main loop already did — added spawns need an independent stream, not extra assurance. One sub-agent when one can finish the task. Prefer explicit invocation (direct Agent tool call or `--delegate auto`) over relying on auto-spawn.
  - Model: omit the Agent tool's `model` parameter so the delegate falls through to its own frontmatter model, `CLAUDE_CODE_SUBAGENT_MODEL`, or the session model, in that order; pass a model only when the user asked for it for that work. Fable is the case that matters: it is priced above Opus 5.5, and headless runs can bill it to usage credits without a consent prompt.
  - Run-alongside: while a delegate runs, continue main-loop work that does not depend on its result (the Agent tool returns immediately and notifies on completion); never redo the delegated work in the main loop, and wait only when the next step needs the result. For follow-up work in the same stream, continue the existing delegate with SendMessage rather than spawning a fresh one — its context is intact and cached.
  - Worktree-parallel: when the user waits on a long in-progress iteration (spec authoring, deep research, multi-phase plan), propose a worktree-isolated agent (EnterWorktree) for independent side-work — e.g., reviewing the project's own framework/config or drafting follow-up tickets. Split file-edit surfaces so the streams cannot conflict on merge. Decline when the side-work needs current conversation state or the main iteration ends within 5 minutes.
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

  <delegate_packet>
  The prompt carries user_request_verbatim, allowed_scope, forbidden_changes, files_or_areas_of_interest and stop_condition, plus two fields with defined content:
  - required_evidence_format: by default files inspected, commands run, exact evidence, assumptions and residual risks.
  - active_mode_directives: the operative directives of any active mode, copied into the prompt — sub-agents never receive context_loader/UserPromptSubmit injections, so mode context that must govern the sub-agent travels only if copied. Omitted when no mode is active.
  Review and verification delegations: a persuasive rationale flips a reviewer's verdict even when it is wrong, and telling the reviewer to disregard it does not undo that.
  - Withheld: the author's rationale, self-assessment and any verdict on the artifact that come with it rather than in it (the author's message, a PR or commit description, the main loop's own notes, an earlier reviewer's approval), even inside the user's request.
  - Marker: user_request_verbatim keeps the user's words with each withheld passage replaced by a marker naming only its category, such as `[prior verdict withheld]`, never its content, so the edit shows.
  - Sent: the artifact and its acceptance criteria. Everything written in the artifact travels as part of it except its review history (a self-review or iteration log, a "resolved" or "review clean" note).
  - Earlier findings: every finding from an earlier review, including findings recorded in the artifact's review history (cut from the artifact copy), travels as an acceptance criterion — the defect and the check that proves it gone — with no claim that it is fixed, except a decided defect (next item). A finding rejected as not a defect travels the same way.
  - Decided defects: the exception to Earlier findings — a finding acknowledged as a defect but left unfixed by decision (fix declined, deferred, accepted as a known limit) travels as that decision instead, without its rationale.
  - Alternatives: when alternatives exist they go side by side in one prompt, not as a follow-up.
  - Limit: withholding controls the prompt only; a delegate that can read the repo can still reach withheld material in the artifact's file or its git history.
  </delegate_packet>

  <delegate_return>
  This block governs the summary a sub-agent returns.
  - Before dispatch: the main loop writes down the evidence shape it expects and the check that will judge it [R20], never a predicted verdict — a predicted verdict anchors the main loop and, copied into the prompt, hands the reviewer a prior verdict. A known ground truth such as a planted defect belongs to the check and stays out of the delegate's prompt.
  - On return: the main loop judges the summary against that check and the requested evidence format, not by how confident it reads, and revalidates every cited file:line (re-grep / re-read the specific lines) before editing or reporting.
  - Exploration and audit: the prompt requires the branch to return counterevidence and unknowns next to its conclusion — a summary carrying only what the branch found leaves the main loop unable to tell a complete set from an incomplete one, the same R15 risk as silently filtered fan-out results.
  </delegate_return>

  <workflow_delegation>
  Via a Workflow `agent(prompt, opts)` the seven delegate packet fields pack into the one free-form prompt argument (many-to-one).
  - Scope: allowed_scope/forbidden_changes have no `opts` counterpart and stay prose discipline.
  - Schema: `opts.schema`/StructuredOutput hardens return shape only — a well-typed citation can be fabricated, so the cited-file:line re-grep stays mandatory.
  - Cache: cached/replayed results (Workflow resume-from-cache) may cite stale state and must be re-validated against the current repo before acting (R15 gates resume).
  - Fan-out: every `parallel()` under SC governance must `log()` dropped/null thunks before `filter(Boolean)` — silent filtering makes the main loop synthesize from a silently-incomplete set, an R15 'claimed done on partial evidence' risk.
  - Write-Return: subprocess file writes are discarded — document- or code-producing fan-out returns its artifact and the main loop performs every Write/Edit; approval checkpoints (e.g. >3-unit change) fire in the main loop because subagents cannot pause for the user.
  </workflow_delegation>

  <agent_routing note="Single-trigger only — compound requests route via <sub_agent_decision>">
  When agents overlap on a single verb, prefer the agent whose description matches explicit evidence in the request (cited metric, named library, stated scope). When that leaves it unresolved, state the options with a 1-line rationale each and pick one.
  Research SC-norm: repo before web — try Grep/Serena before delegating to deep-researcher, which is only for external knowledge not in the repo.
  </agent_routing>
</component>
