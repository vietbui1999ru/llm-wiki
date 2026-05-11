---
title: "Local Wiki Q&A: Current State and RAG Upgrade Path"
type: synthesis
tags: [rag, local-llm, ollama, qmd, tui, future-development]
sources: []
created: 2026-05-11
updated: 2026-05-11
---

# Local Wiki Q&A: Current State and RAG Upgrade Path

> **Future development note.** This page captures the current `wiki-chat` implementation and the full RAG migration path. Pick up from here when revisiting local RAG.

---

## What's built (2026-05-11)

**Tool:** `~/.local/bin/wiki-chat` — Python TUI, runs from anywhere on the machine.

**Usage:**
```bash
wiki-chat                        # interactive Q&A
wiki-chat --model gemma3:12b     # better quality
wiki-chat --top-n 8              # more pages per query
```

**Prompt commands:**
- `/search <terms>` — show matched pages without synthesis
- `/model <name>` — switch model mid-session
- `q` — quit

**Dependencies:** `pip install ollama rich prompt_toolkit` (already installed)

**Config constants** (edit the script to change):
| Constant | Default | Purpose |
|---|---|---|
| `WIKI_DIR` | `~/repos/llm-wiki` | Wiki root |
| `DEFAULT_MODEL` | `gemma4:e4b` | Ollama model |
| `MIN_SCORE` | `0.4` | qmd retrieval threshold |
| `TOP_N` | `5` | Max pages per query |
| `MAX_CHARS` | `4000` | Per-page context trim |

### How it works

```
query → qmd CLI (BM25 + vector hybrid) → top-N wiki/wiki/ pages → ollama synthesis → rich TUI
```

qmd output format: `#docid,score,qmd://wiki/wiki/concepts/foo.md,"context label"`

The script filters to `qmd://wiki/wiki/` paths only, skipping `raw/`, `index.md`, and `log.md`.

### qmd index maintenance

The index needs manual updates when wiki pages are added:

```bash
cd ~/repos/llm-wiki
qmd update          # re-index new/changed files
qmd embed           # regenerate vectors (runs embeddinggemma-300M locally)
```

The index was 20 days stale when wiki-chat was built — 349 new pages were missing. Add `qmd update && qmd embed` to the ingest flow or run it periodically.

---

## Why the current approach works at this scale

Per [[concepts/contextual-retrieval]]: the classic RAG chunking problem is decontextualized fragments — chunks that lose provenance when split from their source. The wiki is structured with one concept per page (CLAUDE.md rule), so each page is already a focused, self-contained chunk. No chunking needed.

Per [[entities/qmd]]: qmd already does BM25 + vector hybrid — the full retrieval pipeline. The only missing piece was synthesis, which ollama provides.

**When this breaks down:** pages grow past ~500 lines, or the wiki exceeds ~500 pages. At that point, whole-page retrieval starts pulling in too much noise per page and page-level search precision drops.

---

## RAG upgrade path

### Level 1 — Current (qmd + ollama)
- Whole-page retrieval via qmd
- `wiki-chat` TUI
- Works for wiki < ~300 pages with focused pages
- No additional dependencies

### Level 2 — Section chunking (when pages get long)

Split pages at H2 (`##`) headers. Prepend the page's frontmatter YAML as context to each chunk before indexing. This is [[concepts/contextual-retrieval]] applied to markdown.

```python
import re, yaml

def chunk_page(path: Path) -> list[dict]:
    text = path.read_text()
    # extract frontmatter
    fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    fm = fm_match.group(1) if fm_match else ""
    body = text[fm_match.end():] if fm_match else text
    # split at H2 headers
    sections = re.split(r"(?=^## )", body, flags=re.MULTILINE)
    return [{"context": fm, "content": s.strip(), "source": str(path)} for s in sections if s.strip()]
```

Each chunk = frontmatter + section. Index these instead of whole pages.

**Trigger:** when `/search <terms>` returns pages that are clearly not fully relevant (the matched page has a section that's relevant but also much unrelated content).

### Level 3 — Qdrant + local embeddings (scale)

Replace qmd's internal vector store with Qdrant. Use `nomic-embed-text` (via ollama, free, local) for consistent embeddings between indexing and query.

```bash
docker run -d -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant
ollama pull nomic-embed-text
```

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import ollama

client = QdrantClient("localhost", port=6333)
# embed at index time:
vec = ollama.embeddings(model="nomic-embed-text", prompt=chunk_text)["embedding"]
# embed at query time:
query_vec = ollama.embeddings(model="nomic-embed-text", prompt=query)["embedding"]
# vector search:
hits = client.search("wiki", query_vector=query_vec, limit=20)
```

Retain BM25 via qmd (or switch to Whoosh/tantivy for pure Python). Merge results with RRF (Reciprocal Rank Fusion):

```python
def rrf(bm25_hits, vec_hits, k=60):
    scores = {}
    for rank, doc in enumerate(bm25_hits):
        scores[doc.id] = scores.get(doc.id, 0) + 1 / (k + rank + 1)
    for rank, doc in enumerate(vec_hits):
        scores[doc.id] = scores.get(doc.id, 0) + 1 / (k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)
```

**Trigger:** wiki > 500 pages, or need metadata filtering (by type, tag, date range).

### Level 4 — Reranking (quality over latency)

After RRF merge, pass top 20 candidates through a cross-encoder reranker, then send top 5 to ollama.

```bash
pip install sentence-transformers
```

```python
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("BAAI/bge-reranker-base")  # ~280MB, runs on CPU
pairs = [(query, doc.content) for doc in top_20]
scores = reranker.predict(pairs)
top_5 = [doc for _, doc in sorted(zip(scores, top_20), reverse=True)][:5]
```

Per [[concepts/reranking]] + [[concepts/contextual-retrieval]]: combined gain is −67% retrieval failure vs plain BM25.

**Trigger:** synthesis quality is high but answers sometimes miss the best page. Reranking fixes retrieval recall precision without changing the synthesis step.

---

## Related wiki pages

- [[concepts/contextual-retrieval]] — chunk context prepending; −49% retrieval failure
- [[concepts/bm25]] — lexical retrieval half of the hybrid pipeline
- [[concepts/reranking]] — post-retrieval filtering; −67% combined with contextual retrieval
- [[entities/qmd]] — current retrieval engine; BM25 + vector + LLM reranking, on-device
- [[entities/mnemory]] — Qdrant + S3 memory service; Qdrant usage patterns relevant to Level 3
- [[summaries/docling]] — document parsing if ingesting non-markdown sources into RAG
