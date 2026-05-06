#!/usr/bin/env bash
# install.sh — everything-ros2-claude-code installer
# Usage:
#   ./install.sh                       # install all for Claude Code
#   ./install.sh --target cursor       # install for Cursor IDE
#   ./install.sh --target copilot      # install for GitHub Copilot
#   ./install.sh --target windsurf     # install for Windsurf/Cascade
#   ./install.sh --target cline        # install for Cline
#   ./install.sh --target gemini       # install for Gemini Code Assist
#   ./install.sh --target codex        # install for OpenAI Codex
#   ./install.sh --target all          # install for ALL agents
#   ./install.sh --agents-only         # install only agents
#   ./install.sh --dry-run             # preview without writing

set -euo pipefail

# ── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${BLUE}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*"; exit 1; }

# ── Defaults ─────────────────────────────────────────────────────────────────
TARGET="claude"          # claude | cursor | codex | copilot | windsurf | cline | gemini | all
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
      echo "Usage: ./install.sh [--target claude|cursor|codex|copilot|windsurf|cline|gemini|all] [--dry-run] [--agents-only]"
      echo ""
      echo "Targets:"
      echo "  claude     Install for Claude Code (~/.claude/)"
      echo "  cursor     Install for Cursor IDE (.cursor/rules/)"
      echo "  codex      Install for OpenAI Codex (.codex/)"
      echo "  copilot    Install for GitHub Copilot (.github/copilot-instructions.md)"
      echo "  windsurf   Install for Windsurf/Cascade (.windsurf/rules/)"
      echo "  cline      Install for Cline (.clinerules/)"
      echo "  gemini     Install for Gemini Code Assist (GEMINI.md)"
      echo "  all        Install for ALL supported agents"
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
echo -e "${BOLD}║   Multi-Agent ROS 2 Development Harness               ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════╝${RESET}"
echo ""
info "Target: ${TARGET}"
info "Source: ${SCRIPT_DIR}"
[[ "$DRY_RUN" == true ]] && warn "DRY RUN — no files will be written"
echo ""

# ── Install function for Claude Code ──────────────────────────────────────────
install_claude() {
  local AGENTS_DIR="${CLAUDE_DIR}/agents"
  local COMMANDS_DIR="${CLAUDE_DIR}/commands"
  local RULES_DIR="${CLAUDE_DIR}/rules"
  local SKILLS_DIR="${CLAUDE_DIR}/skills"

  echo -e "${BOLD}Installing for Claude Code (${CLAUDE_DIR})...${RESET}"

  # Agents
  do_mkdir "$AGENTS_DIR"
  for agent in "${SCRIPT_DIR}/agents/"*.md; do
    [[ -f "$agent" ]] || continue
    do_copy "$agent" "${AGENTS_DIR}/$(basename "$agent")"
    success "Agent: $(basename "$agent")"
  done

  if [[ "$AGENTS_ONLY" == true ]]; then
    success "Agents installed (--agents-only mode)."
    return
  fi

  # Commands
  do_mkdir "$COMMANDS_DIR"
  for cmd in "${SCRIPT_DIR}/commands/"*.md; do
    [[ -f "$cmd" ]] || continue
    do_copy "$cmd" "${COMMANDS_DIR}/$(basename "$cmd")"
    success "Command: /$(basename "${cmd%.md}")"
  done

  # Rules
  do_mkdir "$RULES_DIR"
  for rule in "${SCRIPT_DIR}/rules/common/"*.md; do
    [[ -f "$rule" ]] || continue
    do_copy "$rule" "${RULES_DIR}/$(basename "$rule")"
    success "Rule (common): $(basename "$rule")"
  done
  for lang in cpp python; do
    for rule in "${SCRIPT_DIR}/rules/${lang}/"*.md; do
      [[ -f "$rule" ]] || continue
      do_copy "$rule" "${RULES_DIR}/$(basename "$rule")"
      success "Rule (${lang}): $(basename "$rule")"
    done
  done

  # Skills
  do_mkdir "$SKILLS_DIR"
  for skill_dir in "${SCRIPT_DIR}/skills/"*/; do
    local skill_name=$(basename "$skill_dir")
    local skill_file="${skill_dir}SKILL.md"
    if [[ -f "$skill_file" ]]; then
      do_mkdir "${SKILLS_DIR}/${skill_name}"
      do_copy "$skill_file" "${SKILLS_DIR}/${skill_name}/SKILL.md"
      success "Skill: ${skill_name}"
    fi
  done

  # Hooks
  if [[ "$SKIP_HOOKS" == false ]]; then
    local src_hooks="${SCRIPT_DIR}/hooks/hooks.json"
    if [[ -f "${CLAUDE_DIR}/hooks.json" ]]; then
      warn "~/.claude/hooks.json already exists — merging not yet automated."
      warn "Manually merge ${src_hooks} into ${CLAUDE_DIR}/hooks.json"
    else
      do_copy "$src_hooks" "${CLAUDE_DIR}/hooks.json"
      success "Hooks installed: ~/.claude/hooks.json"
    fi
    do_mkdir "${CLAUDE_DIR}/scripts/ros2-hooks"
    for script in "${SCRIPT_DIR}/scripts/hooks/"*.js; do
      [[ -f "$script" ]] || continue
      do_copy "$script" "${CLAUDE_DIR}/scripts/ros2-hooks/$(basename "$script")"
      success "Hook script: $(basename "$script")"
    done
  fi
}

