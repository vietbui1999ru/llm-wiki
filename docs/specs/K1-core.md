---
status: draft
branch: kit
work_type: foundation
scope:
  - pyproject.toml
  - .gitignore
  - src/kb/**
  - tests/**
  - docs/specs/K1-*
---
# SPEC: K1, the local core of the knowledge base kit

## Objective

Build the local core of a domain-neutral, local-first knowledge base kit. A user runs `kb init`, writes markdown notes in Obsidian or with `kb new`, and asks questions. Code retrieves and routes. An LLM only writes the answer from the retrieved passages. With the default config, no data leaves the machine.

The design source is `docs/lean-kit/PLAN.md` on branch `plan/lean-kit` (sections 0 to 5). That file stays off this branch, because it describes the personal line. The repository root is the kit source. It is not a vault.

The kit v1 has five specs. This spec is K1.

| Spec | Content |
| --- | --- |
| K1 | Schema, `init`, templates, capture, lint, index, hybrid search, confidence router, `ask` without web, eval with calibration, `doctor` |
| K2 | Web adapters (`firecrawl-local`, `firecrawl-cloud`, `searxng`), the inbox flow, the MCP server, `kb tools --json` |
| K3 | `kb run-due`, the job list, stale scan, source link check |
| K4 | Block ID writes on citation, bootstrap graph patch, reorganizer patches with eval gating and budget caps, chat REPL |
| K5 | Repo migration, release gate (secret scan, personal-string scan), license, README, example vaults, `AGENTS.md`, the uvx install check |

### Stack and packaging

- Python 3.11 or later. Standard library only (`sqlite3` with FTS5, `tomllib`, `urllib`, `array`, `hashlib`, `json`, `argparse`, `secrets`).
- `pyproject.toml` uses the setuptools backend with a `src/` layout. Package data: `src/kb/presets/**` and `src/kb/data/*`. Entry point: `kb = "kb.cli:main"`. `python3 -m kb` also runs the CLI. The distribution name is decided in K5.
- Tests: `unittest`. The fake embedder and the fake LLM are one HTTP server on `127.0.0.1` in `tests/fakes.py`. It serves `/v1/embeddings` (feature hashing into 256 dimensions of the terms from `kb`'s own term function, stop words removed) and `/v1/chat/completions` (scripted replies). Tests use the real client code. No test needs a network or Ollama.
- Clock and date: every command takes today's date in local time from one function, `kb.clock.today()`, which tests replace.

### Exit codes (all commands)

| Code | Meaning |
| --- | --- |
| 0 | success; lint has warnings only |
| 1 | a check failed: lint errors, `index --check` stale, eval drop past the tolerance |
| 2 | usage error or refused action |
| 3 | no vault found (no `kb.toml` in the current directory or a parent), for every command except `init`; or no index, for `search`, `ask` and `eval` only. The message says `run kb init` or `run kb index` |

### Vault layout

`kb init [--preset glossary|research|docs] DIR` creates this layout. The default preset is `research`. It refuses a non-empty `DIR` with exit 2 unless `--force` is given. `--force` adds missing files and never overwrites an existing file.

```
kb.toml          types, retrieval, router, providers
notes/           notes; the preset adds 3 example notes
inbox/           captures (empty in K1)
templates/       one template per type of the preset
golden/          golden.json with a sample set over the example notes
.obsidian/       app.json, templates.json (folder templates/, dateFormat YYYY-MM-DD, timeFormat HH:mm)
.gitignore       contains .kb/
```

Presets live in `src/kb/presets/<name>/`. Each preset holds its `kb.toml`, its templates, its example notes and its `golden.json`.

### Note format

- A note is a UTF-8 markdown file under `notes/` with a frontmatter block between two `---` lines at the top.
- Frontmatter is the Obsidian Properties subset of YAML:
  - a key is `[A-Za-z_][A-Za-z0-9_-]*` followed by `: `;
  - a scalar is a plain or quoted (`"..."` or `'...'`) string, an integer, a decimal, `true`, `false`, a date `YYYY-MM-DD`, or null (`null`, `~` or empty);
  - `yes`, `no`, `on` and `off` stay strings;
  - a list is block form (`- x` lines indented by zero or two spaces) or flow form (`[x, y]`) of scalars; the writer keeps the existing indent and uses two spaces for a new list;
  - a full-line comment (`# ...`) is kept on write; inline comments are not supported;
  - a nested map, a nested list, an anchor, a tag (`!`) and a multi-line string are errors.
- A wikilink in a property must be a quoted string (`"[[note]]"`). An unquoted `[[note]]` is an error.
- The writer keeps key order, comments and the quoting style of each existing value. It writes new values unquoted when safe, else double-quoted.
- Fields:

| Field | Required | Value |
| --- | --- | --- |
| `id` | yes (see below) | 26-character Crockford base32 ULID from `secrets` and the clock |
| `title` | yes | text |
| `type` | yes | one of the types in `kb.toml` |
| `aliases`, `tags`, `related` | no | lists; `related` holds quoted wikilinks |
| `sources` | for `verified` | list of text: a URL, a quoted wikilink, or a citation |
| `retrieved` | no | date of the last web retrieval of the sources |
| `created`, `updated` | yes | date |
| `reviewed` | no | date |
| `review_interval` | no | `<n>d`; default `[notes] review_interval` in `kb.toml` (365d) |
| `confidence` | yes | `low`, `medium` or `high` |
| `status` | yes | `draft`, `verified`, `stale` or `superseded` |
| `superseded_by` | no | quoted wikilink |

- Obsidian templates cannot make a ULID. A note with no `id` is a lint warning. `kb lint --fix` assigns the missing `id`, and adds missing `created`, `updated` (file mtime date), `status: draft` and `confidence: low`. It changes nothing else.
- A type in `kb.toml` may add required fields and a word cap. The default word cap is 600 words of body text.

### Links

- Forms: `[[target]]`, `[[target|label]]`, `[[target#heading]]`, `[[target#^block]]`, `![[target]]`, and the same forms in quoted properties.
- The link corpus is the files under `notes/` and `inbox/`, plus non-markdown attachments anywhere in the vault outside `templates/`, `.obsidian/` and `.kb/`.
- Resolution follows Obsidian: an exact vault-relative path first, then a unique file name in the link corpus. Matching ignores case. A markdown target may omit `.md`. A non-markdown target (`![[x.png]]`) resolves to an attachment with that name.
- Aliases do not resolve. `[[alias]]` is unresolved, as in Obsidian.
- When two files share a name, the link must use a path; else it is ambiguous.
- `#heading` must match a heading of the target. Both sides are normalized as Obsidian does: each `#`, `|`, `^`, `:`, `%%`, `[[` and `]]` becomes a space, whitespace runs collapse to one space, and the comparison ignores case. `#^block` must match a block ID in the target.
- A block ID is ` ^` plus 1 to 32 characters from `[A-Za-z0-9-]` at the end of a paragraph or list item line.

### Templates and capture

- `templates/<type>.md` uses `{{title}}`, `{{date}}` and `{{time}}`, which the Obsidian core Templates plugin also fills.
- Slug: NFKD-normalize the title, drop combining marks, lowercase, replace each run of characters outside `[a-z0-9]` with `-`, trim `-`, cut to 80 characters. An empty slug becomes `note`. If `notes/<slug>.md` exists, add `-2`, `-3`, and so on.
- `kb new TYPE TITLE` writes `notes/<slug>.md` from the template, with a new `id`, `created` and `updated` set to today, `status: draft` and `confidence: low`. It prints the path. An unknown type exits 2.
- `kb add --json FILE|-` takes `{"type", "title", "body", optional fields}` from an agent. It validates against the type, writes the note like `kb new`, and prints `{"path", "id"}`. It rejects `status: verified` and `confidence: high` with exit 2.
- `kb verify NOTE [--confidence high|medium]` sets `status: verified`, `reviewed` and `updated` to today, and the confidence (default `high`). It refuses a note with no `sources` with exit 2. It is the only command that writes `verified` or `high`.

### Lint

`kb lint [--json] [--fix]` checks every note under `notes/` and `inbox/`.

- Errors: bad frontmatter, a missing required field other than `id`, an unknown type, a duplicate `id`, an unresolved link, an ambiguous link, a missing heading or block target, an unquoted wikilink in a property, `verified` with no `sources`.
- Warnings: a missing `id`, a body over the word cap, an orphan note (no inbound and no outbound link), a note past `reviewed + review_interval`.
- `--json` prints one object: `{"errors": [...], "warnings": [...]}`, each item `{"path", "line", "code", "message"}`.

### Index

`kb index [--full] [--check]` reads the notes and writes `.kb/`.

- Blocks: the body splits into blocks at blank lines. A heading line starts a new block and is not itself a block. Each top-level list item with its nested items is one block. A fenced code block, a table and a callout (`> [!type]`) are each one block. `line` is 1-based from the file start. A block key is its `^id` if present, else `L<line>`.
- Hashes: SHA-256 of the UTF-8 text. The block hash excludes a trailing ` ^id`. The note hash covers the whole file.
- `.kb/notes.jsonl`: one record per note (`kind: note`, all frontmatter fields, `path`, `hash`, `links_out`) and one per block (`kind: block`, `note_id`, `path`, `block`, `heading`, `text`, `line`, `hash`). Order: path ascending, note record first, then blocks by line.
- `.kb/links.json`: `{"edges": [...]}`, each edge `{"src", "dst", "kind"}` with vault-relative paths. `kind` is `link`, `embed`, `related` or `tag`. A tag edge is stored once with `src < dst`. Order: `src`, `dst`, `kind`.
- JSON output: `sort_keys=True`, `ensure_ascii=False`, separators `(",", ":")`, dates as `YYYY-MM-DD` strings, one trailing newline. The same vault gives the same bytes.
- `.kb/index.sqlite`: an FTS5 table `blocks_fts(text, title, aliases, tags)` with tokenizer `unicode61 remove_diacritics 2`; each row repeats its note's title, aliases and tags. A table `vectors(block_key, path, hash, model, dim, emb)` with `emb` as a float32 BLOB.
- Invalid notes: a note with a lint error is skipped, and `kb index` prints one warning per skipped note. A note with no `id` is indexed with `note_id: null`.
- Incremental: a block with an unchanged hash and the same model keeps its embedding. A model change re-embeds every block. `--full` rebuilds everything.
- `--check` builds `notes.jsonl` and `links.json` in memory and exits 1 when the files on disk differ.
- Embedder: `[embed]` in `kb.toml` with `provider = "openai-compatible"`, `base_url = "http://127.0.0.1:11434/v1"` (Ollama), `model = "nomic-embed-text"`, `timeout_s = 2`. When the endpoint does not answer within the timeout, the index has no vectors, `kb index` prints one warning, and search runs without the vector stage.

### Search

`kb search QUERY [-k N] [--json] [--stages bm25,vector,graph]` returns block-level hits: note path, title, block key, heading, text, line, the fused score and the raw score of each stage.

1. Query terms: lowercase, split on the `unicode61` rules, drop the stop words in `src/kb/data/stopwords.txt`. Each term is double-quoted (inner `"` doubled) and the terms are joined with `OR`. User text never reaches FTS5 unquoted.
2. BM25 top 50 from FTS5, `bm25(blocks_fts, 1.0, 2.0, 2.0, 1.0)`.
3. Vector top 50 by cosine similarity (brute force over the BLOBs).
4. Reciprocal rank fusion: `rrf(b) = sum over active rank stages of 1 / (60 + rank(b))`. Graph is not a rank stage.
5. Graph expansion: for each note one hop (in either direction, any edge kind) from the top 5 notes, its score is `graph_weight * best rrf of the source note` (default `graph_weight = 0.5`). Its block is its best-ranked block in steps 2 to 3, else its first block. A block that already has a score keeps the larger score.
6. Sort by score descending, then path ascending, then line ascending. Cut to `k` (default 8).

Zero query terms after stop words, or zero hits: an empty result, exit 0.

### Confidence router

The router computes `c` in 0..1 from the search result and the raw stage scores, with no LLM call:

```
c = w1*top + w2*agree + w3*cover + w4*support + w5*trust
```

Reading: confidence is a weighted sum of five retrieval signals, each scaled to 0..1.

- `top`: the largest of the active raw signals. Vector: `clamp((cos_best - cos_floor) / (1 - cos_floor))`, with `cos_floor = 0.3`. BM25: `s / (s + bm25_half)`, where `s` is the negated best `bm25()` value and `bm25_half = 5.0`. Ranks do not enter `top`.
- `agree`: the size of the overlap of the BM25 top 10 notes and the vector top 10 notes, divided by the size of the smaller of the two sets. When either set is empty, `agree = 0`.
- `cover`: the fraction of query terms found in the top `k` blocks.
- `support`: the count of distinct notes in the top `k` with score at least half of the best, capped at 3, divided by 3.
- `trust`: the mean over the top notes (up to 3) of `status_w * confidence_w * fresh`. Defaults: verified 1.0, draft 0.6, stale 0.3, superseded 0.1; high 1.0, medium 0.8, low 0.5. `fresh` is 1.0 within `reviewed + review_interval`, 0.5 after it, and 0.8 when `reviewed` is absent.
- Missing stages: without vectors, the `agree` weight moves to `cover`. Without BM25, the `agree` weight moves to `top`.
- Empty result: `c = 0`.

Defaults: `w = (0.30, 0.15, 0.25, 0.15, 0.15)`, `t_high = 0.60`, `t_low = 0.35`, in `[router]` in `kb.toml`. The defaults must route every sample positive query of each preset to a KB label and every sample negative query to `NOT IN KB`, with the fake embedder.

Routes in K1 (web arrives in K2):

| Condition | Route | Label |
| --- | --- | --- |
| `c >= t_high` | answer from the KB | `KB` |
| `t_low <= c < t_high` | answer from the KB with a low coverage note | `KB (low coverage)` |
| `c < t_low` | no answer; suggest `kb new` | `NOT IN KB` |

`--kb-only` keeps the KB routes. In K1, `--web` exits 2 with the message `web access arrives in K2`.

### Ask

`kb ask QUESTION [--json] [--kb-only] [--no-llm]`

- Order: search, then the router, then the LLM. The LLM gets only the question and the top `k` blocks, each tagged with its citation.
- Citation form: `[[path#^id]]` when the block has an ID; else `[[path#heading]] L<line>`, or `[[path]] L<line>` when the block has no heading. Every citation is a valid Obsidian link.
- The prompt template is `src/kb/data/answer_prompt.txt`. It says: answer only from the passages, cite each claim with the given citation, and say "not in the passages" when they do not answer.
- After the LLM answers, the kit checks each citation. It removes a citation that is not in the given blocks and adds the warning `unknown citation removed`.
- `--no-llm`, or an empty `[llm] model`: the answer is the top blocks with their citations (extractive).
- LLM: `[llm]` with `provider = "openai-compatible"`, `base_url = "http://127.0.0.1:11434/v1"`, `model = ""` (empty by default), `timeout_s = 120`.
- `ask` writes nothing. Block ID writes move to K4.
- Output: the answer, the label, `c` with its five parts, and the citations. `--json` gives the same as one object: `{"label", "c", "parts", "answer", "citations", "warnings"}`.

### Eval

`kb eval [--split dev|test|all] [--json] [--baseline FILE] [--calibrate [--write]]`

- `golden/golden.json` keeps the version 2 format of the personal line: `{"version": 2, "queries": [{"id", "query", "category", "split", "relevant": [{"page", "grade"}], "must_hit"}]}`. `page` is a vault-relative path. K1 adds `"expect": "kb" | "none"` (default `kb`); `none` marks a negative query.
- Eval searches with `k = 10`. Hits are deduplicated to notes, keeping the first rank of each note.
- Metrics on positive queries: recall@10, nDCG@10 (gain = grade), MRR, must_hit rate (a `must_hit` query passes when a grade-2 page is in the top 8). On all queries: router accuracy (positive queries routed to a KB label, negative queries routed to `NOT IN KB`).
- `--json` prints `{"split", "n", "metrics": {...}}`. `--baseline FILE` takes a saved `--json` output and exits 1 when a metric drops by more than `[eval] tolerance` (default 0.02).
- `--calibrate` searches integer weights in twentieths (sum 20) and both thresholds in steps of 0.05 (`t_low < t_high`) on the dev split, for the best router accuracy. Ties go to the smallest L1 distance from the current 7 values (5 weights in twentieths, 2 thresholds), then to the lexicographically smallest tuple. It prints the result and the test split score.
- `--write` replaces the values of the `[router]` keys in `kb.toml` in place and keeps every other line and comment. It refuses with exit 2 when the dev split has fewer than 30 queries.
- Each preset's sample `golden.json` has at least 6 positive and 3 negative queries over its example notes. A sample negative query shares no content term (after stop words) with the preset's notes.

### Doctor

`kb doctor [--json]` prints the vault path, the note count, FTS5 support, the index state (missing, fresh or stale), the embedder and LLM endpoints with reachability, and every outbound path. An outbound path is a configured endpoint whose host is not a loopback address. With the default config, the list is empty. No FTS5 support is an error (exit 1).

## Acceptance Criteria
- AC-1: `kb init` creates the vault layout for each preset, including the template date and time formats in `templates.json`; it refuses a non-empty directory, and `--force` adds missing files without overwriting.
  verify: `PYTHONPATH=src python3 -m unittest tests.test_init -v`
- AC-2: The frontmatter parser reads and writes the Properties subset and passes a fixture corpus: quoting, null forms, `yes` as a string, comments, block and flow lists, quoted wikilinks; it rejects nested maps, anchors, tags and unquoted wikilinks; unchanged notes round-trip byte for byte.
  verify: `PYTHONPATH=src python3 -m unittest tests.test_frontmatter -v`
- AC-3: Link parsing and resolution follow the Obsidian rules for paths, names, case, headings, block IDs, labels, embeds, non-markdown targets, unresolved aliases and ambiguous names.
  verify: `PYTHONPATH=src python3 -m unittest tests.test_links -v`
- AC-4: `kb new` fills the template and handles slug collisions; `kb add` validates agent JSON and rejects `verified` and `high`; `kb verify` sets its fields and refuses a note with no sources; ULIDs are 26 Crockford base32 characters.
  verify: `PYTHONPATH=src python3 -m unittest tests.test_capture -v`
- AC-5: `kb lint` reports each listed error and warning with the right code and exit code, `--fix` adds only the listed fields, and a fresh preset vault lints clean.
  verify: `PYTHONPATH=src python3 -m unittest tests.test_lint -v`
- AC-6: `kb index` splits blocks as specified, writes byte-identical `notes.jsonl` and `links.json` on two runs, keeps embeddings of unchanged blocks, re-embeds on a model change, and `--check` exits 1 after a note changes.
  verify: `PYTHONPATH=src python3 -m unittest tests.test_index -v`
- AC-7: `kb search` returns block-level hits from BM25, vectors, fusion and graph expansion with the specified tie-break; each stage can be turned off; it works with no embedder; hostile queries (quotes, `-`, `AND`, `NEAR`, `col:`, `*`) return results or an empty list, never an error.
  verify: `PYTHONPATH=src python3 -m unittest tests.test_search -v`
- AC-8: The router computes the five parts and `c` as specified, including the edge cases; with the defaults it routes every sample positive query of each preset to a KB label and every sample negative query to `NOT IN KB`.
  verify: `PYTHONPATH=src python3 -m unittest tests.test_router -v`
- AC-9: `kb ask` calls the LLM only after routing, sends only the top blocks, uses valid Obsidian citations, removes unknown citations, writes no file, gives an extractive answer with `--no-llm`, and exits 2 on `--web`.
  verify: `PYTHONPATH=src python3 -m unittest tests.test_ask -v`
- AC-10: `kb eval` computes every metric on a fixed golden set, exits 1 on a drop past the tolerance, calibrates on an integer grid, and `--write` keeps comments and refuses with fewer than 30 dev queries.
  verify: `PYTHONPATH=src python3 -m unittest tests.test_eval -v`
- AC-11: With `socket.connect` patched to refuse non-loopback addresses and the embedder pointed at a closed loopback port, `init`, `index`, `search`, `ask --no-llm`, `eval`, `lint` and `doctor` pass on a preset vault; `doctor` lists no outbound path and reports FTS5.
  verify: `PYTHONPATH=src python3 -m unittest tests.test_local_first -v`
- AC-12: The CLI runs from the source tree and the full suite passes.
  verify: `PYTHONPATH=src python3 -m kb --version && PYTHONPATH=src python3 -m unittest discover -s tests -t . -v`
- AC-13: On a machine with Ollama and `nomic-embed-text`, `kb index` on the research preset stores vectors, and `kb ask` on a sample positive query returns the label `KB` with citations.
  verify: manual - needs a local Ollama, which the host and CI do not have.

## Boundaries
### Always
- Keep markdown as the only source of truth. Generate everything under `.kb/`.
- Keep retrieval, routing and validation in code. Call the LLM only to write the answer.
- Use the loopback fake server for the embedder and the LLM in tests.
- Keep the default config loopback-only.
### Ask first
- Adding a dependency outside the Python standard library.
- Renaming a frontmatter field, a command, or a `kb.toml` key from this spec.
- Any write to a note other than `kb new`, `kb add`, `kb verify` and `kb lint --fix`.
- Any change to the router defaults that breaks the AC-8 routing of the sample golden sets.
### Never
- Copy a note, log, golden query or document from the personal line.
- Commit `.kb/` or any embedding.
- Let `kb add`, `kb ask`, `kb lint --fix` or an LLM set `status: verified` or `confidence: high`.
- Touch `main` of the public repo. The rename happens in K5.

## Open Questions
- The distribution name and the license are decided in K5. K1 uses the command `kb` and the package `kb`. A rename later changes the scope and needs a new approval.
- The default router values are guesses tuned only on the small sample sets. Real values need a vault with at least 30 dev queries.
- Brute-force vector search is fine to about 20,000 blocks (assumption, not measured). A `sqlite-vec` stage is a candidate for a later spec, with an approval for the dependency.
- Plan question 8 chose block IDs on first citation. K1 cites by heading and line and moves the writes to K4, because a read command that edits notes races with Obsidian.
