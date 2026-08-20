# Global skill inventory

## Restore order

Install these sources in order. The later source wins duplicate names.

1. `no-session/pstack`
2. `mattpocock/skills`
3. `https://github.com/cursor/plugins/tree/main/pstack/skills`
4. `skills/unslop/SKILL.md` from this repository

The bootstrap scripts install all skills from each source globally for every host supported by the Skills CLI. They then apply the tracked `unslop` overlay and remove em dashes from every discovered `SKILL.md`. Cursor pstack intentionally provides the active `tdd`, `teach`, and `reflect` variants.

## Current inventory

### Cursor pstack

`architect`, `arena`, `automate-me`, `blast-radius`, `bro`, `create-verification-skill`, `figure-it-out`, `how`, `interrogate`, `maintain-verification-skill`, `no-comments`, `poteto-mode`, `recall`, `reflect`, `setup-pstack`, `show-me-your-work`, `swarm`, `tdd`, `teach`, `technical-writing`, `typescript-best-practices`, `unslop`, `why`.

`principle-boundary-discipline`, `principle-build-the-lever`, `principle-encode-lessons-in-structure`, `principle-exhaust-the-design-space`, `principle-experience-first`, `principle-fix-root-causes`, `principle-foundational-thinking`, `principle-guard-the-context-window`, `principle-laziness-protocol`, `principle-make-operations-idempotent`, `principle-migrate-callers-then-delete-legacy-apis`, `principle-minimize-reader-load`, `principle-model-the-domain`, `principle-never-block-on-the-human`, `principle-outcome-oriented-execution`, `principle-prove-it-works`, `principle-redesign-from-first-principles`, `principle-separate-before-serializing-shared-state`, `principle-sequence-verifiable-units`, `principle-subtract-before-you-add`, `principle-type-system-discipline`.

### Matt Pocock

`ask-matt`, `claude-handoff`, `code-review`, `codebase-design`, `diagnosing-bugs`, `domain-modeling`, `git-guardrails-claude-code`, `grill-me`, `grill-with-docs`, `grilling`, `handoff`, `implement`, `improve-codebase-architecture`, `loop-me`, `migrate-to-shoehorn`, `prototype`, `research`, `resolving-merge-conflicts`, `scaffold-exercises`, `setup-matt-pocock-skills`, `setup-pre-commit`, `setup-ts-deep-modules`, `to-questionnaire`, `to-spec`, `to-tickets`, `triage`, `wait-what`, `wayfinder`, `wizard`, `writing-beats`, `writing-for-agents`, `writing-fragments`, `writing-shape`.

### No-session pstack

`pstack`, `benchmark`, `browse`, `careful`, `codex`, `connect-chrome`, `cso`, `design-consultation`, `design-review`, `design-shotgun`, `document-release`, `freeze`, `guard`, `investigate`, `land-and-deploy`, `monitor`, `plan`, `plan-ceo-review`, `plan-design-review`, `plan-eng-review`, `qa`, `qa-only`, `review`, `setup-browser-cookies`, `setup-deploy`, `ship`, `unfreeze`, `pstack-upgrade`, `validate`.

## Update rule

After any global skill change, update this file with its source, installation order, and name. Keep the source command in `install.ps1` and `install.sh` in sync with this file.
