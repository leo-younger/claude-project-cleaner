#!/usr/bin/env bash
# Claude Project Cleaner — One-click install
# Usage: bash install.sh [--global] [--project <path>]

set -e

SKILL_NAME="claude-project-cleaner"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_TARGET=""

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --global)
            INSTALL_TARGET="$HOME/.claude/skills/$SKILL_NAME"
            shift
            ;;
        --project)
            INSTALL_TARGET="$2/.claude/skills/$SKILL_NAME"
            shift 2
            ;;
        *)
            echo "Usage: bash install.sh [--global] [--project <path>]"
            echo "  --global       Install to ~/.claude/skills/ (available in all projects)"
            echo "  --project <p>  Install to <project>/.claude/skills/ (project only)"
            exit 1
            ;;
    esac
done

# Default: install to current project if .claude exists, else global
if [ -z "$INSTALL_TARGET" ]; then
    if [ -d "$PWD/.claude" ]; then
        INSTALL_TARGET="$PWD/.claude/skills/$SKILL_NAME"
    else
        INSTALL_TARGET="$HOME/.claude/skills/$SKILL_NAME"
    fi
fi

echo "📦 Installing $SKILL_NAME to: $INSTALL_TARGET"

# Remove old install if exists
if [ -d "$INSTALL_TARGET" ] || [ -L "$INSTALL_TARGET" ]; then
    rm -rf "$INSTALL_TARGET"
fi

# Copy skill files
mkdir -p "$(dirname "$INSTALL_TARGET")"
cp -r "$SCRIPT_DIR" "$INSTALL_TARGET"

# Remove .git if copied
rm -rf "$INSTALL_TARGET/.git" 2>/dev/null || true

echo "✅ Installed! Trigger Claude Code with: /cleanup"
echo "   Or run manually: cd $INSTALL_TARGET/scripts && python scanner.py"
