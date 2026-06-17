---
date: 2026-06-17
type: bad-assumption
domain: vitest-cli-verification
severity: low
---

# Interactive CLI Verification Hung During Registry Check

## What happened
I added a Vitest test that used `process.chdir()`, which is unsupported in Vitest workers, then ran `resumeloop onboard` with blank piped input and caused the interactive provider prompt to loop until timeout.

## What the fix was
Replace the test with a cwd-independent `registryPath()` assertion and verify outside-repo behavior through a non-interactive registry import instead of the onboarding wizard.

## Prevention rule
When verifying cwd-independent code, test the path resolver or run a non-interactive child command; do not drive an interactive wizard unless every prompt has bounded scripted input.

## Context
Fixing ResumeLoop provider registry lookup so packaged/global CLI usage loads `config/providers.yml` from the package root rather than caller cwd.
