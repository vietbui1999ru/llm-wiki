---
title: "diagrammer agent"
type: entity
tags: [subagents, mermaid, diagrams, system-design, mvp, documentation, pele, agent-harness]
sources: []
created: 2026-10-22
updated: 2026-10-22
---

# diagrammer agent

A subagent that designs technical Mermaid diagrams: MVP overviews, system and architecture design, data flow, workflows, state machines, data models and migration timelines. It exists so diagram work for specs, wiki pages, the docs site and slides gets the same grounding and style every time, instead of being improvised inline by whichever agent is writing the page.

Added in dotfiles PR #171 (2026-10-22). First intended job: the MVP presentation section of `SPEC-HARNESS-MIGRATION.md`.

## Where it lives

The same instruction body is defined once per harness, following the `firecrawl` agent pattern. Each copy has its own frontmatter.

| Harness | Definition in `~/dotfiles` | How it reaches the harness |
|---|---|---|
| Claude Code | `claude/.claude/agents/diagrammer.md` (source copy; Sonnet, medium effort, preloads the `pele` skill) | stowed into `~/.claude/agents` |
| Pi | `pi/.pi/agent/agents/diagrammer.md` (Pi default model) | stowed into `~/.pi/agent/agents` |
| OpenCode | `opencode/.config/opencode/agents/diagrammer.md` (edits allowed; shell limited to `pele-render`, `printf`, `rg`, `fd`, `ls`) | stowed into `~/.config/opencode/agents` |
| Codex | `codex/.codex/agents/diagrammer.toml` | copied by `scripts/sync-agent-rules.sh` (Codex cannot spawn a symlinked agent) |

The agent-harness repo sees all four through its `src/agents/*` links, so it needs no change. When the migration gives rules and skills a single home (step 2 in `SPEC-HARNESS-MIGRATION.md` at the wiki root), these four copies are a candidate to generate from one source. Until then, edit the Claude copy and regenerate the others so the bodies stay identical.

Not in `~/.agents`: that folder holds cross-harness **skills** only. The `pele` skill is linked there, which is how the non-Claude harnesses get the renderer.

## How it works

```mermaid
flowchart LR
  parent[Parent agent] -- "question + sources" --> dg([diagrammer])
  dg -- reads --> src[(spec, code, notes)]
  dg --> pick{target?}
  pick -- markdown page --> fence["mermaid fence in the page"]
  pick -- slides or export --> files[(".mmd + .svg")]
  fence -. validate .-> pele[[pele-render]]
  files -- render --> pele
  pele -- "exit 1: fix and retry" --> dg
  dg -- "report + open questions" --> parent
```

1. **Ground it.** Every node and edge must come from the source material. Unclear facts are marked `?` and reported, never invented.
2. **Pick the question, then the type.** Wiring → `flowchart LR` with subgraphs per boundary; interactions over time → `sequenceDiagram`; lifecycle → `stateDiagram-v2`; data model → `erDiagram`; outsider view → C4; phases → `timeline`/`gantt`; migrations → before/after flowcharts with the same node ids.
3. **Size it.** About 9 nodes per diagram (7 for slides); larger systems become an overview plus detail diagrams.
4. **Write it where it will be read.** Markdown targets get a `mermaid` fence in the page, because Mintlify, GitHub and Obsidian render fences themselves. pele only validates the fence. Slides and exports get `.mmd` + `.svg` files.
5. **Check it** against the grounded list, and flag newer diagram types for a visual check on the published page.

House style (in the agent file, meant to be tuned): short stable node ids reused across a set; edge labels that name what moves; shapes with meaning (cylinder = store, stadium = daemon, subroutine = external); dotted edges for optional or set-up-only links; at most three `classDef` states; no hardcoded themes.

## Mermaid on the docs site

- `claude-setup/scripts/build-docs-site.mjs` copies `mermaid` fences into the `.mdx` output unchanged, and Mintlify renders them in the browser with zoom and pan controls. Fences accept `placement="top-left"` and `actions={false}`.
- So the wiki keeps Mermaid **source** in pages. It does not commit pre-rendered SVGs for pages, which would lose zoom and pan and could look different from GitHub and Obsidian (pele has its own layout engine).
- pele targets Mermaid 12.1 syntax and Mintlify ships its own Mermaid build. A fence pele accepts almost always renders on the site, but check newer types such as `architecture-beta` once they are published.

## Related pages

- [[entities/pele]]: the renderer and validator
- [[concepts/agent-subagents]]: subagent format and scopes
- [[systems/dotfiles-agent-harness-layout]]: where agents and skills are linked
- [[systems/system-design-process]]
