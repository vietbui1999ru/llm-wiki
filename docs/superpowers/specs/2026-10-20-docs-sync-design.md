# docs-sync: refresh llm-wiki docs after dotfiles workflow changes

## Context

Dotfiles agent-workflow architecture (shared/skills, claude rules, scripts, pi config) has
churned heavily over the past weeks. llm-wiki documents that architecture in hand-written
guides (`docs/architecture.md`, `docs/workflows.md`, with 12 Mermaid diagrams) and wiki
pages (`wiki/systems/dotfiles-agent-harness-layout.md`, `wiki/entities/pi-agent.md`, ...).
Nothing links a dotfiles change to the docs that describe it, so they drift silently and the
Mintlify site (vietbui.mintlify.app, auto-deployed on push to llm-wiki main) goes stale.

Goal: one manually-run command that reads what changed in dotfiles since the last sync,
has `opencode-go/deepseek-v4.1-flash` rewrite affected docs (prose, workflow descriptions,
Mermaid diagrams, restructuring allowed), validates every rewrite, rebuilds `docs-site/`,
and pushes one commit to llm-wiki main. Fully unattended.

## Decisions (user)

- Trigger: manual, after a burst of changes. No cron, not wired into "lint the wiki".
- Output: commit pushed straight to llm-wiki `main`; no PR, no y/n pause.
- Mapping: self-growing manifest. Script auto-appends model-proposed entries for uncovered
  dotfiles paths; user only fixes wrong lines.
- Scope: llm-wiki guides + llm-wiki wiki pages. Dotfiles is read-only input, never edited.
- Home: `claude-setup/scripts/docs-sync.mjs` (Node, same runtime as build-docs-site.mjs).
- Model: deepseek-v4.1-flash only, for all content/diagram work.

## Calls made by me (check these)

- Baseline stored as `last_synced_sha` in the manifest; first run needs `--since <ref>`.
- Diff source: committed dotfiles `main` only (uncommitted work ignored); excludes
  `.claude/worktrees/**`, `docs/superpowers/**`, `*.bak`.
- pi runs as pure text-in/text-out:
  `pi -p --model opencode-go/deepseek-v4.1-flash:medium --no-tools --no-session
  --no-extensions --no-skills --no-context-files --no-mcp < /dev/null` (prompt via arg/file).
- Concurrency 3 pi calls at a time.
- `--dry-run` flag: everything except commit/push (needed for first verification).
- `pele-render` required at preflight (abort if missing). Today it is NOT on PATH — dotfiles
  PR #124 must land or `pele` be installed first.
- markdownlint via `npx --yes markdownlint-cli2@<pin matching CI action v17>`.
- Model never edits frontmatter; script owns `updated:`.

## Files

New:
- `claude-setup/docs-sync.json` — `dotfiles: ~/dotfiles`, `last_synced_sha`, and
  `entries: [{paths: [globs], docs: [llm-wiki paths]}]`. JSON, parsed with `JSON.parse`
  (no YAML library in the repo; a JSON document is also valid YAML). Seed ~15-25 entries by hand from
  recon (e.g. `shared/skills/delegate-pi/**` → `wiki/entities/pi-agent.md`, `docs/workflows.md`;
  `claude/.claude/rules/**` → `docs/architecture.md`, `wiki/concepts/model-tier-routing.md`;
  `scripts/{ac-run,floor-guard}` → `wiki/syntheses/spec-conformance-and-review-loop-options.md`).
- `claude-setup/scripts/docs-sync.mjs` — the script.
- `claude-setup/scripts/docs-sync.test.mjs` — `node --test` unit tests for pure functions.

Reused:
- `claude-setup/scripts/build-docs-site.mjs` (regenerates `docs-site/`; CI `docs-site-sync`
  in `.github/workflows/quality.yml` fails if not committed).
- Node 22 `path.matchesGlob` for manifest globs (no deps; repo has no package.json).

Modified:
- `log.md` (append entry per run), `index.md` (refresh one-line description of touched pages).
- `CLAUDE.md` — one line under Operations naming the command.

## Flow

1. **Preflight** — llm-wiki on `main`, clean tree, `git pull --ff-only`; `pi`, `pele-render`,
   `node` present; lockfile in `$TMPDIR`. Any failure: abort, nothing written.
2. **Range** — `git -C ~/dotfiles log/diff last_synced_sha..main`; changed paths minus
   excludes. Empty range: exit 0 "nothing to sync".
3. **Map** — glob-match paths to docs. Uncovered paths: one pi call with the path list +
   catalog of in-scope docs (`docs/*.md`, `GUIDE.md`, `wiki/{systems,entities,concepts,syntheses}`)
   returns JSON `{glob: [docs]}`; keep only entries whose docs exist and are in scope; append
   to manifest. Still-uncovered paths go into the report.
4. **Rewrite** — per affected doc: prompt = style rules (keep wikilinks/headings conventions,
   Mermaid allowed and may be added/restructured, no invented model names or numbers,
   `(training data — verify)` rule) + current body + relevant commit messages + diff hunks
   (truncated to a token budget). Model returns body between sentinel markers plus an
   `INDEX:` one-liner.
5. **Gate** (`acceptRewrite`, per doc; fail = keep original, log reason):
   - sentinels parsed, non-empty, actually changed;
   - every ```mermaid block renders via `pele-render`;
   - deletion cap (reject if >75% of original lines removed; raised from 60% because
     edited lines count as removed and restructuring is allowed);
   - shrink guard (reject if under 50% of the original's non-blank lines: likely truncation);
   - every `[[wikilink]]` resolves to an existing page.
6. **Bookkeeping** — wiki pages: set `updated:` today; replace that page's `index.md` line
   text with `INDEX:`; append `## [YYYY-MM-DD] docs-sync | dotfiles <old>..<new>` to
   `log.md` listing updated, skipped (with reason), and uncovered paths.
7. **Build + lint** — `node claude-setup/scripts/build-docs-site.mjs`; markdownlint on changed
   files; a page failing lint is reverted and site rebuilt.
8. **Ship** — bump `last_synced_sha`; stage by path (changed docs, docs-site/, log.md,
   index.md, manifest); one commit `docs-sync: dotfiles <old7>..<new7>`; `git push origin main`.
   Baseline only advances on successful push, so a failed run retries the same range.
   Undo a bad run: `git revert <sha>`.

## Implementation notes

- ~250-350 LOC total; build in ~50-LOC chunks (preflight/range, map, pi wrapper, gate,
  bookkeeping, ship). Per plan-handoff, dispatch to Pi after approval.
- Learning-mode contribution: user writes `acceptRewrite(original, rewritten)` gate policy
  (thresholds and which checks are hard vs soft) — the trade-off that most shapes safety.
- Seed manifest written by Claude from recon, reviewed in the diff.

## Verification

1. `node --test claude-setup/scripts/docs-sync.test.mjs` — glob mapping, sentinel parsing,
   deletion cap, wikilink check, frontmatter `updated:` bump.
2. Preflight negative: run with dirty tree / missing pele → aborts, `git status` unchanged.
3. `node claude-setup/scripts/docs-sync.mjs --since <sha ~2 weeks back> --dry-run` — inspect
   `git diff`, report, rendered Mermaid; confirm docs-site rebuilt and markdownlint clean.
4. CI-equivalent: `git diff --exit-code -- docs-site` after a rebuild is clean.
5. First real run without `--dry-run`; confirm quality.yml green and Mintlify deploy.
