---
title: "Claude Agent Skills — First Principles Deep Dive"
type: summary
tags: [agent-skills, claude-code, meta-tool, architecture, prompt-injection, security]
sources:
  - "Claude Agent Skills A First Principles Deep Dive.md"
created: 2026-05-25
updated: 2026-05-25
---

# Claude Agent Skills — First Principles Deep Dive

Source: [leehanchung.github.io — Claude Agent Skills: A First Principles Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/) (Oct 2025). Detailed reverse-engineering of the Claude Code skill system from the Claude Code client source.

## Core mental model

Skills are **prompt-based conversation and execution context modifiers**. They do not execute code. They:
1. Inject instruction prompts into conversation history (`isMeta: true`)
2. Modify execution context: tool permissions + optional model override
3. Return enriched context so Claude then acts on specialized instructions

Contrast with traditional tools (`Read`, `Bash`): tools execute a discrete action and return a result. Skills prepare Claude to solve a problem class.

## The `Skill` Meta-Tool

Skills live in the `tools` array of the API request — **not** in the system prompt. A single meta-tool named `Skill` (capital S) manages all individual skills. Its description contains a dynamically generated `<available_skills>` block (15,000 char budget) listing every loaded skill with name + description.

```
tools: [
  { name: "Skill", description: "...<available_skills>\n\"pdf\": Extract text...\n</available_skills>" },
  { name: "Bash", ... },
  { name: "Read", ... }
]
```

Selection is **pure LLM reasoning** — no embeddings, no classifiers, no regex. Claude reads the skill list and decides which (if any) to invoke via its forward pass.

## Three-Tier Loading (Progressive Disclosure)

| Tier | When | Token cost | Content |
|---|---|---|---|
| 1 — Metadata | Startup, always | ~100/skill | name + description from frontmatter |
| 2 — Instructions | After skill invoked | <5k tokens | Full SKILL.md body |
| 3 — Resources | As referenced | Unlimited | scripts/ output, references/ text, assets/ paths |

Script code never enters context — only script stdout. A 500-line Python helper costs ~0 tokens.

## Execution Flow (5 phases)

1. **Startup** — Claude Code scans `~/.claude/skills/`, `.claude/skills/`, plugins. Builds available skills list.
2. **Turn 1** — User sends request. Claude reads `<available_skills>`, reasons, invokes `Skill` tool with `command: "pdf"`.
3. **Skill Tool Execution** — Validates skill, checks permissions, loads SKILL.md, yields:
   - Message A (visible, `isMeta: false`): `<command-message>The "pdf" skill is loading</command-message>`
   - Message B (hidden, `isMeta: true`): full SKILL.md prompt
   - Context modifier: pre-approves allowed-tools, overrides model if specified
4. **API Call** — Full message history (including hidden prompt) sent to Anthropic API.
5. **Tool Use with Skill Context** — Claude acts under enriched context + pre-approved permissions.

## Why Two Messages

Single-message design forces a tradeoff: visible = dumps 5k words of AI instructions into user's chat; hidden = zero transparency. The two-message split resolves this:

| | Metadata message | Skill prompt |
|---|---|---|
| Audience | Human | Claude |
| isMeta | false (visible) | true (hidden) |
| Length | 50–200 chars | 500–5,000 words |
| Format | Structured XML | Markdown instructions |

## SKILL.md Format Details

Two-part structure: YAML frontmatter (configuration) + markdown body (Claude's instructions).

**Critical frontmatter fields:**
- `name` — becomes the `command` value in Skill tool invocations
- `description` — **the primary matching signal**; must be action-oriented and specific
- `allowed-tools` — comma-separated; scoped wildcards supported (`Bash(git:*)`)
- `model` — `inherit` (default) or specific model ID
- `disable-model-invocation: true` — user-only via `/skill-name`; excluded from LLM's available list
- `mode: true` — appears in "Mode Commands" section (top of list)

**Undocumented field:** `when_to_use` appears in source code — gets appended to description with " - " separator. Not in official docs; avoid in production until documented.

**Body best practices:**
- Under 5,000 words (~800 lines)
- Imperative language ("Analyze X") not second person
- Reference bundled files via `{baseDir}/scripts/...` — never hardcode paths
- Use progressive disclosure: core steps in SKILL.md, details in `references/`

## Resource Directories

```
my-skill/
├── SKILL.md          # Core prompt (required)
├── scripts/          # Python/Bash — Claude runs via Bash; only stdout enters context
├── references/       # Markdown docs — Claude reads via Read tool into context
└── assets/           # Templates, images — referenced by path only, never read into context
```

Key distinction: `references/` costs tokens (text loaded into context). `assets/` costs zero tokens (path only).

## Supply Chain Risk

Skills from untrusted sources are prompt injection vectors. The `Skill` tool has no sandboxing — a malicious SKILL.md with `Bash` in `allowed-tools` can execute arbitrary commands. Snyk ToxicSkills research found prompt injection in 36% of tested skills. Rule: treat skills like software packages. Always read SKILL.md and bundled scripts before installing.

## Skills vs Subagents vs Agents

| | Skills | Subagents | Agents |
|---|---|---|---|
| Context | Main conversation | Separate window | Separate window |
| Purpose | Prompt injection + context modification | Isolated task execution | Autonomous multi-step work |
| Token cost | ~1,500+ per invoke | Full context window | Full context window |
| Persistence | Temporary session shift | Isolated | Maintains own state |

Subagents don't inherit parent skills. Preload via `skills:` frontmatter in the subagent definition.

## Key Antipatterns (from source analysis)

- **Overly broad allowed-tools**: listing every tool defeats principle of least privilege and creates security risk
- **Vague description field**: Claude can't reliably match user intent to skills with generic descriptions
- **Hardcoded absolute paths**: breaks portability — use `{baseDir}` always
- **Monolithic SKILL.md**: embedding everything inflates token cost on every invoke; offload to `references/`
- **Relying on `when_to_use`**: undocumented field; could change or be removed

## Related Pages

- [[concepts/agent-skills]] — core concept page with SKILL.md schema, patterns, scopes
- [[concepts/indirect-prompt-injection]] — attack vector via malicious skill content
- [[concepts/agent-subagents]] — subagents and skill preloading
- [[concepts/claude-code-plugins]] — plugin system that namespaces and bundles skills
- [[summaries/top-8-claude-skills-uiux]] — architecture clarification + ToxicSkills supply chain risk
