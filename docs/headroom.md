# Headroom: one proxy, and where it actually saves tokens

Headroom is a context-optimization proxy already installed on this machine (`headroom 0.24.0`, uv tool).
It sits between a client and the provider, compressing context and stabilizing prompt prefixes before
the request goes upstream. This page records what it can and cannot save here, and how the wiki's own
scripts use it.

Decision summary:

| Path | Headroom helps? | Why |
|---|---|---|
| Agent harness traffic (Claude Code, Codex, Pi) | **yes, the most** | long tool outputs and multi-turn history are exactly what it compresses |
| `wiki-chat` / `wiki_mcp` synthesis | **yes, some** | retrieved graph context is prose, and the query is the expensive half of RAG |
| `wiki-index` extraction | **no** | the prompt *is* the content being stored in the graph; compressing it corrupts entities |
| Embeddings, graph traversal, qmd | **no** | all local, zero token cost already |

The indexer therefore routes through the proxy with `x-headroom-bypass: true` by default: it gains
observability and session affinity, not compression. Set `WIKI_PROXY_COMPRESS_INDEX=1` to override,
but expect extraction quality to drop.

## One address for every agent

A single proxy process serves Anthropic, OpenAI-shaped and OpenCode Go traffic because it routes by
path and auth shape, not by client.

Verified on 0.24.0 (smoke-tested against the real endpoints; a dummy-key request through the proxy
returns the upstream's own error byte for byte):

| Client | Base URL | Upstream the proxy picks |
|---|---|---|
| Claude Code | `http://127.0.0.1:8787` (`ANTHROPIC_BASE_URL`) | `api.anthropic.com` |
| Codex CLI (ChatGPT subscription auth) | `http://127.0.0.1:8787` | `chatgpt.com/backend-api/codex` |
| Pi `opencode-go`, `wiki-index/chat/mcp` | `http://127.0.0.1:8787/v1` (`OPENAI_BASE_URL`) | `OPENAI_TARGET_API_URL` |

Start the proxy with the OpenAI target pointed at OpenCode Go, since Codex's subscription traffic is
routed to `chatgpt.com` by auth shape and never consults that setting:

```bash
OPENAI_TARGET_API_URL=https://opencode.ai/zen/go/v1 headroom proxy --port 8787
```

Caveat found by probing: `/v1/responses` only branches to `chatgpt.com` when the Authorization header
is a ChatGPT session token. A Codex install using a plain `OPENAI_API_KEY` would also be sent to the
OpenCode endpoint, so do not run both Codex auth modes against one proxy.

Client wiring:

```bash
# Claude Code — durable: ~/.claude/settings.json
"env": { "ANTHROPIC_BASE_URL": "http://127.0.0.1:8787" }

# Pi — ~/.pi/agent/models.json, provider-level only, keeps the built-in model catalog
{ "providers": { "opencode-go": { "baseUrl": "http://127.0.0.1:8787/v1" } } }

# wiki scripts — .env or shell
WIKI_LLM_PROXY_URL=http://127.0.0.1:8787/v1
```

## Monitoring

One address, one set of numbers:

```bash
curl -s http://127.0.0.1:8787/stats | jq '.requests, .savings, .cost'   # counters, by_provider/by_stack
curl -s http://127.0.0.1:8787/metrics                                    # Prometheus
curl -s http://127.0.0.1:8787/stats-history                              # durable history
headroom perf                                                            # analyze the proxy logs
```

The wiki scripts tag every request so traffic is attributable per consumer: `x-headroom-stack` is
`llm_wiki_index`, `llm_wiki_chat` or `llm_wiki_mcp`, and `x-headroom-session-id` carries
`OPENCODE_LIGHTRAG_SESSION` (default `wiki-index` / `wiki-chat` / `wiki-mcp`).

The stack slug must match `^[a-z][a-z0-9_]{0,63}$` — underscores, no hyphens. A hyphenated value is
silently dropped and the request lands unattributed in `/stats`, which is why these use underscores
(verified: `llm_wiki_index` appears in `requests.by_stack`; `llm-wiki-index` does not).

Those two headers are not cosmetic for OpenCode Go. The endpoint refuses requests without
`x-opencode-session` (`MissingSessionID`) and uses the value for routing and prefix-cache affinity, so
the scripts send a **stable** id. It used to be `f"...-{os.getpid()}"`, which put every run in a fresh
namespace and gave the prefix cache nothing to hit.

## Prompt caching: what the wiki controls

Prefix caching is worth more than compression on the extraction path, and the levers are local:

- **Stable session id** — done above.
- **Stable content** — entities only cost tokens when they are re-extracted. The index manifest now
  keys on a SHA-256 of the page instead of its mtime, so a checkout, clone or worktree switch (which
  rewrites mtimes for unchanged files) no longer re-extracts the whole wiki. `wiki-index --status`
  reports what is actually changed.
- **Stable prompt prefix** — `wiki_chunking_func` prepends the same graph-structure block before the
  page body on every chunk of a page, so the extractor's prompt starts with a repeated prefix.
- **Response cache** — LightRAG's own `kv_store_llm_response_cache.json` (56 MB, 3400 records here)
  already deduplicates repeated extraction calls; keep it when reusing a work dir.

## What to change only with the eval gate

These are the remaining token levers, all on the extraction or retrieval-parameter side. Each one
changes what the graph contains or what the synthesiser sees, so run the gate first
(`docs/retrieval-eval.md`) rather than tuning by feel:

| Lever | Default | Effect |
|---|---|---|
| `entity_extract_max_gleaning` | `1` (LightRAG default) | a second extraction round per chunk; `0` removes roughly half the extraction calls |
| `chunk_token_size` / `chunk_overlap_token_size` | `800` / `64` | bigger chunks mean fewer calls and more tokens per call |
| `summary_max_tokens` | `1200` | caps merged entity/relation descriptions; lower means a leaner graph and smaller query context |
| `related_chunk_number` | `5` | chunks pulled per entity/relation at query time |
| `chunk_top_k` / `max_total_tokens` | `20` / `30000` | size of the synthesis context, the main per-query cost |

`wiki-index` and `wiki-mcp`/`wiki-chat` set `top_k=20` and `cosine_better_than_threshold=0.3`
deliberately; anything below that needs a baseline run to prove it did not cost recall.

## Why not LLMLingua-style compression here

A dedicated prompt compressor (LLMLingua, Kompress) is what Headroom already runs for prose, and it is
the right shape for agent traffic. For this wiki it is the wrong tool on the write path and a marginal
one on the read path, because:

- Extraction prompts must stay verbatim; anything dropped is missing from the graph permanently.
- Retrieved wiki chunks are already dense, cross-linked prose written for this exact purpose. Dropping
  tokens there trades answer quality for a saving that the response cache and the context caps above
  capture more safely.
- The cheapest large win is not compression at all: it is not re-extracting pages that did not change.

Measure before believing either claim: `qmd cleanup` frees index space but nothing in tokens, and the
retrieval eval is the only thing here that can tell a real saving from a quality regression.
