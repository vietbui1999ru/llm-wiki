---
title: "Codex Custom Instructions via AGENTS.md"
type: summary
tags: [agent-context-instructions, codex, openai, layering]
sources: ["Custom instructions with AGENTS.md – Codex.md"]
created: 2026-05-06
updated: 2026-05-06
---

# Codex Custom Instructions via AGENTS.md

How OpenAI Codex discovers and layers AGENTS.md files. Codex builds an instruction chain once per run (once per TUI session). The layering mechanism is more explicit and configurable than other tools.

---

## Discovery Precedence

1. **Global scope** (`~/.codex/` or `$CODEX_HOME`):
   - Reads `AGENTS.override.md` if it exists, otherwise `AGENTS.md`
   - Only one file at this level

2. **Project scope** (git root → current working directory):
   - For each directory along the path: checks `AGENTS.override.md`, then `AGENTS.md`, then `project_doc_fallback_filenames`
   - At most one file per directory

3. **Merge order**: concatenated root→CWD, joined by blank lines. Files closer to CWD appear later — **later wins** because they override earlier guidance.

---

## Key Mechanisms

**AGENTS.override.md**: A parallel file that overrides the regular AGENTS.md at that directory level without deleting it. Useful for temporary local overrides.

```bash
# Restore default after override
rm services/payments/AGENTS.override.md
```

**32 KiB combined limit**: `project_doc_max_bytes` defaults to 32768 bytes. Codex stops adding files when the combined chain hits this limit. Raise it in `~/.codex/config.toml`:

```toml
project_doc_max_bytes = 65536
```

**Fallback filenames**: Configure alternate instruction file names:

```toml
project_doc_fallback_filenames = ["TEAM_GUIDE.md", ".agents.md"]
```

Codex then checks each directory for: `AGENTS.override.md` → `AGENTS.md` → `TEAM_GUIDE.md` → `.agents.md`.

**CODEX_HOME profiles**: Run with a different home directory for project-specific automation:

```bash
CODEX_HOME=$(pwd)/.codex codex exec "List active instruction sources"
```

---

## Verification Commands

```bash
# See what instructions Codex loaded (from project root)
codex --ask-for-approval never "Summarize the current instructions."

# Check nested override
codex --cd services/payments --ask-for-approval never "Show which instruction files are active."
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Nothing loads | Empty file / wrong workspace root | Verify `codex status`, ensure file has content |
| Wrong guidance | AGENTS.override.md higher in tree | Find and rename/remove override |
| Fallback name ignored | Not in `project_doc_fallback_filenames` | Add to config, restart Codex |
| Instructions truncated | Hit 32 KiB limit | Raise `project_doc_max_bytes` or split files |
| Profile confusion | $CODEX_HOME set | Run `echo $CODEX_HOME` before launching |

---

## Related Pages

- [[entities/agents-md-format]] — the format this builds on
- [[summaries/agents-md-spec]] — cross-tool compatibility table
- [[concepts/agent-context-instructions]] — the pattern this implements
