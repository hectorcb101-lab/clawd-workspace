---
name: fix
description: Run typechecking and linting, then spawn parallel agents to fix all issues
---

Run all linting and typechecking tools, collect errors, group them by domain, and use the subagent tool to spawn parallel sub-agents to fix them.

## Step 1: Run Checks

Run these commands and capture their full output (allow non-zero exit codes):

```bash
npm run typecheck 2>&1
npm run lint 2>&1
```

## Step 2: Collect and Group Errors

Parse the output from Step 1. Group errors into these domains:

- **Type errors**: Issues from `tsc --noEmit` (TypeScript compiler errors)
- **Lint errors**: Issues from `eslint` (unused vars, style violations, etc.)

If both commands pass with zero errors, report success and stop.

## Step 3: Spawn Parallel Agents

For each domain that has errors, use the `subagent` tool to spawn a sub-agent to fix all errors in that domain. Include the full error output in the agent's task so it knows exactly what to fix.

**Type errors agent task template:**
> Fix all TypeScript type errors in the atlas-intel project. Run `npm run typecheck` to see current errors. Fix each error in the source files under `src/`. Do not use `any` type or `@ts-ignore` unless absolutely necessary. After fixing, re-run `npm run typecheck` to verify zero errors.

**Lint errors agent task template:**
> Fix all ESLint lint errors in the atlas-intel project. Run `npm run lint` to see current errors. Fix each error in the source files under `src/`. Prefer fixing the root cause over disabling rules. Use `// eslint-disable-next-line` only as a last resort with a justification comment. After fixing, re-run `npm run lint` to verify zero errors.

Spawn these agents in parallel if both domains have errors.

## Step 4: Verify

After all agents complete, re-run all checks to confirm everything passes:

```bash
npm run typecheck 2>&1
npm run lint 2>&1
```

If any issues remain, report them clearly. Do NOT spawn another round of agents — just list the remaining issues for the user.
