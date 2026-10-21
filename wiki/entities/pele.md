---
title: "pele"
type: entity
tags: [pele, mermaid, diagrams, svg, system-design, presentations, agent-skills, javascript]
sources: ["obsidianmdpele Renders Mermaid diagrams faster than you'd run from a volcano! 🌋.md"]
created: 2026-10-19
updated: 2026-10-22
---

# pele

Mermaid-to-SVG renderer from Obsidian (`obsidianmd/pele`, npm `pele`, MIT, docs at pele.run). Synchronous,
zero runtime dependencies, Mermaid 12.1.0 syntax with its own layout and style, themed by CSS variables.
Source summary: [[summaries/pele]].

## Facts

| | |
|---|---|
| Kind | JavaScript library (ESM). No CLI binary in the package. |
| Version used here | 1.6.0 (latest on npm, 2026-10-19), Node `>=20` |
| Core API | `render(text, options) -> { svg, width, height, type }`; browser `mount(el, text)` |
| Output | Standalone SVG with inline colour fallbacks; restyle via `--pele-*` CSS variables without re-rendering |
| Speed | "Faster than Mermaid" `(claimed, unverified)`: no published benchmark |

## In this setup

Installed as the `pele` skill in `~/dotfiles/shared/skills/pele/` (dotfiles PR #124, draft as of 2026-10-19):

- The folder owns its pinned dependency (`package.json` + committed `package-lock.json`), so every machine
  gets the same version without a global npm install.
- `render.mjs` wraps `render()` as `pele-render [in.mmd|-] [-o out.svg] [--max-width N] [--padding N]`.
  Exit codes: 1 for a Mermaid error, 2 for bad arguments.
- `scripts/bootstrap-dirs.sh` runs `npm ci` there when the lock is newer than `node_modules`, links
  `~/.local/bin/pele-render`, and links the skill into `~/.agents/skills` (Codex, OpenCode, Pi) and
  `~/.claude/skills`. Ansible runs bootstrap, and the mise role supplies node, so a new machine needs no extra step.
- Why not the alternatives: a global `npm i -g pele` or mise `npm:pele` installs no runnable command, and
  `npx -p pele` downloads again on each use and is not pinned.

## When to use which diagram tool

| Need | Tool |
|---|---|
| Diagram inside a markdown page (wiki, docs site, README, spec) | A `mermaid` fence in the page; Mintlify, GitHub and Obsidian render it natively. Validate it with `pele-render` (stdin, exit 1 on a parse error). |
| Standalone diagram file (slides, `<img>`, export) | pele (`pele-render x.mmd -o x.svg`) |
| Designing the diagram itself | the [[entities/diagrammer-agent]] subagent, in any harness |
| Neovim inline preview | none: `mmdc` was removed (not installed as of 2026-10-22) and nothing replaces it |
| Freeform layout, whiteboard, hand-drawn slide deck | Excalidraw MCP |

The docs site does not need pele. `build-docs-site.mjs` passes `mermaid` fences through to `.mdx`, and Mintlify
renders them client-side with zoom and pan. Pre-rendering pages with pele would lose that and use pele's own
layout instead of Mermaid's. pele targets Mermaid 12.1; Mintlify ships its own Mermaid build, so check newer
types such as `architecture-beta` on the published page.

Diagram type per question, for system design: components and links → `flowchart LR` or `architecture-beta`;
calls over time → `sequenceDiagram`; context for non-engineers → `C4Context`; entity lifecycle →
`stateDiagram-v2`; data model → `erDiagram`. All four of flowchart, sequence, architecture-beta and C4Context
were rendered and visually checked on 2026-10-19.

For slides: prefer left-to-right layouts and roughly 7 nodes per diagram. Pass `--max-width` only when the target
is narrow, because below 640 px pele switches supported diagrams to a vertical layout.

## Related pages

- [[entities/diagrammer-agent]]: the subagent that designs diagrams and validates them with pele
- [[systems/system-design-process]]
- [[systems/dotfiles-agent-harness-layout]]: where shared skills are linked
