# Global skill sources

Install in this order:

1. `no-session/pstack` — existing workflow skills.
2. `mattpocock/skills` — engineering skills.
3. `cursor/plugins` at `pstack/skills` — full Cursor pstack, including `unslop`.

The final source intentionally wins name collisions. Today that means Cursor pstack provides `tdd`, `teach`, and `reflect`; the other libraries remain installed under their distinct names.

The installer targets every agent host supported by the Skills CLI. Codex and Claude Code are both supported.