# ── Install function for Cursor ───────────────────────────────────────────────
install_cursor() {
  echo -e "${BOLD}Installing for Cursor (.cursor/rules/)...${RESET}"

  local CURSOR_DIR="${PWD}/.cursor/rules"
  do_mkdir "$CURSOR_DIR"

  # Copy .mdc rules
  for mdc in "${SCRIPT_DIR}/.cursor/rules/"*.mdc; do
    [[ -f "$mdc" ]] || continue
    do_copy "$mdc" "${CURSOR_DIR}/$(basename "$mdc")"
    success "Cursor rule: $(basename "$mdc")"
  done

  # Copy AGENTS.md to project root for agent reference
  do_copy "${SCRIPT_DIR}/AGENTS.md" "${PWD}/AGENTS.md"
  success "AGENTS.md → project root"
}

# ── Install function for Codex ────────────────────────────────────────────────
install_codex() {
  echo -e "${BOLD}Installing for OpenAI Codex...${RESET}"

  local CODEX_DIR="${PWD}/.codex"
  do_mkdir "${CODEX_DIR}/agents"
  do_mkdir "${CODEX_DIR}/commands"
  do_mkdir "${CODEX_DIR}/rules"
  do_mkdir "${CODEX_DIR}/skills"

  for agent in "${SCRIPT_DIR}/agents/"*.md; do
    [[ -f "$agent" ]] || continue
    do_copy "$agent" "${CODEX_DIR}/agents/$(basename "$agent")"
    success "Agent: $(basename "$agent")"
  done

  if [[ "$AGENTS_ONLY" != true ]]; then
    for cmd in "${SCRIPT_DIR}/commands/"*.md; do
      [[ -f "$cmd" ]] || continue
      do_copy "$cmd" "${CODEX_DIR}/commands/$(basename "$cmd")"
    done
    for rule in "${SCRIPT_DIR}/rules/common/"*.md; do
      [[ -f "$rule" ]] || continue
      do_copy "$rule" "${CODEX_DIR}/rules/$(basename "$rule")"
    done
  fi

  # AGENTS.md at root is the primary entry point for Codex
  do_copy "${SCRIPT_DIR}/AGENTS.md" "${PWD}/AGENTS.md"
  success "AGENTS.md → project root"
}

# ── Install function for GitHub Copilot ───────────────────────────────────────
install_copilot() {
  echo -e "${BOLD}Installing for GitHub Copilot (.github/copilot-instructions.md)...${RESET}"

  do_mkdir "${PWD}/.github"
  do_copy "${SCRIPT_DIR}/.github/copilot-instructions.md" "${PWD}/.github/copilot-instructions.md"
  success "copilot-instructions.md → .github/"

  # Also copy AGENTS.md (Copilot coding agent reads it)
  do_copy "${SCRIPT_DIR}/AGENTS.md" "${PWD}/AGENTS.md"
  success "AGENTS.md → project root"
}

