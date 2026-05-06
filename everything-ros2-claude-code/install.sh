#!/usr/bin/env bash
# install.sh — everything-ros2-claude-code installer
# Usage:
#   ./install.sh                    # install all (agents + commands + rules + hooks)
#   ./install.sh --target cursor    # install for Cursor IDE
#   ./install.sh --agents-only      # install only agents
#   ./install.sh --dry-run          # preview without writing

set -euo pipefail

# ── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${BLUE}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*"; exit 1; }

# ── Defaults ─────────────────────────────────────────────────────────────────
TARGET="claude"          # claude | cursor | codex
DRY_RUN=false
AGENTS_ONLY=false
SKIP_HOOKS=false
CLAUDE_DIR="${HOME}/.claude"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Parse arguments ───────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case $1 in
    --target)     TARGET="$2";     shift 2 ;;
    --dry-run)    DRY_RUN=true;   shift   ;;
    --agents-only) AGENTS_ONLY=true; shift ;;
    --skip-hooks) SKIP_HOOKS=true; shift  ;;
    -h|--help)
      echo "Usage: ./install.sh [--target claude|cursor|codex] [--dry-run] [--agents-only]"
      exit 0 ;;
    *) warn "Unknown argument: $1"; shift ;;
  esac
done

# ── Helper ────────────────────────────────────────────────────────────────────
do_copy() {
  local src="$1" dst="$2"
  if [[ "$DRY_RUN" == true ]]; then
    echo "  [DRY-RUN] cp $src → $dst"
    return
  fi
  mkdir -p "$(dirname "$dst")"
  cp -r "$src" "$dst"
}

do_mkdir() {
  if [[ "$DRY_RUN" == true ]]; then
    echo "  [DRY-RUN] mkdir -p $1"
    return
  fi
  mkdir -p "$1"
}

# ── Banner ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║   everything-ros2-claude-code  Installer              ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════╝${RESET}"
echo ""
info "Target: ${TARGET}"
info "Source: ${SCRIPT_DIR}"
[[ "$DRY_RUN" == true ]] && warn "DRY RUN — no files will be written"
echo ""

# ── Target-specific paths ─────────────────────────────────────────────────────
case "$TARGET" in
  claude)
    AGENTS_DIR="${CLAUDE_DIR}/agents"
    COMMANDS_DIR="${CLAUDE_DIR}/commands"
    RULES_DIR="${CLAUDE_DIR}/rules"
    SKILLS_DIR="${CLAUDE_DIR}/skills"
    HOOKS_FILE="${CLAUDE_DIR}/hooks.json"
    ;;
  cursor)
    AGENTS_DIR="${PWD}/.cursor/agents"
    COMMANDS_DIR="${PWD}/.cursor/commands"
    RULES_DIR="${PWD}/.cursor/rules"
    SKILLS_DIR="${PWD}/.cursor/skills"
    HOOKS_FILE="${PWD}/.cursor/hooks.json"
    ;;
  codex)
    AGENTS_DIR="${PWD}/.codex/agents"
    COMMANDS_DIR="${PWD}/.codex/commands"
    RULES_DIR="${PWD}/.codex/rules"
    SKILLS_DIR="${PWD}/.codex/skills"
    HOOKS_FILE="${PWD}/.codex/hooks.json"
    ;;
  *)
    error "Unknown target '$TARGET'. Use: claude | cursor | codex"
    ;;
esac

# ── Install Agents ────────────────────────────────────────────────────────────
echo -e "${BOLD}Installing Agents (${AGENTS_DIR})...${RESET}"
do_mkdir "$AGENTS_DIR"

for agent in "${SCRIPT_DIR}/agents/"*.md; do
  name=$(basename "$agent")
  do_copy "$agent" "${AGENTS_DIR}/${name}"
  success "Agent: ${name}"
done

if [[ "$AGENTS_ONLY" == true ]]; then
  echo ""
  success "Agents installed (--agents-only mode). Done!"
  exit 0
fi

# ── Install Commands ───────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}Installing Commands (${COMMANDS_DIR})...${RESET}"
do_mkdir "$COMMANDS_DIR"

