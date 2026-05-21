---
title: "PentAGI"
type: entity
tags: [security, penetration-testing, agents, multi-agent, autonomous, OSS]
sources: ["vxcontrolpentagi Fully autonomous AI Agents system capable of performing complex penetration testing tasks.md"]
created: 2026-05-21
updated: 2026-05-21
---

# PentAGI

Fully autonomous, self-hosted penetration testing system powered by multi-agent AI. OSS (GitHub: vxcontrol/pentagi). Docker Compose deployment. Supports 10+ LLM providers including Anthropic.

## What It Does

PentAGI runs autonomous pen tests end-to-end: recon, exploitation planning, tool execution, memory storage, and report generation. Human sets the target; agents drive the rest with optional monitoring.

## Agent Architecture

Three-tier delegation:

| Agent | Role |
|---|---|
| Orchestrator | Plans flow, routes to specialists, synthesizes results |
| Researcher | Gathers intel, queries knowledge base, identifies vulnerabilities |
| Developer | Plans attack sequences, selects exploits |
| Executor | Runs tools, stores results, reports back |

Data model: `Flow → Task → SubTask → Action → Artifact/Memory`. Each action produces artifacts (files, reports, logs) and memories (observations stored as vectors).

## Memory System

Three memory tiers:
- **Long-term**: vector store (pgvector), knowledge base, tool usage patterns
- **Working**: current task context, active goals, system state
- **Episodic**: past actions, outcomes, success patterns

Orchestrator queries vector store at flow start to surface similar past tasks — avoids re-exploring known terrain.

## Context Management

Built-in chain summarization: when conversation chain grows too large, converts to `ChainAST`, summarizes older message pairs, rebuilds a smaller chain. Configurable: preserve-last-section (default 50KB), max body pair size (16KB). This prevents token limit failures mid-pentest.

See [[concepts/context-compression]] — PentAGI's chain summarization is an instance of anchored iterative summarization.

## Security Tools (20+)

Includes: nmap, sqlmap, metasploit, and web browser (isolated scraper container). All tools run in sandboxed Docker containers — host is never directly exposed. Tool selection is automatic based on task requirements.

## Infrastructure Stack

- **Backend**: Go + GraphQL API
- **Frontend**: React + TypeScript
- **Storage**: PostgreSQL + pgvector (vector search), Neo4j + Graphiti (knowledge graph)
- **Observability**: Grafana, VictoriaMetrics, Jaeger (tracing), Loki (logs), Langfuse (LLM analytics)
- **Queue**: async task queue between API and agent layer

## Key Differentiators vs. Our Design

| Feature | PentAGI | Our pentest-agent |
|---|---|---|
| Scope | General-purpose, any target | Next.js + ECS + Neon specific |
| Memory | pgvector + Neo4j knowledge graph | Shared filesystem (JSON) |
| Tools | 20+ (metasploit, etc.) | Targeted: nuclei, nmap, sqlmap, testssl, Prowler, Trivy |
| Deployment | Docker Compose microservices | Local script → GitHub Actions |
| Context mgmt | Chain summarization | Per-agent isolated context |
| Auth handling | Not highlighted | Dedicated test account + session injection |

## What to Borrow

- **Flow → Task → SubTask** hierarchy maps to our supervisor → specialist → tool call structure
- **Accessible vs. target domains** — same as AWS Security Agent's pattern
- **Chain summarization** — relevant if our agents hit context limits during long scans
- **Sandboxed tool execution** — run CLI tools in subprocess isolation, not direct shell

## Related Pages

- [[summaries/aws-security-agent]] — managed AWS alternative; compare scope control patterns
- [[concepts/pentest-agent-design]] — our custom agent built from both reference sources
- [[concepts/agent-harness]] — supervisor pattern PentAGI instantiates
- [[concepts/context-compression]] — PentAGI's chain summarization is a live example
