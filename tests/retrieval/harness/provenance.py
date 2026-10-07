"""Content hashes recorded with every run and baseline (stdlib only), so the gate can tell a retrieval change from a
change in the wiki or the labels. The hashes cover bytes, not mtimes, so touching a file does not change them."""
import hashlib
from pathlib import Path


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def wiki_sha256(repo_root):
    """SHA-256 over every wiki/**/*.md (sorted repo-relative path and bytes), so a rename also changes it."""
    root = Path(repo_root)
    digest = hashlib.sha256()
    for page in sorted((root / "wiki").rglob("*.md")):
        digest.update(page.relative_to(root).as_posix().encode() + b"\0" + page.read_bytes() + b"\0")
    return digest.hexdigest()
