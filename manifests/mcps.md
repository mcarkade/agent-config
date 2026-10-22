# MCP inventory

MCP registrations and their runtime commands live in each user's client configuration, not in this repository. Use the official setup command to preserve unrelated client settings and create a recovery backup.

## REA

- Source: [morluto/rea](https://github.com/morluto/rea)
- Package: `rea-agents@6.7.0`
- Clients configured on this machine: Codex, Claude Code
- Setup: `npx -y rea-agents@6.7.0 setup --client codex` and `npx -y rea-agents@6.7.0 setup --client claude_code`
- Read-only plan: add `--dry-run --format json` to either setup command
- Verify: `npx -y rea-agents@6.7.0 doctor --client codex --skill --json` and `npx -y rea-agents@6.7.0 doctor --client claude_code --skill --json`
- Installed skill source: `skills/reverse-engineer-anything/`, copied from the same release (skill version 42, 207 tools).

REA setup pins the Codex MCP command to this package version and installs the bundled skill. Review its planned paths before approving setup. It does not install Hopper, Ghidra, IDA, or other analysis engines unless separately selected. After setup, restart Codex so the MCP connection and skill are rediscovered.

When updating REA, update the pinned package version and bundled skill together, then verify the matching tool catalog. The repository's main branch can contain a newer unreleased skill than the latest npm package; do not mix those versions silently.
