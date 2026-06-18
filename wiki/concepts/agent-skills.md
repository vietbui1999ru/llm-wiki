---
title: "Agent Skills"
type: concept
tags: [agent-engineering, skills, progressive-disclosure, prompt-injection, context-management]
sources:
  - "Agent Skills.md"
  - "Claude Agent Skills A First Principles Deep Dive.md"
  - "9 Things People Get Wrong With My grill-* skills.md"
  - "mattpocockskills Skills for Real Engineers. Straight from my .claude directory..md"
  - "Top 8 Claude Skills for UIUX Engineers.md"
  - "BuilderIOskills Skills for coding agents.md"
created: 2026-04-26
updated: 2026-06-17
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
argument-hint: "<path>"       # optional; merges slash-command functionality into skill
---
```

**Undocumented field**: `when_to_use` appears in source code — appended to description with " - " separator. Not in official docs; avoid in production until documented.

**Custom slash commands** are now merged into skills via the `argument-hint` frontmatter field — no separate slash command format.

### Progressive Disclosure

Three loading levels — only what's needed enters context:

| Level | When Loaded | Token Cost | Content |
|---|---|---|---|
| **Metadata** | Always (startup) | ~100/skill | name + description |
| **Instructions** | When triggered | <5k tokens | SKILL.md body |
| **Resources** | As referenced | Effectively unlimited | Scripts (output only), reference files, assets |

**Critical:** Script code never enters context — only script output. A 500-line Python script in `scripts/` costs ~0 tokens; only what it prints is visible to Claude.

**`references/` vs `assets/`**: `references/` (markdown docs) cost tokens — text is read into context via the Read tool. `assets/` (templates, images) cost zero tokens — referenced by path only, never read into context. Prefer `assets/` for large binary or template files.

The `Skill` meta-tool's description contains a dynamically generated `<available_skills>` block with a **15,000 character budget** for listing all loaded skills. Near this limit, skill descriptions may be truncated — keep descriptions concise.

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

Snyk ToxicSkills research found prompt injection in **36% of tested skills**, with 1,467 malicious payloads found across the ecosystem. Always read `SKILL.md` and bundled scripts before installing. `Bash` in `allowed-tools` warrants extra scrutiny.

Rule: treat Skills like software packages — only use from trusted sources.

## Skill Composition Patterns

Skills can be chained through context: invoke one skill to produce context/artifacts, then invoke another skill that operates on that output. Common compositions:

- **grill → to-prd → to-issues**: planning session → PRD → task breakdown
- **grill → handoff → prototype → handoff back**: handle high-fidelity questions via prototype detour
- **diagnose → tdd**: establish feedback loop → implement fix with red-green-refactor

Skills do not call other skills directly. Composition happens through the shared conversation context and user direction.

## Grill-* Skills: Specific Antipatterns

The `/grill-me` and `/grill-with-docs` skills fail in predictable ways. Key patterns:

| Antipattern | Fix |
|---|---|
| Answering high-fidelity questions in grilling | Use `/handoff` to prototype session; return after |
| Grilling too large a scope | Break scope first; grill each piece separately |
| Being too passive | Lead the conversation; redirect off-scope questions |
| Clearing context before handoff | Create `/to-prd` or `/handoff` artifact first |
| Using small model for grilling | Grilling needs parametric knowledge → use frontier model |
| Running a single grilling session | Run 2 in parallel for 2× throughput |

**Low vs. high fidelity questions** (Ryan Singer / Shape Up):
- **Low-fidelity** — answerable by Q&A: "what URL?", "which field is optional?" → grillable
- **High-fidelity** — needs prototype to answer: "how will this 12-field form feel?" → ungrillable; hand off

## When NOT to Use Skills

Skills add ~1,500+ tokens of overhead per invocation. Avoid when:
- Task is one-off with no reuse potential — just prompt directly
- Context window is already constrained — skill injection may push into "dumb zone"
- The workflow is already defined in CLAUDE.md — no need for a skill to reinject context
- User is at implementation stage with a detailed plan — skills designed for planning/setup phases pay less dividends here

Prefer direct prompting for: quick one-shot tasks, tasks fully specified in context, simple file transformations with no workflow complexity.

## Visual Artifact Skills

Builder.io's skills package adds a concrete pattern: skills that produce reviewable artifacts instead of more chat text.

- `/visual-plan` turns implementation plans into MDX documents with diagrams, file maps, annotated code, open questions, and UI/prototype review surfaces.
- `/visual-recap` turns a branch, commit, PR, or diff into a visual recap with annotated diffs, API/schema summaries, architecture diagrams, and UI impact notes.

The pattern is valuable because it moves high-leverage context out of the transient chat stream and into durable, commentable artifacts. It also matches [[concepts/compound-engineering]]: plans and recaps become reusable system memory rather than one-off messages.

Other Builder.io skills map to existing wiki patterns: `/plan-arbiter` implements [[concepts/multi-vendor-adversarial-review]] for competing plans, `/efficient-frontier` implements [[concepts/model-tier-routing]], and `/read-the-damn-docs` is an operational form of the context7/current-docs rule.

## Related Pages

- [[concepts/agent-harness]] — harness components including skill/progressive disclosure as context management
- [[concepts/agent-subagents]] — subagents and how skills can be preloaded into them
- [[concepts/agent-teams]] — teams and skill loading behavior
- [[concepts/indirect-prompt-injection]] — attack vector via malicious skill content
- [[concepts/claude-code-plugins]] — plugin system that namespaces and bundles skills
- [[summaries/builderio-skills]] — Builder.io skill catalog with visual plan/recap artifacts
