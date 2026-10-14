#!/usr/bin/env bash
#
# superclaude Legacy Cleanup Script
# Removes old superclaude-related files from ~/.claude
#

set -euo pipefail

CLAUDE_DIR="$HOME/.claude"
BACKUP_DIR="$HOME/.claude-superclaude-backup-$(date +%Y%m%d_%H%M%S)"

echo "🧹 superclaude Legacy Cleanup"
echo "=============================="
echo ""

# Check if .claude directory exists
if [[ ! -d "$CLAUDE_DIR" ]]; then
    echo "✅ No .claude directory found - nothing to clean"
    exit 0
fi

# List of superclaude-related files/directories to remove
SUPERCLAUDE_ITEMS=(
    # superclaude plugin (if exists)
    "plugins/superclaude@superclaude"

    # Legacy superclaude configs (if any)
    "superclaude.json"
    "superclaude_config.json"
)

# Function to backup and remove
backup_and_remove() {
    local item="$1"
    local full_path="$CLAUDE_DIR/$item"

    if [[ -e "$full_path" ]] || [[ -L "$full_path" ]]; then
        echo "📦 Backing up: $item"
        mkdir -p "$BACKUP_DIR/$(dirname "$item")"
        cp -R "$full_path" "$BACKUP_DIR/$item" 2>/dev/null || true

        echo "🗑️  Removing: $item"
        rm -rf "$full_path"
        return 0
    fi
    return 1
}

echo "🔍 Scanning for superclaude files..."
echo ""

FOUND_COUNT=0
for item in "${SUPERCLAUDE_ITEMS[@]}"; do
    if backup_and_remove "$item"; then
        ((FOUND_COUNT++))
    fi
done

# Clean up settings.json if it contains superclaude plugin reference
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
if [[ -f "$SETTINGS_FILE" ]]; then
    if grep -q "superclaude@superclaude" "$SETTINGS_FILE" 2>/dev/null; then
        echo "📦 Backing up: settings.json"
        mkdir -p "$BACKUP_DIR"
        cp "$SETTINGS_FILE" "$BACKUP_DIR/settings.json"

        echo "🧹 Removing superclaude plugin from settings.json"
        # Use Python to properly manipulate JSON
        python3 - <<'PYEOF' "$SETTINGS_FILE"
import json
import sys

settings_file = sys.argv[1]

try:
    with open(settings_file, 'r') as f:
        settings = json.load(f)

    # Remove superclaude plugin
    if 'enabledPlugins' in settings:
        if 'superclaude@superclaude' in settings['enabledPlugins']:
            del settings['enabledPlugins']['superclaude@superclaude']
            print(f"   ✅ Removed superclaude@superclaude from enabledPlugins")

        # Remove enabledPlugins if empty
        if not settings['enabledPlugins']:
            del settings['enabledPlugins']

    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
        f.write('\n')

except Exception as e:
    print(f"   ⚠️  Failed to update settings.json: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF
        ((FOUND_COUNT++))
    fi
fi

echo ""
echo "=============================="

if [[ $FOUND_COUNT -eq 0 ]]; then
    echo "✅ No superclaude files found - already clean!"
    rmdir "$BACKUP_DIR" 2>/dev/null || true
else
    echo "🎉 Cleanup complete!"
    echo ""
    echo "📦 Backup saved to:"
    echo "   $BACKUP_DIR"
    echo ""
    echo "Removed $FOUND_COUNT superclaude-related item(s)"
fi

echo ""
echo "ℹ️  Note: Official Claude Code files were NOT touched"
echo "   (history.jsonl, mcp.json, projects/, etc.)"
