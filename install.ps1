$ErrorActionPreference = 'Stop'

function Backup-And-Copy([string]$Source, [string]$Destination) {
  $destinationDirectory = Split-Path -Parent $Destination
  New-Item -ItemType Directory -Force -Path $destinationDirectory | Out-Null
  if (Test-Path $Destination) {
    Copy-Item $Destination "$Destination.backup-$(Get-Date -Format yyyyMMddHHmmss)"
  }
  Copy-Item $Source $Destination -Force
}

function Install-Skills([string]$Source) {
  & npx skills@latest add $Source --all --global --agent '*' --yes --full-depth
  if ($LASTEXITCODE -ne 0) { throw "Skill installation failed: $Source" }
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# This order preserves the preferred Cursor pstack variants for duplicate names.
Install-Skills 'no-session/pstack'
Install-Skills 'mattpocock/skills'
Install-Skills 'https://github.com/cursor/plugins/tree/main/pstack/skills'

# Apply maintained skill overlays after upstream installs.
Copy-Item "$root\skills\unslop\SKILL.md" "$env:USERPROFILE\.agents\skills\unslop\SKILL.md" -Force

& node "$root\scripts\remove-em-dashes.mjs" `
  "$root\skills" `
  "$env:USERPROFILE\.agents\skills" `
  "$env:USERPROFILE\.codex\skills" `
  "$env:USERPROFILE\.claude\skills" `
  "$env:USERPROFILE\.codex\plugins\cache" `
  "$env:USERPROFILE\.claude\plugins\cache"
if ($LASTEXITCODE -ne 0) { throw 'Em dash cleanup failed.' }

Backup-And-Copy "$root\global\AGENTS.md" "$env:USERPROFILE\.codex\AGENTS.md"
Backup-And-Copy "$root\global\CLAUDE.md" "$env:USERPROFILE\.claude\CLAUDE.md"

Write-Host 'Global skills and instructions restored. Restart Codex and Claude Code sessions.'
