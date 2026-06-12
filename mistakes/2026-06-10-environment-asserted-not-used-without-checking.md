---
date: 2026-06-10
type: bad-assumption
domain: environment-inspection
severity: medium
---

# Asserted a tool was "not used" from docs/memory without inspecting the live environment

## What happened
Asked whether the Commandr repo uses Headroom (AI context-compression). Answered "no, zero external services" twice — relying on CLAUDE.md ("v1 infra: zero external services") and training data. Both background agents did the same. In fact the Headroom proxy (v0.24.0) was running on `127.0.0.1:8787`, `ANTHROPIC_BASE_URL` pointed at it, and a `settings.local.json` hook auto-started it — so every Claude Code turn was already routed through Headroom.

## What the fix was
Inspected the live environment: `env | rg ANTHROPIC_BASE_URL`, `lsof -iTCP:8787`, `curl localhost:8787/health`, and read the gitignored `.claude/settings.local.json`. Confirmed the proxy was active and reversed the answer.

## Prevention rule
Before asserting a tool/service/integration is "not used," check the live environment (env vars, listening ports, running processes, machine-local + gitignored config) — not just committed docs, manifests, and memory. Distinguish product source from the harness/session it runs under: "not in the repo's deps" ≠ "not active in this session."

## Context
A `/btw` background question. The harness config that enabled Headroom lived in `.claude/settings.local.json`, which is gitignored — invisible to a docs-only or git-only check. The "zero external services" claim was true of Commandr-the-product but not of the Claude Code harness running it.
