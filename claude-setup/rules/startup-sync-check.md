# Startup: Tier 0 Sync Check

After session state check, look for pending Tier 0 drift flags:

```bash
grep -c "^status: pending" ~/repos/llm-wiki/pending-sync.md 2>/dev/null || echo "0"
```

| Result | Action |
|---|---|
| `0` or file missing | Silent skip. |
| `1` or more | Surface pending entries, prompt to resolve. |

When pending entries exist, read the full file:
```bash
cat ~/repos/llm-wiki/pending-sync.md
```

Parse every block (delimited by `---`) where `status: pending`. For each, surface:

> **Tier 0 drift: N wiki page(s) changed that are cited in your always-loaded rules.**
> Pending:
> - `[[wikilink]]` in `tier0_file` (changed: `wiki_page`)
>
> Run `/sync-tier0` to review and patch. ~2 min per entry.

**Override:** user says "skip tier0 sync" or "ignore drift" → silent skip for this session.
