---
name: recommend
type: command
triggers: [/sc:recommend, command-recommendation, suggest-command, help-choose]
description: "Ultra-intelligent command recommendation engine - recommends the most suitable SuperClaude commands for any user input"
category: utility
complexity: standard
mcp-servers: []
personas: []
---

<document type="command" name="recommend"
          triggers="/sc:recommend, command-recommendation, suggest-command, help-choose">

# SuperClaude Intelligent Command Recommender

**Purpose**: Recommend optimal SuperClaude commands based on user input analysis.

## Command Definition

```bash
/sc:recommend [user request] [--estimate] [--alternatives] [--stream]
```

## Options

| Flag | Description |
|------|-------------|
| `--estimate` | Include time/budget estimation |
| `--alternatives` | Show multiple solution approaches |
| `--stream` | Enable continuous project tracking |
| `--expertise [level]` | Set beginner/intermediate/expert |

## Keyword-to-Command Mapping

```yaml
categories:
  ml_category:
    keywords: [machine learning, ml, ai, model, algorithm]
    commands: ["/sc:analyze --seq --c7", "/sc:design --seq --ultrathink"]
    personas: ["--persona-analyzer", "--persona-architect"]

  web_category:
    keywords: [website, frontend, ui, react, vue, component]
    commands: ["/sc:build --feature --magic", "/sc:test --e2e --pup"]
    personas: ["--persona-frontend", "--persona-qa"]

  api_category:
    keywords: [api, backend, server, microservice, endpoint]
    commands: ["/sc:design --api --ddd --seq", "/sc:build --feature --tdd"]
    personas: ["--persona-backend", "--persona-security"]

  debug_category:
    keywords: [error, bug, issue, not working, broken]
    commands: ["/sc:troubleshoot --investigate --seq", "/sc:analyze --code"]
    personas: ["--persona-analyzer"]

  performance_category:
    keywords: [slow, performance, optimization, speed]
    commands: ["/sc:analyze --performance --pup --profile", "/sc:improve --performance"]
    personas: ["--persona-performance"]

  security_category:
    keywords: [security, auth, vulnerability, owasp]
    commands: ["/sc:scan --security --owasp --deps", "/sc:analyze --security"]
    personas: ["--persona-security"]

  test_category:
    keywords: [test, qa, coverage, validation, e2e]
    commands: ["/sc:test --coverage --e2e --pup", "/sc:scan --validate"]
    personas: ["--persona-qa"]

  learning_category:
    keywords: [how, learn, explain, tutorial, understand]
    commands: ["/sc:document --user --examples", "/sc:brainstorm --interactive"]
    personas: ["--persona-mentor"]
```

## Project Context Detection

```yaml
project_detection:
  react_project:
    indicators: [package.json with react, src/App.jsx]
    auto_flags: ["--magic", "--c7", "--pup"]

  node_api_project:
    indicators: [express, server.js, routes/]
    auto_flags: ["--seq", "--c7"]

  python_project:
    indicators: [requirements.txt, setup.py, main.py]
    auto_flags: ["--seq"]

expertise_levels:
  beginner: "--tutorial --examples --step-by-step"
  intermediate: "--guided --examples"
  expert: "--advanced --no-explanations"
```

## Examples

### Example 1: Beginner ML Project
```bash
User: /sc:recommend "I'm new, I want to do machine learning"

🎯 Analysis: ML project - Beginner level
🎭 Persona: --persona-mentor + --persona-analyzer

✅ Recommended Flow:
1. /sc:analyze --seq --c7 --persona-mentor
2. /sc:design --seq --ultrathink --persona-architect
3. /sc:build --feature --tdd
4. /sc:test --coverage --e2e --pup

🔧 MCP: --c7 --seq
```

### Example 2: Web Performance Issue
```bash
User: /sc:recommend "my site is very slow"

🎯 Analysis: Performance optimization - Urgent
🎭 Persona: --persona-performance + --persona-analyzer

✅ Recommended Flow:
1. /sc:analyze --performance --pup --profile
2. /sc:troubleshoot --investigate --seq
3. /sc:improve --performance --iterate
4. /sc:test --coverage --benchmark

🔧 MCP: --pup --seq
💡 Flags: --monitoring --benchmark --profile
```

### Example 3: E-commerce Project (with --estimate)
```bash
User: /sc:recommend "building e-commerce site" --estimate

🎯 Analysis: E-commerce - Multi-domain
🎭 Persona: --persona-architect + --persona-frontend + --persona-security

✅ Recommended Flow:
1. /sc:design --api --ddd --seq --ultrathink
2. /sc:build --feature --magic --nextjs
3. /sc:build --feature --tdd (payment/security)
4. /sc:scan --security --owasp

⏱️ Estimate:
- Planning: 1-2 weeks
- Frontend: 2-4 weeks
- Backend/Payment: 2-3 weeks
- Testing: 1-2 weeks
- Total: 6-12 weeks
```

## Response Format

```yaml
standard_response:
  header:
    - 🎯 Project analysis
    - 🎭 Persona recommendation

  recommendations:
    - ✅ Main commands (3-4)
    - 🔧 MCP servers
    - 💡 Smart flags

  enhanced (with flags):
    - ⏱️ Time estimate (--estimate)
    - 🔧 Alternatives (--alternatives)
```

## Quick Reference

```bash
# Basic recommendation
/sc:recommend "I want to build X"

# With estimation
/sc:recommend "new feature" --estimate

# Multiple options
/sc:recommend "blog site" --alternatives

# Continuous tracking
/sc:recommend --stream "tracking my project"

# For beginners
/sc:recommend "learn React" --expertise beginner
```

</document>
