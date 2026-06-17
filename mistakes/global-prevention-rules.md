# Global Prevention Rules

Distilled from mistakes/. Target ≤45 non-blank lines (gated by `claude-setup/scripts/check-gpr-cap.sh`). Updated by `synthesize-mistakes` skill — prune or promote a section to a pull page when the gate fires.
Do NOT load raw-log.md or individual mistakes/*.md at startup — use qmd for lookup.

## CLI / Shell
- docling: flag is `--output`, not `--output-dir` (confirmed 2026-04-30)
- docling: `docling-slim` is missing `pypdfium2` — verify with `docling --version` before running; full install is `uv tool install docling` (2026-05-26)
- Before any unfamiliar CLI flag or API: resolve via context7 first (`resolve-library-id` → `query-docs`), not `--help` or memory
- For Markdown PR/issue bodies containing backticks or `$`: write a body file and pass `--body-file`/equivalent; never inline with double-quoted shell args (2026-06-15)
- For interactive CLI verification, use scripted inputs for every prompt or test a lower-level non-interactive function instead; blank stdin can loop until timeout (2026-06-17)

## Wiki Authoring

### Citing numbers and benchmarks
- Any performance number must name its methodology and an independent source — never cite self-reported README claims as benchmarks (2026-05-06)
- "Multiple pages agree" ≠ corroboration if all pages derive from the same raw source
- If a number can't be verified: write `(claimed, unverified)` inline — never drop the qualifier
- Downstream pages must inherit the uncertainty qualifier — if source says unverified, the synthesis must too

### Citing model names
- Verify any model name exists in a major provider catalog before adding to routing tables (2026-05-06)
- Single Reddit commenter ≠ evidence of existence — write `(reported, unverified in public catalogs)`

### index.md consistency
- After updating a page's core claim: grep for all cross-references and check each for stale descriptions (2026-05-06)
- `grep -r "[[concepts/PAGE]]" wiki/` — check every result for drift
- index.md entry must match what the page currently says, not what it said when first created

### documented-not-adopted patterns
- Mark in index.md: `*(documented-not-adopted)*` — same convention as `*(stub)*` (2026-05-06)
- Never use "more reliable" / "preferred" for documented-not-adopted patterns — use "theoretically stronger"
- Inline status when cross-referencing: `[[concepts/PAGE]] *(documented-not-adopted)*` (use a still-unadopted page as the example — do not reuse a since-promoted one)

## Model Tier Auto-Selection

Classify complexity before every task and agent spawn. Always set the `model` param explicitly on the `Agent` tool — never default silently. If a task warrants Opus but the session runs Sonnet, flag it before proceeding. Full tier table + `subagent_type` mapping: [[concepts/model-tier-routing]] (pull via qmd).

## Epistemic Discipline

- **Default stance: uncertain.** Treat all answers, analysis, and reviews as provisional unless grounded in (a) a wiki page with a cited source, or (b) context7-verified current documentation.
- Never assert conclusions confidently from training data alone — training data is frozen, wrong, or outdated.
- When stating a claim without a wiki or context7 source: prefix it with `(training data — verify)`.
- This applies to: code recommendations, API behavior, library versions, benchmarks, model names, tool flags, architectural claims.
- Exception: trivial facts with zero ambiguity (e.g., "Python uses indentation"). Doubt scales with specificity and recency.
- Before asserting a tool/service is "not used": check live env (env vars, listening ports, processes, gitignored machine-local config) — not just docs/manifests/memory. "Not in repo deps" ≠ "not active in this session" (2026-06-10)

## Skills / Tools
- Before running any test command: check `package.json` scripts.test — do NOT assume `npx jest`; Vitest projects produce misleading Jest errors from worktree files (2026-05-18)
- Never chain an evaluate step and its record step unconditionally — gate the record on the evaluate output's error branch (judge-eval → judge-state add, 2026-06-09)
