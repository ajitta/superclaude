# SuperClaude Framework - Comprehensive Feature List

Complete inventory of all features restored in v4.1.9+

## 📋 Commands (30)

All slash commands are documented in [commands-list.md](commands-list.md)

## 🤖 Agents (20)

### Specialized Experts
1. **backend-architect** - Backend system design
2. **business-panel-experts** - Multi-expert business analysis  
3. **deep-research-agent** - Autonomous web research
4. **devops-architect** - Infrastructure and deployment
5. **frontend-architect** - UI/UX and frontend patterns
6. **learning-guide** - Educational mentorship
7. **performance-engineer** - Performance optimization
8. **pm-agent** - Project management and coordination
9. **python-expert** - Python best practices
10. **quality-engineer** - Quality assurance and testing
11. **refactoring-expert** - Code refactoring
12. **requirements-analyst** - Requirements gathering
13. **root-cause-analyst** - Problem root cause analysis
14. **security-engineer** - Security analysis and hardening
15. **socratic-mentor** - Socratic method mentorship
16. **system-architect** - System architecture design
17. **technical-writer** - Technical documentation
18. **deep-research** (in src) - Research capability
19. **repo-index** (in src) - Repository indexing
20. **self-review** (in src) - Code review

## 🎨 Behavioral Modes (8)

1. **Brainstorming** - Multi-perspective ideation
2. **Business Panel** - Executive-level strategic analysis
3. **Deep Research** - Autonomous research with iteration
4. **Introspection** - Meta-cognitive analysis
5. **Orchestration** - Efficient tool coordination
6. **Task Management** - Systematic organization
7. **Token Efficiency** - 30-50% context savings
8. **Unified** - Combined reference mode (default)

## 🔌 MCP Server Integration (10)

### CLI Installation

SuperClaude provides a convenient CLI command for MCP server installation:

```bash
# List available MCP servers
superclaude mcp --list

# Interactive installation
superclaude mcp

# Install specific servers
superclaude mcp --servers tavily --servers context7

# Install with specific scope
superclaude mcp --servers tavily --scope project

# Dry run to see what would be installed
superclaude mcp --dry-run
```

### Available Servers
1. **sequential-thinking** - Multi-step problem solving and systematic analysis
2. **context7** - Official library documentation and code examples
3. **playwright** - Cross-browser E2E testing and automation
4. **serena** - Semantic code analysis and intelligent editing
6. **filesystem-with-morph** - Pattern-based bulk code transformations with filesystem access (requires API key)
7. **tavily** - Web search and real-time information retrieval (requires API key)
8. **chrome-devtools** - Chrome DevTools debugging and performance analysis

### Documentation Files
1. **MCP_Tavily.md** - Primary web search
2. **MCP_Serena.md** - Session persistence & memory
3. **MCP_Sequential.md** - Token-efficient reasoning
4. **MCP_Context7.md** - Official documentation lookup
5. **MCP_Playwright.md** - Browser automation
6. **MCP_Morphllm.md** - Model transformation
7. **MCP_Chrome-DevTools.md** - Performance analysis

### Configuration Files
- context7.json
- morphllm.json
- playwright.json
- sequential.json
- serena-docker.json
- serena.json
- tavily.json

## 📚 Core Documentation

### Principles & Rules
- **PRINCIPLES.md** - Framework design principles
- **RULES.md** - Operational rules
- **FLAGS.md** - Command flags and options
- **RESEARCH_CONFIG.md** - Deep research configuration
- **BUSINESS_PANEL_EXAMPLES.md** - Business panel examples
- **BUSINESS_SYMBOLS.md** - Symbol language for business

## 📖 Documentation Structure (152 files)

### User Guides
- **User-Guide/** - English documentation
- **User-Guide-jp/** - Japanese (日本語)
- **User-Guide-kr/** - Korean (한국어)
- **User-Guide-zh/** - Chinese (中文)

Each includes:
- agents.md - Agent usage guide
- commands.md - Command reference
- flags.md - Flag documentation
- mcp-servers.md - MCP server guide
- modes.md - Behavioral modes
- session-management.md - Session handling

### Developer Guides  
- **Developer-Guide/** - Contributing and architecture
- **Development/** - Development workflows and tasks
- **Reference/** - Advanced patterns and examples

### Getting Started
- **Getting-Started/** - Installation and quick start

## 🎯 Package Distribution

All resources are included in both:
- `plugins/superclaude/` - Source repository structure
- `src/superclaude/` - Installed package structure

### Directory Structure
```
src/superclaude/
├── agents/          # 20 agent definitions
├── commands/        # 30 slash commands  
├── modes/           # 8 behavioral modes
├── mcp/            # 10 MCP integrations + configs
├── core/           # 7 core documentation files
├── examples/       # Workflow examples
├── hooks/          # Hook configurations
├── scripts/        # Utility scripts
├── skills/         # Pytest integration skills
├── cli/            # CLI tools
├── execution/      # Parallel execution engine
└── pm_agent/       # PM Agent core
```

## 🚀 Installation

```bash
# Install SuperClaude
pipx install superclaude

# Install all 30 commands
superclaude install

# List all features
superclaude install --list
```

## 📊 Statistics Summary

| Feature | Count | Location |
|---------|-------|----------|
| **Commands** | 30 | commands/ |
| **Agents** | 20 | agents/ |
| **Modes** | 8 | modes/ |
| **MCP Servers** | 10 | mcp/ |
| **Core Docs** | 7 | core/ |
| **User Docs** | 152 | docs/ |

**Total Resource Files**: 200+

## 🔗 Related Documentation

- [Commands List](commands-list.md) - All 30 commands
- [MCP Server Guide](../User-Guide/mcp-servers.md) - MCP integration
- [Agents Guide](../User-Guide/agents.md) - Agent usage
- [Quick Start](../Getting-Started/quick-start.md) - Getting started
