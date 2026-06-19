# pi-headroom

Headroom context compression plugin for [oh-my-pi](https://omp.sh).

Compresses tool outputs before they reach the LLM. Falls back to basic truncation when Headroom returns no savings. The model can call `headroom_retrieve` to fetch full originals on demand.

## What's inside

| Piece | Purpose |
|---|---|
| `hooks/pre/headroom-compress.ts` | `tool_result` hook — compresses or truncates large tool outputs before the model sees them |
| `tools/headroom-retrieve/index.ts` | Custom tool — lets the model fetch original uncompressed content on demand |

## Install (local)

```bash
# 1. Install headroom-ai inside the plugin directory
cd pi-headroom
npm install

# 2. Install the plugin into omp (symlinks + watches for changes)
omp install ./pi-headroom

# 3. Verify it loaded
# The hook auto-discovers from ~/.omp/agent/hooks/pre/
# The tool auto-discovers from ~/.omp/agent/tools/headroom-retrieve/
```

## How it works

1. **After every tool call**, the `tool_result` hook checks if the output is large (> 2k chars).
2. **If large**, it tries Headroom compression first. If Headroom saves tokens, the compressed version is sent to the model.
3. **If Headroom returns no savings** (proxy not configured, content not compressible), it falls back to truncating after 50 lines and appending a retrieval hint.
4. **The model sees truncated/summarized output**. If it needs details, it calls `headroom_retrieve(chunkId)`.
5. **The tool fetches the original** from Headroom's CCR store (if available) or returns a not-found message.

## Configuration

Edit `hooks/pre/headroom-compress.ts` to tune:

- `COMPRESS_THRESHOLD_CHARS` — when to trigger compression (default: 2000)
- `DEFAULT_MODEL` — model identifier for Headroom's compressor router
- `MAX_LINES` — fallback truncation line count (default: 50)

## Test Results (omp v16.0.9)

| Feature | Status | Notes |
|---|---|---|
| Plugin install | ✅ | `omp install ./pi-headroom` works; symlinks + watches |
| `tool_result` hook | ✅ | Fires for all tool results; return value modifies what model sees |
| `headroom_retrieve` tool | ✅ | Registered and callable; returns 404 for unknown chunkIds |
| `context` hook | ❌ | `{ messages }` return contract ignored in omp 16.0.9 |
| Headroom compression | ⚠️ | Requires proxy in API-passthrough mode or cloud API key; fallback truncation works |
| Auto-discovery | ✅ | Hooks from `~/.omp/agent/hooks/pre/` and plugin both discovered |

### Verified end-to-end

```bash
# Truncation fallback tested with 32KB markdown file:
# Before: 501 lines, ~15k tokens
# After: 50 lines + "[... 451 lines truncated. Use headroom_retrieve to fetch full original if needed.]"
```

## Known Limitations

1. **omp 16.0.9 `context` hook**: The `{ messages }` return contract documented at omp.sh/docs/hooks does not actually replace the message array in this version. We use `tool_result` instead, which covers the bulk of token bloat (tool outputs).

2. **Headroom standalone compression**: The `HeadroomClient.compress()` method returns null metrics when pointing at a local `headroom proxy --port 8787`. The proxy is designed as an API passthrough (set `ANTHROPIC_BASE_URL=http://localhost:8787`), not a standalone compression service. For full Headroom compression, either:
   - Use the proxy in passthrough mode and skip this plugin entirely (headroom compresses transparently)
   - Get a Headroom cloud API key and pass it to `HeadroomClient({ apiKey: "..." })`

3. **CCR retrieval**: The `headroom_retrieve` tool calls `HeadroomClient.retrieve(hash)`. If the proxy doesn't have the hash in cache, it returns 404. This is expected for fallback-truncated content (no CCR hash generated).

## Troubleshooting

| Symptom | Fix |
|---|---|
| Hook not firing | Verify file is in `~/.omp/agent/hooks/pre/` (not nested deeper) |
| `headroom-ai` import fails | Run `npm install` inside the plugin directory |
| Tool not available | Verify `~/.omp/agent/tools/headroom-retrieve/index.ts` exists |
| No compression happening | Check if content exceeds `COMPRESS_THRESHOLD_CHARS`; verify proxy/API key config |

## Future Paths

- **(Z)** PR to `can1357/oh-my-pi` as an official plugin once `context` hook works
- **(AA)** Integrate into `commandr-omp-runner` bootstrap for automatic setup
- Investigate omp `context` hook support in newer versions

## License

MIT
