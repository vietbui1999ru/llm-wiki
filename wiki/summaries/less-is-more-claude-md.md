---
title: "Stop Stuffing Your CLAUDE.md. The Research Says Less Is More."
type: summary
tags: [claude-md, agents-md, context-files, research, progressive-disclosure]
sources: ["Stop Stuffing Your CLAUDE.md. The Research Says Less Is More..md"]
created: 2026-10-22
updated: 2026-10-22
---

# Stop Stuffing Your CLAUDE.md (Pattern Interruption, first published 2026-03-03)

Blog summary of Gloaguen, Mündler, Müller, Raychev & Vechev (ETH Zurich / LogicStar.ai), **"Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?"**, arXiv:2602.11988 (Feb 2026). The paper itself was not ingested; numbers below are as reported by the blog *(secondary source; verify against the paper)*.

## Study design (as reported)

New benchmark (the blog calls it "AgentBench"; distinct from the older AgentBench of Liu et al.): 138 real GitHub issues from 12 repos that already had developer-written context files. Four agent/model setups: Claude Code + Sonnet 4.5, Codex + GPT-5.2, Codex + GPT-5.1 Mini, Qwen Code + Qwen3-30B. Three conditions: no context file; LLM-generated file (`/init`-style); the developers' own file.

## Reported findings

- **LLM-generated context files reduced task success by ~2–3% on average and raised inference cost by > 20%.**
- **Developer-written files: ~+4% success**, but still more cost and more steps.
- 100% of Sonnet-4.5-generated files (95–99% for other models) contained a codebase overview, which is redundant with README/ls.
- Context files did **not** help agents find the relevant files faster; agents sometimes re-read the context file.
- With context files, agents ran more tests, grepped and read more, and used more repo-specific tooling: obedient but not more successful. GPT-5.2 reasoning tokens +22% with generated files.
- When *all* other docs were removed from the repo, generated files finally beat no file, which suggests `/init` mostly parrots existing documentation.
- Paper quote: "human-written context files should describe only minimal requirements."

## Recommended shape

A ~30-line hand-written pointer file:

- Commands (test, lint, typecheck, single test).
- **Non-obvious rules** only (migration workflow, auth is custom HMAC not JWT, modules X and Y must not cross-import).
- **Key documents** to load on demand, above all a 2–4 page **Software System Design (SSD)** doc: purpose, architectural decisions *and rejected alternatives*, component boundaries (what each must *not* own), data flow, security model, known traps.

Leave out anything discoverable: tech stack, directory tree, code style, endpoints, general best practices. Test for linked docs: could a competent developer learn this from the code and existing docs? If yes, do not link it.

## Wiki connections

- [[concepts/agent-context-instructions]]: **contradicts** that page's "What to include" template (project overview, style sections). Flagged there.
- [[concepts/context-degradation]]: distraction failure mode, measured.
- [[entities/agents-md-format]]: the format under test.
- [[summaries/steer-not-script-agent-instructions]]: companion piece.
