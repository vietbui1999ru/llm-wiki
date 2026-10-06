"""Building blocks for the seed golden set (stdlib only).

Spec: docs/specs/retrieval-eval-suite.md, section 5.3 step 1. Pages are read once; sampling is seeded so the
same wiki gives the same candidates. Exact queries come from titles, relational ones from wikilink pairs.
"""
import random
import re
from pathlib import Path

ELIGIBLE_DIRS = ("concepts", "entities", "systems", "patterns")
LINK = re.compile(r"\[\[([^\]|#]+)")


def read_wiki(repo_root):
    """{page path: {title, status, text, links}}; links are resolved to pages that exist."""
    root = Path(repo_root)
    pages = {}
    for f in sorted((root / "wiki").rglob("*.md")):
        text = f.read_text()
        meta = text.split("---")[1] if text.startswith("---") else ""
        title = re.search(r'^title:\s*"?(.*?)"?\s*$', meta, re.M)
        status = re.search(r"^status:\s*(\S+)", meta, re.M)
        pages[f.relative_to(root).as_posix()] = {
            "title": title.group(1) if title else f.stem, "status": status.group(1) if status else "", "text": text,
            "raw_links": [f"wiki/{m.strip()}.md" for m in LINK.findall(text)]}
    for page in pages.values():
        page["links"] = sorted({link for link in page.pop("raw_links") if link in pages})
    return pages


def eligible(pages):
    """Substantive pages from the curated dirs: no stubs, no summaries (they mirror one source each)."""
    return sorted(p for p, v in pages.items()
                  if p.split("/")[1] in ELIGIBLE_DIRS and v["status"] != "stub")


def link_pairs(pages):
    """Sorted (a, b) wikilink pairs between eligible pages, each pair once."""
    ok = set(eligible(pages))
    return sorted({tuple(sorted((a, b))) for a in ok for b in pages[a]["links"] if b in ok and b != a})


def pick(paths, n, seed):
    return sorted(random.Random(seed).sample(sorted(paths), min(n, len(paths))))
