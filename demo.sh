#!/usr/bin/env bash
# Run a live demo of claude-project-cleaner
# Creates a temp sandbox and runs the full pipeline

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

SBOX="/tmp/claude-cleaner-demo-$$"
FHOME="/tmp/claude-cleaner-fakehome-$$"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)/scripts"

cleanup_demo() { rm -rf "$SBOX" "$FHOME"; }
trap cleanup_demo EXIT

echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║   🧹 Claude Project Cleaner — Live Demo      ║${NC}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════╝${NC}"
echo ""

# Build sandbox
echo -e "${YELLOW}📦 Setting up demo environment...${NC}"
mkdir -p "$SBOX/.claude"/{skills,plugins,cache,commands,hooks,memory}
mkdir -p "$SBOX/node_modules"
echo '{}' > "$SBOX/.claude/settings.json"
echo "# My Project" > "$SBOX/CLAUDE.md"
echo "source code" > "$SBOX/src.py"

mkdir -p "$FHOME/skills"/{gstack,frintend-design,java-springboot}
mkdir -p "$FHOME/plugins"/{playwright-chromium-120,playwright-chromium-115}
mkdir -p "$FHOME/cache/sessions"
echo "old" > "$FHOME/cache/sessions/session-1.json"
echo "old" > "$FHOME/cache/sessions/session-2.json"
sleep 0.5
echo -e "${GREEN}   ✓ Sandbox ready (simulating 2-week project)${NC}"
echo ""

# Step 1: Scanner
echo -e "${BOLD}${CYAN}🔍 Step 1: Scanning 12 Claude Code locations...${NC}"
sleep 1
PYTHONIOENCODING=utf-8 python "$SCRIPT_DIR/scanner.py" "$SBOX" --claude-home "$FHOME" 2>&1 | sed 's/^/   /'
echo ""

# Step 2: Organizer
echo -e "${BOLD}${CYAN}🧠 Step 2: Classifying into 6 categories...${NC}"
sleep 1
PYTHONIOENCODING=utf-8 python "$SCRIPT_DIR/organizer.py" "$SBOX/.claude/scan_result.json" 2>&1 | sed 's/^/   /'
echo ""

# Step 3: Cleaner dry-run
echo -e "${BOLD}${CYAN}🧹 Step 3: Dry-run preview...${NC}"
sleep 1
PYTHONIOENCODING=utf-8 python "$SCRIPT_DIR/cleaner.py" "$SBOX/.claude/classified.json" 2>&1 | sed 's/^/   /'
echo ""

# Show report excerpt
echo -e "${BOLD}${CYAN}📋 Cleanup Report:${NC}"
echo -e "${BOLD}────────────────────────────────────────────────${NC}"
head -35 "$SBOX/.claude/CLAUDE-CLEANUP-REPORT.md" 2>/dev/null | sed 's/^/   /'
echo -e "   ..."
echo ""

# Summary
TOTAL=$(python -c "import json; d=json.load(open('$SBOX/.claude/classified.json')); print(d['total_items'])")
echo -e "${BOLD}${GREEN}✅ Demo complete!${NC}"
echo -e "   ${TOTAL} items scanned → classified → ready for cleanup"
echo ""
echo -e "${YELLOW}💡 Real usage:${NC}"
echo -e "   ${BOLD}cd scripts/ && python scanner.py && python organizer.py && python cleaner.py --auto${NC}"
