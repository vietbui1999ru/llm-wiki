---
date: 2026-05-18
type: tool-misuse
domain: vitest
severity: medium
---

# Used `npx jest` to run tests in a Vitest project

## What happened
Ran `npx jest github-ingest --no-coverage` to verify whether a test was passing after adding
`import 'server-only'` to `lib/ai-client.ts`. The project uses Vitest (`npm test` → `vitest run`),
not Jest. Jest picked up Vitest-syntax test files from `.claude/worktrees/` and reported
"SyntaxError: Cannot use import statement outside a module" — a completely misleading error
with no relation to the actual test suite state.

## What the fix was
Run `npm test` (which invokes `vitest run`) to check the real test suite.
Always check `package.json` `"scripts"."test"` before running any test command.

## Prevention rule
Before running any test command: check `package.json` scripts.test. Do NOT assume `npx jest`
— if the project uses Vitest, Jest produces misleading errors from incompatible worktree files.

## Context
Was verifying that adding `import 'server-only'` to lib files (security fix M3) did not break
the test suite. The worktrees in `.claude/worktrees/` contain Vitest-syntax test files that
Jest cannot parse, making the failure undiagnosable from Jest output alone.
