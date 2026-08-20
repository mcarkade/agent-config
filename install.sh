#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

backup_and_copy() {
  local source="$1" destination="$2"
  mkdir -p "$(dirname "$destination")"
  if [ -f "$destination" ]; then
    cp "$destination" "${destination}.backup-$(date +%Y%m%d%H%M%S)"
  fi
  cp "$source" "$destination"
}

install_skills() {
  npx skills@latest add "$1" --all --global --agent '*' --yes --full-depth
}

# This order preserves the preferred Cursor pstack variants for duplicate names.
install_skills 'no-session/pstack'
install_skills 'mattpocock/skills'
install_skills 'https://github.com/cursor/plugins/tree/main/pstack/skills'

# Apply maintained skill overlays after upstream installs.
mkdir -p "$HOME/.agents/skills/unslop"
cp "$root/skills/unslop/SKILL.md" "$HOME/.agents/skills/unslop/SKILL.md"

node "$root/scripts/remove-em-dashes.mjs" \
  "$root/skills" \
  "$HOME/.agents/skills" \
  "$HOME/.codex/skills" \
  "$HOME/.claude/skills" \
  "$HOME/.codex/plugins/cache" \
  "$HOME/.claude/plugins/cache"

backup_and_copy "$root/global/AGENTS.md" "$HOME/.codex/AGENTS.md"
backup_and_copy "$root/global/CLAUDE.md" "$HOME/.claude/CLAUDE.md"

echo 'Global skills and instructions restored. Restart Codex and Claude Code sessions.'
