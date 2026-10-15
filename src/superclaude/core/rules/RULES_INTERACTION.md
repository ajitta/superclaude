<component name="rules-interaction" type="core-module">
  <role>
    <mission>Structured choice presentation for commands — on-demand module of core/RULES.md kernel</mission>
    <loading>Injected by context_loader on /sc: command invocations</loading>
  </role>

  <selection_protocol note="Text menus for /sc: commands">
When: only when a command step waits on the user's choice, or an irreversible, >3-file, or security/data step needs confirmation. A response with nothing waiting on the user ends without a menu. When the command names AskUserQuestion for the step, use that tool instead of a text menu.
Labels: [1]–[7] (max 7), sub-options [1a] [1b], [y/n] for yes/no. A command that defines its own labels (e.g. [a]/[b]/[c] in /sc:brainstorm, /sc:init) keeps them.
Format: "#### [N] Label" with a short sub-list; mark the recommended option with ★.
Close: "select: N" ("select: N,N" for multi-select, "[y/n]" for yes/no) plus "or type your own". Accept numbers, letters, comma lists, y/n, and free text.
Depth: top-level options first, drill down next turn; list ≤3 sub-options inline.
  </selection_protocol>
</component>
