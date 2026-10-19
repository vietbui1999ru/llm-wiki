---
title: "pele"
type: entity
tags: [pele, mermaid, diagrams, svg, system-design, presentations, agent-skills, javascript]
sources: ["obsidianmdpele Renders Mermaid diagrams faster than you'd run from a volcano! 🌋.md"]
created: 2026-10-19
updated: 2026-10-19
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
| Agent-written diagram as a file (design docs, wiki, slides) | pele (`pele-render`) |
| Neovim inline preview (snacks.image, diagram.nvim) | `mermaid-cli` / `mmdc` (Brewfile), which matches Mermaid's own rendering exactly |
| Freeform layout, whiteboard, hand-drawn slide deck | Excalidraw MCP |

Diagram type per question, for system design: components and links → `flowchart LR` or `architecture-beta`;
calls over time → `sequenceDiagram`; context for non-engineers → `C4Context`; entity lifecycle →
`stateDiagram-v2`; data model → `erDiagram`. All four of flowchart, sequence, architecture-beta and C4Context
were rendered and visually checked on 2026-10-19.

For slides: prefer left-to-right layouts and roughly 7 nodes per diagram. Pass `--max-width` only when the target
is narrow, because below 640 px pele switches supported diagrams to a vertical layout.

## Related pages

- [[systems/system-design-process]]
- [[systems/dotfiles-agent-harness-layout]]: where shared skills are linked
