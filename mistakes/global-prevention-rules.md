# Global Prevention Rules

Distilled from mistakes/. Max 30 lines. Updated by `synthesize-mistakes` skill.
Do NOT load raw-log.md or individual mistakes/*.md at startup — use qmd for lookup.

## CLI / Shell
- docling: flag is `--output`, not `--output-dir` (confirmed 2026-04-30)
- Before any unfamiliar CLI flag or API: resolve via context7 first (`resolve-library-id` → `query-docs`), not `--help` or memory

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
- Inline status when cross-referencing: `[[concepts/instinct-clustering]] *(documented-not-adopted)*`

## Skills / Tools
- (empty — will populate from capture-mistake entries)
