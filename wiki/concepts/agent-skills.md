---
title: "Agent Skills"
type: concept
tags: [agent-engineering, skills, progressive-disclosure, prompt-injection, context-management]
sources:
  - "Agent Skills.md"
  - "Claude Agent Skills A First Principles Deep Dive.md"
created: 2026-04-26
updated: 2026-04-26
---

# Agent Skills

Skills are reusable, filesystem-based resources that give Claude domain-specific expertise on demand. Unlike subagents (separate context windows) or tools (executable functions), Skills are **prompt templates** that inject specialized instructions into the current conversation context when triggered.

**Key insight:** Skills do not execute code. They prepare Claude to solve a problem by expanding into detailed instructions, modifying tool permissions, and optionally switching models — then Claude executes from that enriched context.

## How Skills Work

Skills operate via a meta-tool architecture:

1. **At startup** — Claude loads all Skill metadata (name + description only, ~100 tokens/skill) into its context via the `Skill` meta-tool's description
2. **User sends request** — Claude reasons over available skills and decides whether to invoke one (pure LLM reasoning, no algorithmic matching)
3. **Skill tool fires** — Two messages are injected:
   - Message 1 (visible): `<command-message>The "pdf" skill is loading</command-message>` — status for the user
   - Message 2 (`isMeta: true`, hidden): full SKILL.md content — instructions for Claude
4. **Execution context modified** — Allowed tools pre-approved, model optionally overridden
5. **Claude continues** with enriched context and restricted/expanded tool access

Skills are fundamentally different from tools:

| Aspect | Traditional Tools (Read, Bash) | Skills |
|---|---|---|
| Execution | Direct action → result | Prompt expansion → Claude acts |
| Purpose | Discrete operations | Guide complex workflows |
| Token cost | ~100 tokens | ~1,500+ tokens per invocation |
| Persistence | One turn | Temporary session context shift |
| Selection | Deterministic | LLM reasoning |

## Skill Structure

Every Skill is a directory containing `SKILL.md` and optional bundled resources:

```
my-skill/
├── SKILL.md          # Core prompt and instructions (required)
├── scripts/          # Executable Python/Bash scripts
├── references/       # Markdown docs loaded into context on demand
└── assets/           # Templates and binary files referenced by path
```

### SKILL.md Frontmatter

```yaml
---
name: skill-name              # required; lowercase, hyphens only
description: What it does and WHEN to use it — this is what Claude reads to decide
allowed-tools: "Read,Write,Bash(git:*)"  # optional; principle of least privilege
model: inherit                # optional; inherit | sonnet | opus | haiku | full ID
version: "1.0.0"              # optional; metadata only
disable-model-invocation: false  # optional; true = user-only invocation via /skill-name
mode: false                   # optional; true = appears in "Mode Commands" section
---
```

### Progressive Disclosure

Three loading levels — only what's needed enters context:

| Level | When Loaded | Token Cost | Content |
|---|---|---|---|
| **Metadata** | Always (startup) | ~100/skill | name + description |
| **Instructions** | When triggered | <5k tokens | SKILL.md body |
| **Resources** | As referenced | Effectively unlimited | Scripts (output only), reference files, assets |

**Critical:** Script code never enters context — only script output. A 500-line Python script in `scripts/` costs ~0 tokens; only what it prints is visible to Claude.

## Skill Scopes (Claude Code)

| Location | Scope |
|---|---|
| `~/.claude/skills/` | All projects (user) |
| `.claude/skills/` | Current project only |
| Plugin `skills/` directory | Where plugin is installed |

## Common Patterns

**Script Automation** — offload deterministic logic to `scripts/`:
```markdown
Run scripts/analyzer.py on {userPath}:
`python {baseDir}/scripts/analyzer.py --path "$USER_PATH"`
```

**Read-Process-Write** — file transformation:
```yaml
allowed-tools: "Read,Write"
```

**Search-Analyze-Report** — codebase audit:
```yaml
allowed-tools: "Grep,Read"
```

**Iterative Refinement** — multi-pass with increasing depth: broad scan → deep analysis → recommendation

**Wizard-Style** — step-by-step with user confirmation between phases

## Relationship to Subagents

From the official docs:
- **Skills**: run in the main conversation context; reusable prompts/workflows
- **Subagents**: separate context windows; isolated execution with own tools/model/permissions
- **Preloading skills into subagents**: via `skills:` frontmatter field — full skill content injected at subagent startup

Subagents don't inherit parent skills. List them explicitly in the subagent's `skills:` field.

## Security

Skills from untrusted sources are a prompt injection vector. A malicious SKILL.md can:
- Invoke tools in harmful ways
- Exfiltrate data via network calls
- Execute arbitrary bash

Rule: treat Skills like software packages — only use from trusted sources.

## Related Pages

- [[concepts/agent-harness]] — harness components including skill/progressive disclosure as context management
- [[concepts/agent-subagents]] — subagents and how skills can be preloaded into them
- [[concepts/agent-teams]] — teams and skill loading behavior
- [[concepts/indirect-prompt-injection]] — attack vector via malicious skill content