# ── Install function for Windsurf ─────────────────────────────────────────────
install_windsurf() {
  echo -e "${BOLD}Installing for Windsurf/Cascade (.windsurf/rules/)...${RESET}"

  local WINDSURF_DIR="${PWD}/.windsurf/rules"
  do_mkdir "$WINDSURF_DIR"

  do_copy "${SCRIPT_DIR}/.windsurf/rules/ros2-rules.md" "${WINDSURF_DIR}/ros2-rules.md"
  success "ros2-rules.md → .windsurf/rules/"

  do_copy "${SCRIPT_DIR}/AGENTS.md" "${PWD}/AGENTS.md"
  success "AGENTS.md → project root"
}

# ── Install function for Cline ────────────────────────────────────────────────
install_cline() {
  echo -e "${BOLD}Installing for Cline (.clinerules/)...${RESET}"

  local CLINE_DIR="${PWD}/.clinerules"
  do_mkdir "$CLINE_DIR"

  do_copy "${SCRIPT_DIR}/.clinerules/ros2-rules.md" "${CLINE_DIR}/ros2-rules.md"
  success "ros2-rules.md → .clinerules/"

  do_copy "${SCRIPT_DIR}/AGENTS.md" "${PWD}/AGENTS.md"
  success "AGENTS.md → project root"
}

# ── Install function for Gemini Code Assist ───────────────────────────────────
install_gemini() {
  echo -e "${BOLD}Installing for Gemini Code Assist (GEMINI.md)...${RESET}"

  do_copy "${SCRIPT_DIR}/GEMINI.md" "${PWD}/GEMINI.md"
  success "GEMINI.md → project root"

  do_copy "${SCRIPT_DIR}/AGENTS.md" "${PWD}/AGENTS.md"
  success "AGENTS.md → project root"
}

# ── Execute based on target ───────────────────────────────────────────────────
case "$TARGET" in
  claude)    install_claude ;;
  cursor)    install_cursor ;;
  codex)     install_codex ;;
  copilot)   install_copilot ;;
  windsurf)  install_windsurf ;;
  cline)     install_cline ;;
  gemini)    install_gemini ;;
  all)
    info "Installing for ALL supported agents..."
    echo ""
    install_claude
    echo ""
    install_cursor
    echo ""
    install_codex
    echo ""
    install_copilot
    echo ""
    install_windsurf
    echo ""
    install_cline
    echo ""
    install_gemini
    ;;
  *)
    error "Unknown target '$TARGET'. Use: claude | cursor | codex | copilot | windsurf | cline | gemini | all"
    ;;
esac

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}${BOLD}║   Installation complete! (target: ${TARGET})${RESET}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "Agents available:  $(ls "${SCRIPT_DIR}/agents/"*.md 2>/dev/null | wc -l | tr -d ' ')"
echo -e "Commands available: $(ls "${SCRIPT_DIR}/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')"
echo -e "Skills available:   $(find "${SCRIPT_DIR}/skills" -name 'SKILL.md' 2>/dev/null | wc -l | tr -d ' ')"
echo ""
echo -e "Supported agents:"
echo -e "  ${BOLD}Claude Code${RESET}     ./install.sh --target claude"
echo -e "  ${BOLD}Cursor${RESET}          ./install.sh --target cursor"
echo -e "  ${BOLD}GitHub Copilot${RESET}  ./install.sh --target copilot"
echo -e "  ${BOLD}Windsurf${RESET}        ./install.sh --target windsurf"
echo -e "  ${BOLD}Cline${RESET}           ./install.sh --target cline"
echo -e "  ${BOLD}Gemini${RESET}          ./install.sh --target gemini"
echo -e "  ${BOLD}OpenAI Codex${RESET}    ./install.sh --target codex"
echo -e "  ${BOLD}All agents${RESET}      ./install.sh --target all"
echo ""
echo -e "Next steps:"
echo -e "  1. Copy CLAUDE.md to your ROS 2 workspace root"
echo -e "  2. Set ROS_DISTRO in CLAUDE.md to your target distro"
echo -e "  3. Try: ${BOLD}/ros2-validate${RESET} in Claude Code"
echo -e "  4. Try: ${BOLD}/ros2-new-pkg my_robot_pkg --type cpp --distro humble${RESET}"
echo ""
