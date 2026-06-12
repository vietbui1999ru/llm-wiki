---
title: "Wikilink Graph Extraction: Reducing LightRAG Indexing Cost"
type: concept
tags: [rag, lightrag, obsidian, wikilinks, cost-reduction, knowledge-graph, indexing]
sources: []
created: 2026-05-12
updated: 2026-05-12
---

# Wikilink Graph Extraction: Reducing LightRAG Indexing Cost

LightRAG's entity/relation extraction is expensive because it pays the LLM to discover graph structure from raw text. In an Obsidian-style wiki, this structure is already explicit: `[[wikilinks]]` are a manually curated knowledge graph, and frontmatter declares entity metadata (title, type, tags).

Injecting this pre-parsed structure as extraction hints reduces redundant LLM work and focuses extraction on *implicit* relations not captured by explicit links.

---

## The Problem

LightRAG runs three extraction phases per page during indexing:

1. **Entity extraction** — LLM identifies named concepts, tools, people
2. **Relation extraction** — LLM finds connections between entities
3. **Community summarization** — LLM summarizes entity clusters

Each phase involves multiple LLM calls per chunk. For a wiki where pages already declare their connections via `[[wikilinks]]`, phases 1–2 largely re-discover what's already known. At ~150 pages with Haiku, this costs $10–30 *(claimed, unverified)*.

**Example — what the LLM re-discovers unnecessarily:**
```
concepts/agent-harness.md explicitly links to:
  [[concepts/context-compression]]
  [[concepts/ralph-loop]]
  [[concepts/tool-design-for-agents]]
  [[summaries/autoresearch-karpathy]]
  ...
```
The extraction LLM would have found all of these anyway — and charged tokens for it.

---

## The Optimization: Extraction Hint Injection via `chunking_func`

LightRAG accepts a custom `chunking_func` that controls how each document is split before the extraction LLM sees it. By wrapping the default chunker, we can prepend a structured header:

```
## GRAPH STRUCTURE (pre-parsed — do not re-extract these)
Primary entity: "Agent Harness" (type: concept, tags: agent-engineering, harness)
Confirmed outgoing relations (skip re-extraction):
  → context compression  [concepts/context-compression]
  → ralph loop  [concepts/ralph-loop]
  → tool design for agents  [concepts/tool-design-for-agents]
  → autoresearch karpathy  [summaries/autoresearch-karpathy]
Extract ONLY implicit relations and entities NOT listed above.
## END GRAPH STRUCTURE
```

The LLM reads this first. It no longer needs to spend tokens re-confirming the explicit connections — it focuses on discovering what's *implicit* in the prose.

### Implementation

```python
def wiki_chunking_func(tokenizer, content, split_by_character=None,
                       split_by_character_only=False,
                       chunk_overlap_token_size=64, chunk_token_size=800):
    from lightrag.operate import chunking_by_token_size
    import re

    # Parse frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    fm_text  = fm_match.group(1) if fm_match else ""
    title_m  = re.search(r'^title:\s*"?([^"\n]+)"?', fm_text, re.MULTILINE)
    type_m   = re.search(r'^type:\s*(\w+)', fm_text, re.MULTILINE)
    tags_m   = re.search(r'^tags:\s*\[([^\]]+)\]', fm_text, re.MULTILINE)
    title    = title_m.group(1).strip() if title_m else ""
    etype    = type_m.group(1) if type_m else "concept"
    tags     = [t.strip() for t in tags_m.group(1).split(',')] if tags_m else []
    links    = list(dict.fromkeys(re.findall(r'\[\[([^\]|]+)', content)))

    header = ["## GRAPH STRUCTURE (pre-parsed — do not re-extract these)"]
    if title:
        tags_str = f", tags: {', '.join(tags)}" if tags else ""
        header.append(f'Primary entity: "{title}" (type: {etype}{tags_str})')
    if links:
        header.append("Confirmed outgoing relations (skip re-extraction):")
        for link in links[:25]:
            name = link.split("/")[-1].replace("-", " ")
            header.append(f"  → {name}  [{link}]")
    header.append("Extract ONLY implicit relations and entities NOT listed above.")
    header.append("## END GRAPH STRUCTURE\n")

    enriched = "\n".join(header) + "\n" + content
    return chunking_by_token_size(tokenizer, enriched, split_by_character,
                                  split_by_character_only,
                                  chunk_overlap_token_size, chunk_token_size)
```

Wire into LightRAG:
```python
LightRAG(
    ...
    chunking_func=wiki_chunking_func,
)
```

---

## Expected Savings

The header adds ~50-100 tokens per chunk but saves the LLM from outputting confirmed relations it would have generated anyway. Net reduction depends on link density and how explicit the prose is.

| Wiki characteristic | Expected reduction |
|---|---|
| High link density (5+ links/page, explicit prose) | ~40–60% extraction tokens |
| Low link density (<2 links/page, implicit prose) | ~10–20% |
| This wiki (avg 5.8 links/page, well-linked) | ~40–55% estimated |

These are estimates — actual savings depend on LightRAG's internal prompting and how much the model weighs the hint header.

---

## Limitations

- **Header increases input tokens slightly** per chunk (offset by output savings, since confirmed relations don't need to appear in the LLM's extraction output)
- **Link quality matters** — circular or stale wikilinks in the hints could mislead extraction; keep `[[links]]` accurate
- **Community summarization phase unchanged** — this optimization targets phases 1-2; community summaries still require full LLM passes
- **Not a full bypass** — the LLM still runs; this optimizes *what it's asked to discover*, not whether it runs

---

## Future Work: Direct Graph Injection

A more aggressive optimization would bypass LightRAG's LLM extraction entirely for well-linked pages and write entities/relations directly into LightRAG's graph store from the wikilink structure. This would reduce full-build cost from $10–30 → near-zero.

Requires: understanding LightRAG's internal storage format (`graph_chunk_entity_relation.graphml`, entity/relation KV stores) and injecting programmatically. LightRAG doesn't expose a public API for this — it would require either internal API use or a PR to LightRAG upstream.

---

## Related

- [[syntheses/local-rag-wiki]] — full RAG stack architecture; cost estimates
- [[concepts/contextual-retrieval]] — related technique: prepending context to *chunks* before retrieval (vs extraction); same principle applied differently
- [[entities/qmd]] — the BM25+vector alternative retrieval path that has no extraction cost
