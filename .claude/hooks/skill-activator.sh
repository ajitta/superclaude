#!/bin/bash
# Skill Activator Hook
# Evaluates user prompt against skill triggers for reliable activation
# Cost: ~$0.0004/prompt using Haiku 4.5

# Read prompt from stdin (passed by Claude Code)
PROMPT=$(cat)

# Skills directory
SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

# Output skill activation hints if prompt matches known patterns
check_skill_triggers() {
    local prompt="$1"

    # Confidence check triggers
    if echo "$prompt" | grep -qiE "(implement|build|create|add feature|before starting)"; then
        echo "INSTRUCTION: Consider using /confidence-check skill before implementation"
    fi

    # Research triggers
    if echo "$prompt" | grep -qiE "(research|investigate|find out|what is|how does|latest|current)"; then
        echo "INSTRUCTION: Consider using /sc:research skill for web research"
    fi

    # Business panel triggers
    if echo "$prompt" | grep -qiE "(business|strategy|market|competitive|porter|christensen)"; then
        echo "INSTRUCTION: Consider using /sc:business-panel skill for expert analysis"
    fi
}

# Execute check
check_skill_triggers "$PROMPT"

exit 0
