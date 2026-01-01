<component name="commands-readme" type="documentation">
  <config style="Telegraphic|Imperative|XML" eval="false"/>

  <overview>
    <purpose>Slash commands installed to ~/.claude/commands/sc/ when users run superclaude install</purpose>
    <location>src/superclaude/commands/</location>
  </overview>

  <available_commands>
- agent.md: Specialized AI agents
- index-repo.md: Repository indexing for context optimization
- recommend.md: Command recommendations
- research.md: Deep web research with parallel search
- sc.md: Show all available SuperClaude commands
  </available_commands>

  <sync_note>
    <source>plugins/superclaude/commands/</source>
    <target>src/superclaude/commands/</target>
    <workflow>
1) Edit files in plugins/superclaude/commands/
2) Copy changes to src/superclaude/commands/
3) Both locations must stay in sync
    </workflow>
    <future>v5.0 plugin system will use plugins/ directly</future>
  </sync_note>
</component>
