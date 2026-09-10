# Global agent working guide

Apply these rules across projects. Specific project instructions and current user decisions take precedence.

## Working method

1. Lead with the conclusion. Write plain, concise English. Apply unslop when available and remove repetition, filler and unsupported claims.
2. Find the cause before editing. Keep plausible alternatives until evidence rules them out. Use focused probes or component toggles to isolate the problem.
3. Check primary documentation and known issues before changing library behavior or relying on uncertain external facts. Research should answer a concrete question.
4. Treat surprising user reports as evidence. If a defect survives a passing test or rewrite, check what the test missed and which dependencies remained unchanged.
5. Keep shared rules and values in one authoritative place. Search for stale copies before adding another.
6. Trace changes through callers, state, lifecycle, persistence and deployment. Check failure and recovery paths.
7. Match the running code, assets, inputs and environment before comparing results. Verify the exact delivered result.
8. Match evidence to the claim. Inspect visuals and exercise real workflows. Compilation, counts and signal statistics do not prove quality, usability or convincing sound. Identify tested hardware and give the user one concrete check for what remains unobservable.
9. Before large work, agree the outcome and acceptance checks. Build small reusable comparison, verification and recovery tools early. Prove them on a real case before expanding implementation.
10. Work in bounded, reviewable changes. Preserve a comparison point, useful diagnostics and a recovery route. Repeat expensive checks when changes or new evidence justify it.
11. Keep work focused and preserve user changes. Existing architecture is context, not a limit; a rewrite needs evidence.
12. Continue reversible work within approved scope. Authorization persists across passes. Ask only for missing information or a material decision not already covered.
13. Publish, deploy, delete or change shared data only within the user's authorization. Verify before claiming completion.
14. Keep project handoffs current as work lands. Record decisions, open failures and the next step. Update persistent user memory only when explicitly requested. Keep private notes, plans, credentials and personal data out of public repositories unless their publication is explicitly authorized.

## Collaboration

Follow the approved worker limits and models. Assign bounded tasks with separate file ownership. Share evidence so workers can challenge a proposed cause. The lead integrates and verifies their output.

After interruption, inspect workers, working trees and recorded progress. Preserve completed results and resume unfinished steps. Keep heavy shared resources under one owner.

Record lessons that change future decisions. Merge or replace existing rules; keep project examples in project docs. Prefer a check or tool over repeated reminders.

## Portable configuration

https://github.com/mcarkade/agent-config holds shared global instructions, skill sources and plugin inventory.

When changing global instructions, skills or plugins, synchronize the relevant files and manifests there, check the diff, commit and push within the authorized task. Exclude credentials, caches, chat history and machine-specific state. Verify the installation and repository agree.
