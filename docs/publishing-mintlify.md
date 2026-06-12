# Publishing the wiki as a Mintlify site

The wiki is published to a hosted [Mintlify](https://mintlify.com) docs site. The generated
site lives in `docs-site/` and is produced from the wiki by a transpiler — **never edit
`docs-site/` by hand**; it is wiped and regenerated on every build.

- **Source of truth:** `wiki/*.md` (+ `ONBOARDING.md`, `GUIDE.md`, `docs/architecture.md`,
  `docs/workflows.md`).
- **Generator:** `claude-setup/scripts/build-docs-site.mjs`.
- **Scope:** concepts, patterns, systems, syntheses, comparisons, entities, and the guides.
  Per-source `summaries/` and the `mistakes/` system are excluded.

## What the build does

```bash
node claude-setup/scripts/build-docs-site.mjs
```

- Slims each page's frontmatter to `title` + `description` (Mintlify's fields).
- Rewrites `[[wikilink]]` / `[[wikilink|alias]]` into MDX links, **skipping code blocks** (the
  wiki contains bash `[[ ... ]]`). Links to excluded pages degrade to plain text.
- Escapes bare `<` and `{` in prose (MDX parses them as JSX otherwise).
- Embeds a local-graph side widget on every page (below).
- Generates `index.mdx` (landing) and `docs.json` (navigation).

## Graph widget

Every page carries a fixed bottom-right graph panel:

- **Nested pages** open on the **local graph** — the current node (highlighted with a ring) and
  its nearest wikilink neighbourhood (default depth 2).
- **The landing / root page** opens on the **whole-repo graph** (Depth: All).
- A **⚙ controls panel** (top-right of the widget) exposes sliders for node size, link width,
  label size, label opacity, and **depth**, plus a **directional-arrows** toggle.
- The panel is **draggable** by its header to anywhere on the page (defaults to the bottom-right
  corner); the chosen position is remembered across pages via `localStorage`.
- Click any node to navigate to that page; colours map to wiki section.

Implementation: a self-contained `<iframe srcDoc>` per page using
[`force-graph`](https://github.com/vasturiano/force-graph) pinned at `1.51.4` with Subresource
Integrity (no external hosting, no dependency on Mintlify custom-JS).

- **Nested pages embed only their bounded neighbourhood** — depth ≤ `NEIGH_DEPTH` (3), capped at
  `NEIGH_MAX` (44) nodes by closeness then degree; the depth slider ranges 1 → that cap.
- **The root page embeds the full graph** (the one place that pays for the whole dataset).
- **Performance:** the layout is pre-warmed (`warmupTicks`/`cooldownTicks`), and the render loop
  **pauses whenever the pointer is not over the widget** (`pauseAnimation` / `resumeAnimation`),
  so the fixed panel does not repaint during page scroll. Verified: 0 canvas redraws while idle,
  redraws only on hover/zoom/drag.

Node-size scaling (`sqrt(degree)`), defaults (`opt = {...}`), and the neighbourhood bounds all
live near the top of the `WIDGET_HTML` / `buildNeighborhood` block of the generator. `docs-site/`
is ~5 MB of MDX (plain text, compresses well).

## Preview locally

```bash
npm i -g mint          # one-time; needs Node >= 20.17
cd docs-site
mint dev               # http://localhost:3000
```

## Publish (hosted Mintlify)

Mintlify hosts by reading committed MDX from the repo. One-time connect, then push-to-deploy.

1. Create an account / org at <https://mintlify.com> (Dashboard).
2. **Install the Mintlify GitHub App** from the dashboard; grant it access to the `llm-wiki`
   repository only.
3. In **Git Settings**, set the **docs source path to `docs-site`** (the `docs.json` is not at
   repo root) and confirm the deploy branch (e.g. `main`).
4. Push. Every push to that branch auto-deploys.

> GitHub Enterprise with an IP allowlist: whitelist Mintlify's egress IP `54.242.90.151`.
> *(Dashboard specifics change — verify against current Mintlify docs.)*

## The publishing loop

```
edit wiki/*.md  →  node claude-setup/scripts/build-docs-site.mjs  →  commit wiki + docs-site  →  push  →  Mintlify deploys
```

Because the generated MDX must be committed for Mintlify to read it, regenerate and commit
`docs-site/` whenever wiki content changes. (Optionally wire the build into a pre-push hook.)
