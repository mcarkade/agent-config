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

Backup-And-Copy "$root\global\AGENTS.md" "$env:USERPROFILE\.codex\AGENTS.md"
Backup-And-Copy "$root\global\CLAUDE.md" "$env:USERPROFILE\.claude\CLAUDE.md"

Write-Host 'Global skills and instructions restored. Restart Codex and Claude Code sessions.'
