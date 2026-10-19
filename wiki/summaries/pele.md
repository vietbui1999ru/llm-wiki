---
title: "pele: Mermaid diagrams to SVG (README)"
type: summary
tags: [pele, mermaid, diagrams, svg, system-design, presentations, javascript, obsidian]
sources: ["obsidianmdpele Renders Mermaid diagrams faster than you'd run from a volcano! 🌋.md"]
created: 2026-10-19
updated: 2026-10-19
---

# pele: Mermaid diagrams to SVG

GitHub README of `obsidianmd/pele` (MIT), captured 2026-10-19. Short source (about 3 KB). API details below
the README level come from the project's docs via context7 (`/obsidianmd/pele`, pages `api.md` and
`theming.md`), and the install facts from installing `pele@1.6.0` in this setup. See [[entities/pele]] for the
identity page and how it is wired into the agent setup.

## Problem

Mermaid's reference renderer (and `mermaid-cli`/`mmdc`, which drives it in headless Chromium) needs a browser
DOM to lay out and measure text. That makes server-side or agent-side rendering heavy. pele is a separate
implementation that turns Mermaid text into SVG synchronously, with no runtime dependencies.

## What the README claims

- Renders every diagram type built into Mermaid 12.1.0, with its own layout and visual style (so output is
  **not** pixel-identical to Mermaid's).
- Small, synchronous, zero runtime dependencies. "Faster than Mermaid" is implied by the tagline; the repo has
  an `npm run bench` script but the README publishes no numbers, so speed is `(claimed, unverified)`.
- Parsers are tested against Mermaid's own parser specs and with differential fuzzing (self-reported).
- Security: escapes diagram text, filters links and styles, limits source and output size. Docs give the
  defaults: 50,000-character source limit, 4,000,000-character SVG limit, 5,000 flowchart edges, links limited
  to http/https/mailto/tel.

## API

- `render(source, options) -> { svg, width, height, type, links }`: pure function, works in Node. Text is
  measured with a canvas in browsers and a built-in width table elsewhere.
- `mount(element, source)`: browser only. It reads fonts from CSS and re-renders when the container width changes.
- `pele/core` with `register(diagram)` for a smaller bundle, and `pele/lazy` `renderAsync()` to load diagram types on demand.
- CDN global build: `pele.mount(el, el.textContent)` over every `pre.mermaid`.
- Narrow screens: `maxWidth` lets layouts adapt; below `directionBreakpoint` (640 px) supported diagrams switch
  to a vertical layout unless `autoDirection: false`.
- Errors throw `PeleError` with the Mermaid-style line message (observed when testing).

## Theming

CSS variables on `.pele` or a parent: `--pele-bg`, `--pele-fg`, `--pele-muted`, `--pele-line`,
`--pele-surface`, `--pele-surface-alt`, `--pele-border`, `--pele-accent`, `--pele-font`, `--pele-radius`, and
`--pele-series-1..8` for charts. Colours change without a re-render. Observed: the SVG's inline style carries
fallbacks (`var(--pele-bg,#fff)`), so a standalone `.svg` file renders with default colours.

## Limitations

- Own layout engine: complex diagrams may lay out differently from mermaid.live, and Mermaid features beyond
  12.1.0 syntax are not covered.
- No CLI in the package (no `bin`); a wrapper script is needed for file-to-file rendering.
- Node needs `>=20` (from `package.json engines`).

## Wiki connections

- [[entities/pele]]: setup and when to use it vs `mmdc` or Excalidraw.
- [[systems/system-design-process]]: diagrams are the deliverable of most design steps there.
