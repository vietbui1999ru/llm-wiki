---
name: style-blog
description: Generate or update a blog post style variant. Supports named styles (ai, yoda, shakespeare, etc.). Uses Ollama by default (cost/privacy); falls back to Claude if unavailable.
---

# style-blog

Generate a style variant for a blog post in the Obsidian vault.

## Usage

Called as: `/style-blog <post-slug> [style-name]`

`<style-name>` is optional. If omitted, the style is read from the post's `style_label` frontmatter field.

Examples:
- `/style-blog building-a-vault-cms-pipeline yoda`  ← explicit style
- `/style-blog my-post`                              ← reads style_label from frontmatter
- `/style-blog my-post ai`                           ← explicit override

## Workflow

### Step 1: Locate the canonical post

Look for: `vendor/vault/Blogs/<slug>.md`

If not found, list `.md` files in `vendor/vault/Blogs/` (excluding `*.*.md`) and ask user to pick.

### Step 1b: Resolve style

- If `<style-name>` was provided as an argument → use it directly.
- If not provided → extract `style_label` from the frontmatter of the canonical post. `style_label` is a YAML list:
  ```yaml
  style_label:
    - ai
    - yoda
  ```
  Parse it with (handles both inline `[ai, yoda]` and block list):
  ```bash
  python3 -c "
  import re, sys
  text = open('<post-path>').read()
  fm = re.search(r'^---\n(.*?)\n---', text, re.DOTALL)
  if not fm: sys.exit(1)
  block = fm.group(1)
  items = []
  # inline: style_label: [ai, yoda]
  m = re.search(r'^style_label:\s*\[([^\]]*)\]', block, re.MULTILINE)
  if m and m.group(1).strip():
      items = [s.strip().lower() for s in m.group(1).split(',') if s.strip()]
  else:
      # block list: style_label:\n  - ai\n  - yoda
      m = re.search(r'^style_label:\s*\n((?:[ \t]+-[ \t]+.+\n?)+)', block, re.MULTILINE)
      if m:
          items = [re.sub(r'^[ \t]+-[ \t]+', '', l).strip().lower() for l in m.group(1).splitlines() if l.strip()]
  print('\n'.join(items))
  "
  ```
  Each line of output is one style to generate.
- If neither arg nor `style_label` found → stop and tell the user: "No style specified. Pass a style name as an argument or add `style_label:` list to the post's frontmatter."

**When multiple styles are resolved** (from the list), run Steps 2–7 for each style in sequence, then offer sync once at the end (Step 8).

### Step 2: Check for existing variant

Check for `vendor/vault/Blogs/<slug>.<style>.md`:
- **Exists**: Show first 200 chars. Ask: overwrite / update / cancel?
- **Not found**: Proceed to Step 3.

### Step 3: Load or create style guide

Style guide path: `docs/style-guides/<style>.md`

- **Exists**: Read and use as generation reference.
- **Not found**: Generate a style guide for `<style>` from general knowledge. Write to `docs/style-guides/<style>.md`. Inform user: "Style guide created at docs/style-guides/<style>.md — edit it to tune the voice before regenerating."

Style guide format: voice rules, sentence patterns, vocabulary, preservation rules (code/math/wikilinks), example transformations.

### Step 4: Select model

Check Ollama availability:

```bash
curl -s http://localhost:11434/api/tags 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    models = [m['name'] for m in data.get('models', [])]
    capable = [m for m in models if any(k in m.lower() for k in ['gemma', 'llama', 'mistral', 'qwen', 'phi'])]
    print(capable[0] if capable else '')
except Exception:
    print('')
" 2>/dev/null
```

- Non-empty output → use Ollama with that model.
- Empty / error → use current Claude session.

### Step 5: Build generation prompt

```
You are a writing style transformer. Rewrite the blog post body below using the style guide.

CONTENT PRESERVATION (non-negotiable — violations make the output unusable):
- Output must be at least as long as the input. Never shorten, summarize, or cut content.
- Every paragraph in the input must have a corresponding paragraph in the output.
- Every markdown link [text](url) must appear in the output with the EXACT same URL.
- Every Obsidian image embed ![[file]] or ![[file|alt]] must appear VERBATIM on its own line, at its exact position in the document. These are block-level images — do not move, merge, or omit them.
- Every standard markdown image ![alt](src) must appear unchanged.
- Every wikilink [[target]] or [[target|alias]] must appear unchanged.
- Every footnote, reference, or citation must appear unchanged.
- Every code block (``` or indented) must appear unchanged.
- Every LaTeX expression ($...$ or $$...$$) must appear unchanged.
- Heading levels and heading text must be preserved exactly.
- Do NOT add or remove sections, headings, images, links, or code blocks.

WHAT YOU MAY CHANGE:
- Prose sentence structure, word choice, phrasing — to match the target style.
- That is all.

Output only the transformed body — no frontmatter, no preamble, no wrapper, no
"Here is the rewritten version" framing.

STYLE GUIDE:
{style_guide_contents}

POST BODY:
{post_body_without_frontmatter}
```

### Step 6: Generate

**If Ollama:** POST to `http://localhost:11434/api/generate` with model + prompt, stream: false.

```bash
curl -s http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"MODEL\", \"prompt\": \"ESCAPED_PROMPT\", \"stream\": false}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['response'])"
```

**If Claude:** generate directly in session with the prompt above.

### Step 7: Write the variant file

Write to `vendor/vault/Blogs/<slug>.<style>.md`:

```markdown
---
style_label: <Display Name>
parent_slug: <slug>
---

<generated body>
```

Display name: capitalize first letter (yoda → Yoda, ai → AI, shakespeare → Shakespeare).

### Step 8: Offer sync

Ask: "Variant written to vendor/vault/Blogs/<slug>.<style>.md. Run sync-full.sh to publish? (y/n)"

If yes:
```bash
ls sync-full.sh scripts/sync-full.sh 2>/dev/null | head -1
```
Run whichever path exists. If neither found, tell user to run it manually.
