# mcarkade agent configuration

Portable global setup for Codex, Claude Code, and compatible agent harnesses.

This repository deliberately stores only reproducible configuration:

- global `AGENTS.md` and `CLAUDE.md` guidance;
- skill-library sources and installation order;
- a Windows PowerShell bootstrap and an Ubuntu/Linux shell bootstrap.

It does **not** store credentials, OAuth sessions, API keys, agent chat history, databases, caches, or machine-specific Codex settings.

## New device setup

1. Install and sign in to Codex and/or Claude Code.
2. Install Node.js and Git.
3. Authenticate GitHub CLI if you want to access this private repository: `gh auth login`.
4. Clone this repo, then run the platform bootstrap:

   Windows: `./install.ps1`

   Ubuntu/Linux: `bash ./install.sh`

5. Restart agent sessions so they rediscover global skills.

The bootstrap installs skills globally for every supported agent harness. It restores the two global instruction files with a timestamped backup of the prior local copy.

## Maintenance

Edit the tracked files here, commit, and push. On another machine, pull and rerun the appropriate bootstrap. When upstream skill libraries change, rerunning the bootstrap refreshes them.

See [manifests/skills.md](manifests/skills.md) and [manifests/plugins.md](manifests/plugins.md).
