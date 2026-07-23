---
date: 2026-07-07
type: bad-assumption
domain: planning
severity: medium
---

# Plan proposed new infra that duplicated existing artifacts it never found

## What happened
The planning agent proposed creating `infra/demo/docker-compose.yml` from scratch and designing an Ollama URL guard, while `docker-compose.prod.yml` (homelab prod compose), `docs/deploy.md` (homelab deploy guide incl. Tailscale), and `lib/ollama-url.ts` (SSRF-safe validator) already existed. It also mislabeled the root `docker-compose.yml` as "cloud-v1" when it is the local homelab compose.

## What the fix was
Corrected plan extends `docker-compose.prod.yml` and reuses `lib/ollama-url.ts` and the deploy-guide patterns.

## Prevention rule
Before proposing any new deployment/config artifact, enumerate existing ones first (`find`/glob for compose files, Dockerfiles, deploy docs, related lib modules) and state why each is or isn't reusable.

## Context
ResumeLoop self-hosted demo planning, 2026-07.
