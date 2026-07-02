<component name="rules-interaction" type="core-module">
  <role>
    <mission>Structured choice presentation for commands — on-demand module of core/RULES.md kernel</mission>
    <loading>Injected by context_loader on /sc: command invocations</loading>
  </role>

  <selection_protocol note="Structured choice presentation — all commands">
Identify: [N] flat, [Na] hierarchical, [y/n] binary — max 7 options
Format: "#### [N] Label" with sub-list; mark ★ for recommended option
Guide: end with "select: N" / "select: N,N" / "[y/n]" + "or type your own"
Accept: bare numbers, comma lists, y/n, free text — all valid
Depth: parent first → drill down next turn; ≤3 sub-options → inline [Na] [Nb] [Nc]
  </selection_protocol>
</component>
