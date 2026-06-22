---
name: sync-tier0
description: Resolve pending Tier 0 drift entries. Reads each pending entry from pending-sync.md, compares the current wiki page against the Tier 0 claim that cites it, proposes a targeted replacement, applies it after approval, and marks the entry resolved. Invoke when the startup check surfaces pending entries, or when the user says "sync tier0" or "resolve drift".
allowed-tools: "Bash,Read,Edit"
model: sonnet
---

# sync-tier0 — Tier 0 Drift Resolution

## Step 1: Read all pending entries

```bash
cat ~/repos/llm-wiki/pending-sync.md
```

Parse every block (delimited by `---`) where `status: pending`. For each extract:
- `wiki_page:` — repo-relative path (e.g. `wiki/concepts/context-degradation.md`)
- `tier0_file:` — repo-relative path (e.g. `claude-setup/rules/applied-ai.md`)
- `wikilink:` — exact string (e.g. `[[concepts/context-degradation]]`)
- `timestamp:` — when drift was detected

If no pending entries, print: "No pending Tier 0 drift entries." and stop.

## Step 2: For each pending entry (one at a time)

### 2a — Read the current wiki page

```bash
cat ~/repos/llm-wiki/<wiki_page>
```

Identify the page's current **core claim** — the primary recommendation, heuristic, or
threshold it asserts. This is what the Tier 0 distillation is supposed to capture.

### 2b — Find the Tier 0 claim

Use `-F` (fixed strings) to match literal `[[` and `]]`:

```bash
grep -nF '<wikilink>' ~/repos/llm-wiki/<tier0_file>
```

Read enough surrounding context (typically 1–3 lines) to see the full claim. The claim
is the sentence or bullet containing the wikilink.

### 2c — Assess drift

Compare:
- Wiki page current core claim (Step 2a)
- Tier 0 claim about it (Step 2b)

Classify as:
- **No drift** — consistent. Mark resolved without editing, skip to Step 3.
- **Stale detail** — a specific threshold, behavior, or recommendation has changed.
- **Stale framing** — the page's primary emphasis or recommendation has shifted.

### 2d — Propose replacement (drift cases only)

Formulate a replacement for the specific sentence/bullet containing the wikilink.

Rules:
- Keep the `[[wikilink]]` in place — never remove it
- Match the surrounding formatting (bullet, bold prefix, inline style)
- Stay within 1–2 sentences — Tier 0 files are always-loaded, not reference docs
- Change only what drifted — do not touch adjacent claims

Present to the user:
```
Proposed change to <tier0_file>:

BEFORE:
  <exact current line(s)>

AFTER:
  <proposed replacement>

Reason: <one sentence — what specifically drifted on the wiki page>
```

**Wait for explicit user confirmation before editing.** Do not auto-apply.

### 2e — Apply the edit (after confirmation)

Use the Edit tool on the Tier 0 file. Use the exact current line(s) as `old_string`
(must be unique in the file). Do not touch other content.

## Step 3: Mark entry resolved

For each processed entry (edited or confirmed no-drift), update `pending-sync.md`.

Use the Edit tool. The `old_string` must include the full entry block starting from its
`---` separator and the unique timestamp line to avoid matching the wrong entry:

old_string (example):
```
---
timestamp: 2026-06-22T14:03:11Z
wiki_page: wiki/concepts/context-degradation.md
tier0_file: claude-setup/rules/applied-ai.md
wikilink: [[concepts/context-degradation]]
status: pending
```

new_string: same block, replace `status: pending` with:
```
status: resolved
resolved_at: <current UTC timestamp YYYY-MM-DDTHH:MM:SSZ>
```

Get current UTC timestamp:
```bash
date -u +%Y-%m-%dT%H:%M:%SZ
```

## Step 4: Report and log

After processing all entries:
```
sync-tier0 complete:
  N entries processed — M edits applied, K confirmed no-drift
  pending-sync.md updated.
```

Append to `~/repos/llm-wiki/log.md`:
```
## [YYYY-MM-DD] sync-tier0 | N entries resolved (M edits, K no-drift)
```
