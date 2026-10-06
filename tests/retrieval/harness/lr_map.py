"""Map LightRAG aquery_data results to wiki pages (stdlib only).

Spec: docs/specs/retrieval-eval-suite.md, section 3.3. Verified against lightrag-hku 1.5.7: chunk ids look like
"wiki/concepts/a.md-chunk-000", entity and relationship source_id fields join chunk ids with "<SEP>".
"""
SEP = "<SEP>"


def page_of(chunk_id):
    """'wiki/x.md-chunk-003' -> 'wiki/x.md'. file_path is never used: LightRAG flattens it to the basename."""
    return chunk_id.rsplit("-chunk-", 1)[0]


def _data(result):
    if result.get("status") != "success":
        raise RuntimeError(f"aquery_data failed: {result.get('message', result)}")
    return result["data"]


def ranked_pages(result):
    """Pages in order of first appearance in data.chunks. For graph modes this is a round-robin merge of
    entity-, relation- and vector-derived chunks, not a score sort, so rank metrics are list-order metrics."""
    seen, out = set(), []
    for c in _data(result)["chunks"]:
        page = page_of(c["chunk_id"])
        if page not in seen:
            seen.add(page)
            out.append(page)
    return out


def kg_only_pages(result):
    """Pages cited only by retrieved entities or relationships, never by a returned chunk (diagnostic)."""
    data = _data(result)
    ranked = set(ranked_pages(result))
    cited = {page_of(cid) for item in data["entities"] + data["relationships"]
             for cid in item.get("source_id", "").split(SEP) if cid}
    return sorted(cited - ranked)


def diagnostics(result):
    data = _data(result)
    kw = result.get("metadata", {}).get("keywords", {})
    return {"entities": len(data["entities"]), "relationships": len(data["relationships"]),
            "chunks": len(data["chunks"]), "ll_keywords": len(kw.get("low_level", [])),
            "hl_keywords": len(kw.get("high_level", []))}