for cmd in "${SCRIPT_DIR}/commands/"*.md; do
  name=$(basename "$cmd")
  do_copy "$cmd" "${COMMANDS_DIR}/${name}"
  success "Command: /${name%.md}"
done

# ── Install Rules ─────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}Installing Rules (${RULES_DIR})...${RESET}"
do_mkdir "$RULES_DIR"

# Common rules (always install)
for rule in "${SCRIPT_DIR}/rules/common/"*.md; do
  name=$(basename "$rule")
  do_copy "$rule" "${RULES_DIR}/${name}"
  success "Rule (common): ${name}"
done

# Language-specific rules — install both by default
for lang in cpp python; do
  for rule in "${SCRIPT_DIR}/rules/${lang}/"*.md; do
    [[ -f "$rule" ]] || continue
    name=$(basename "$rule")
    do_copy "$rule" "${RULES_DIR}/${name}"
    success "Rule (${lang}): ${name}"
  done
done

# ── Install Skills ────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}Installing Skills (${SKILLS_DIR})...${RESET}"
do_mkdir "$SKILLS_DIR"

for skill_dir in "${SCRIPT_DIR}/skills/"*/; do
  skill_name=$(basename "$skill_dir")
  skill_file="${skill_dir}SKILL.md"
  if [[ -f "$skill_file" ]]; then
    do_mkdir "${SKILLS_DIR}/${skill_name}"
    do_copy "$skill_file" "${SKILLS_DIR}/${skill_name}/SKILL.md"
    success "Skill: ${skill_name}"
  fi
done

# ── Install Hooks ─────────────────────────────────────────────────────────────
if [[ "$SKIP_HOOKS" == false ]]; then
  echo ""
  echo -e "${BOLD}Installing Hooks...${RESET}"

  if [[ "$TARGET" == "claude" ]]; then
    # Merge hooks into existing hooks.json if it exists
    src_hooks="${SCRIPT_DIR}/hooks/hooks.json"
    if [[ -f "${CLAUDE_DIR}/hooks.json" ]]; then
      warn "~/.claude/hooks.json already exists — merging not yet automated."
      warn "Manually merge ${src_hooks} into ${CLAUDE_DIR}/hooks.json"
    else
      do_copy "$src_hooks" "${CLAUDE_DIR}/hooks.json"
      success "Hooks installed: ~/.claude/hooks.json"
    fi

    # Install hook scripts
    do_mkdir "${CLAUDE_DIR}/scripts/ros2-hooks"
    for script in "${SCRIPT_DIR}/scripts/hooks/"*.js; do
      [[ -f "$script" ]] || continue
      name=$(basename "$script")
      do_copy "$script" "${CLAUDE_DIR}/scripts/ros2-hooks/${name}"
      success "Hook script: ${name}"
    done
  fi
fi

# ── Copy AGENTS.md to project root (for Codex/Cursor cross-tool support) ──────
if [[ "$TARGET" != "claude" ]]; then
  echo ""
  echo -e "${BOLD}Copying AGENTS.md to project root...${RESET}"
  do_copy "${SCRIPT_DIR}/AGENTS.md" "${PWD}/AGENTS.md"
  success "AGENTS.md → project root"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}${BOLD}║   Installation complete!                              ║${RESET}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "Agents installed:   $(ls "${SCRIPT_DIR}/agents/"*.md 2>/dev/null | wc -l | tr -d ' ')"
echo -e "Commands installed: $(ls "${SCRIPT_DIR}/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')"
echo -e "Skills installed:   $(find "${SCRIPT_DIR}/skills" -name 'SKILL.md' 2>/dev/null | wc -l | tr -d ' ')"
echo ""
echo -e "Next steps:"
echo -e "  1. Copy CLAUDE.md to your ROS 2 workspace root"
echo -e "  2. Set ROS_DISTRO in CLAUDE.md to your target distro"
echo -e "  3. Try: ${BOLD}/ros2-validate${RESET} in Claude Code"
echo -e "  4. Try: ${BOLD}/ros2-new-pkg my_robot_pkg --type cpp --distro humble${RESET}"
echo ""
