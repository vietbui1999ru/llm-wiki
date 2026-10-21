#!/usr/bin/env node
// docs-sync.mjs — refresh the llm-wiki docs that describe the dotfiles agent
// harness after the harness changes, then publish them in one commit.
//
// Design: docs/superpowers/specs/2026-10-20-docs-sync-design.md
// Usage:  node claude-setup/scripts/docs-sync.mjs [--since <ref>] [--dry-run]
//
// Flow: preflight -> range -> map -> rewrite -> gate -> lint rewrites -> bookkeeping
// -> ship. Dotfiles is read-only input: every write stays under llm-wiki.
// Node 22, no npm dependencies (node: built-ins only).

import { execFile, spawnSync } from "node:child_process";
import { closeSync, existsSync, openSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { basename, dirname, join, matchesGlob, resolve, sep } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { parseArgs, promisify } from "node:util";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const MANIFEST_REL = "claude-setup/docs-sync.json";
const BUILD_SCRIPT = join(ROOT, "claude-setup", "scripts", "build-docs-site.mjs");

const MODEL = "opencode-go/deepseek-v4.1-flash:medium";
// --no-tools alone is not enough: pi's default system prompt still says it has bash and
// file tools, so on an exploratory-sounding task the model emits tool-call markup as text.
const PI_SYSTEM_PROMPT = "You are a text transformer, not a coding agent. You have no tools and "
  + "cannot read files or run commands. Everything you need is in the user message. Reply with "
  + "exactly the output the user asks for and nothing else.";
const PI_ARGS = [
  "-p", "--model", MODEL,
  "--no-tools", "--no-session", "--no-extensions",
  "--no-skills", "--no-context-files", "--no-mcp",
  "--system-prompt", PI_SYSTEM_PROMPT,
];
const PI_CONCURRENCY = 3;
const MAX_BUFFER = 32 * 1024 * 1024;
const PI_TIMEOUT_MS = 10 * 60 * 1000; // one stuck model call fails its page, not the run
const PROMPT_BUDGET = 60_000; // chars of diff per rewrite prompt
const DELETION_CAP = 0.75; // reject a rewrite that removes more than 75% of the lines
const SHRINK_FLOOR = 0.5; // reject a rewrite with under half the original's non-blank lines
const LINT_PIN = "markdownlint-cli2@0.14.0"; // bundled by markdownlint-cli2-action@v17
// Secret-looking paths never reach a prompt (diffs go to a remote model, rewrites to a
// public site). Built-ins always win over a manifest `!` keep.
const SECRET_GLOBS = [
  "**/.env", "**/.env.*", "**/*.pem", "**/*.key", "**/*.p12", "**/*.pfx", "**/*.gpg",
  "**/auth.json", "**/.netrc", "**/.npmrc", "**/.pypirc", "**/.git-credentials", "**/hosts.yml",
  "**/id_rsa*", "**/id_ed25519*", "**/id_ecdsa*", "**/.ssh/**", "**/.kube/config",
  "**/*credential*", "**/*credential*/**", "**/*secret*", "**/*secret*/**",
  "**/*token*", "**/*token*/**",
];
// Second line of defence on content: a diff hunk with one of these skips its page.
const SECRET_CONTENT_RE = /\b(sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|xox[abpr]-[A-Za-z0-9-]{10,})|-----BEGIN [A-Z ]*PRIVATE KEY-----/;
export const hasSecretContent = (text) => SECRET_CONTENT_RE.test(text);
const EXCLUDE_GLOBS = [".claude/worktrees/**", "docs/superpowers/**", "**/*.bak", ...SECRET_GLOBS];
const CATALOG_DIRS = ["systems", "entities", "concepts", "syntheses"];
const SENTINEL_OPEN = "<<<DOCS_SYNC_BODY>>>";
const SENTINEL_CLOSE = "<<<DOCS_SYNC_END>>>";
const USAGE = "usage: node claude-setup/scripts/docs-sync.mjs [--since <ref>] [--dry-run]";

const today = () => new Date().toISOString().slice(0, 10);

// ---------------------------------------------------------------------------
// pure helpers — unit-tested in docs-sync.test.mjs

/** Replace the body of a page, keeping its frontmatter block as-is. */
function replaceBody(raw, body) {
  const { frontmatter } = splitFrontmatter(raw);
  if (!frontmatter) throw new Error("page has no frontmatter block");
  return `${frontmatter}\n\n${body.replace(/\s+$/, "")}\n`;
}

function splitFrontmatter(raw) {
  if (!raw.startsWith("---\n")) return { frontmatter: "", body: raw };
  const end = raw.indexOf("\n---", 4);
  if (end === -1) return { frontmatter: "", body: raw };
  return { frontmatter: raw.slice(0, end + 4), body: raw.slice(end + 4).replace(/^\r?\n/, "") };
}

/** Set `updated:` in the frontmatter block to `date`; other fields untouched. */
export function bumpUpdated(raw, date) {
  const { frontmatter } = splitFrontmatter(raw);
  if (!frontmatter) throw new Error("page has no frontmatter block");
  if (/^updated:.*$/m.test(frontmatter)) {
    return frontmatter.replace(/^updated:.*$/m, `updated: ${date}`) + raw.slice(frontmatter.length);
  }
  const insertAt = frontmatter.lastIndexOf("\n---");
  return frontmatter.slice(0, insertAt) + `\nupdated: ${date}` + frontmatter.slice(insertAt) +
    raw.slice(frontmatter.length);
}

// path.matchesGlob never lets * or ** match a segment that starts with "." (hidden files),
// but dotfiles paths are full of .config/ and .claude/ dirs. Mask the leading dot of every
// segment in both path and glob: a literal ".claude" still matches, and ** crosses .config.
const unhide = (text) => text.replace(/(^|\/)\./g, "$1\u0001");
export const globMatch = (path, glob) => matchesGlob(unhide(path), unhide(glob));

/**
 * True when a dotfiles path is out of scope: the built-in excludes (worktrees, specs,
 * backups) or the manifest's `ignore` globs. An `ignore` glob starting with `!` keeps a
 * path in scope even when another ignore glob matches it (e.g. agent files under nvim/).
 */
export function isExcluded(path, ignore = []) {
  if (EXCLUDE_GLOBS.some((glob) => globMatch(path, glob))) return true;
  const keep = ignore.filter((glob) => glob.startsWith("!")).map((glob) => glob.slice(1));
  if (keep.some((glob) => globMatch(path, glob))) return false;
  return ignore.some((glob) => !glob.startsWith("!") && globMatch(path, glob));
}

/** Map changed dotfiles paths to llm-wiki docs; report paths no entry covers. */
export function mapToDocs(changedPaths, entries) {
  const byDoc = new Map();
  const uncovered = [];
  for (const path of changedPaths) {
    const hits = entries.filter((entry) => entry.paths.some((glob) => globMatch(path, glob)));
    if (!hits.length) {
      uncovered.push(path);
      continue;
    }
    for (const entry of hits) {
      for (const doc of entry.docs) {
        if (!byDoc.has(doc)) byDoc.set(doc, new Set());
        byDoc.get(doc).add(path);
      }
    }
  }
  const docs = [...byDoc].map(([doc, paths]) => ({ doc, paths: [...paths].sort() }));
  return { docs, uncovered };
}

/**
 * Extract the rewritten body and the INDEX one-liner from a model reply.
 * Returns null when either sentinel is missing.
 */
export function parseSentinels(text) {
  if (typeof text !== "string") return null;
  const start = text.indexOf(SENTINEL_OPEN);
  if (start === -1) return null;
  const end = text.indexOf(SENTINEL_CLOSE, start + SENTINEL_OPEN.length);
  if (end === -1) return null;
  const body = text.slice(start + SENTINEL_OPEN.length, end).replace(/^\s*\n/, "").replace(/\s+$/, "");
  const indexLine = text.match(/^\s*INDEX:\s*(.+)$/m);
  return { body: body === "" ? "" : `${body}\n`, index: indexLine ? indexLine[1].trim() : "" };
}

/** Fraction of the original lines that the rewrite no longer contains (0..1). */
export function deletionRatio(original, rewritten) {
  if (!original) return 0;
  const originalLines = original.split("\n").map((line) => line.trimEnd());
  const pool = new Map();
  for (const line of rewritten.split("\n").map((l) => l.trimEnd())) {
    pool.set(line, (pool.get(line) || 0) + 1);
  }
  let removed = 0;
  for (const line of originalLines) {
    const available = pool.get(line) || 0;
    if (available > 0) pool.set(line, available - 1);
    else removed++;
  }
  return originalLines.length ? removed / originalLines.length : 0;
}

/**
 * Wikilink targets in `body` that `known` does not resolve. Skips fenced and
 * inline code, ignores `#anchors`, and accepts the bare slug form.
 */
export function unresolvedWikilinks(body, known) {
  const keys = known instanceof Set ? known : new Set(known);
  const missing = [];
  let inFence = false;
  for (let line of body.split("\n")) {
    if (/^\s*(```|~~~)/.test(line)) {
      inFence = !inFence;
      continue;
    }
    if (inFence) continue;
    line = line.split(/(`[^`]*`)/).map((span) => (span.startsWith("`") ? "" : span)).join("");
    for (const match of line.matchAll(/\[\[([^\]]+)\]\]/g)) {
      const target = match[1].split("|")[0].split("#")[0].trim();
      if (!target) continue;
      if (!keys.has(target) && !keys.has(basename(target))) missing.push(target);
    }
  }
  return missing;
}

/** True when every ```mermaid block in `body` renders through pele-render. */
export function mermaidRenders(body) {
  const blocks = [];
  for (const match of body.matchAll(/^```mermaid[ \t]*\r?\n([\s\S]*?)^```[ \t]*$/gm)) blocks.push(match[1]);
  for (const source of blocks) {
    const result = spawnSync("pele-render", ["-"], { input: source, encoding: "utf8", maxBuffer: MAX_BUFFER });
    if (result.error || result.status !== 0) return false;
  }
  return true;
}

const nonBlankLines = (text) => text.split("\n").filter((line) => line.trim()).length;

/**
 * Decide whether a rewrite may replace the original page. Every check is hard:
 * the run is unattended, so a doubtful rewrite keeps the original page.
 *
 * - Deletion cap is 75%, not 60%: deletionRatio counts every edited line as
 *   removed, and restructuring is allowed.
 * - Shrink guard: fewer than half the original's non-blank lines usually means
 *   the model's output was cut off, not that the page got tighter.
 *
 * @param {string} original current page body (frontmatter stripped)
 * @param {string} reply    raw model reply (body between sentinel markers)
 * @param {Set<string>} keys resolvable wikilink targets
 * @returns {{ok: boolean, rewrite?: string, index?: string, reason?: string}}
 */
export function acceptRewrite(original, reply, keys) {
  const parsed = parseSentinels(reply);
  if (!parsed) return { ok: false, reason: "sentinels missing" };
  const body = parsed.body;
  if (!body.trim()) return { ok: false, reason: "empty body" };
  if (body === original) return { ok: false, reason: "body unchanged" };
  if (nonBlankLines(body) < nonBlankLines(original) * SHRINK_FLOOR) {
    return { ok: false, reason: `shrank to ${nonBlankLines(body)}/${nonBlankLines(original)} lines (likely truncated)` };
  }
  const ratio = deletionRatio(original, body);
  if (ratio > DELETION_CAP) {
    return { ok: false, reason: `deletes ${Math.round(ratio * 100)}% of lines (cap ${DELETION_CAP * 100}%)` };
  }
  const missing = unresolvedWikilinks(body, keys);
  if (missing.length) return { ok: false, reason: `unresolved wikilinks: ${[...new Set(missing)].join(", ")}` };
  // Last: the only check that spawns a process.
  if (!mermaidRenders(body)) return { ok: false, reason: "mermaid block does not render" };
  return { ok: true, rewrite: body, index: parsed.index };
}

// ---------------------------------------------------------------------------
// runtime helpers

const execFileAsync = promisify(execFile);

// Close the child's stdin at once. An open pipe that is never written never sends
// EOF, and `pi -p` waits for stdin EOF before it starts (why dispatches use < /dev/null).
export function execClosed(cmd, args, opts) {
  const call = execFileAsync(cmd, args, opts);
  call.child.stdin?.end();
  return call;
}

async function run(cmd, args, { allowFailure = false, cwd = ROOT } = {}) {
  try {
    const { stdout, stderr } = await execClosed(cmd, args, { cwd, maxBuffer: MAX_BUFFER });
    return { code: 0, stdout, stderr };
  } catch (err) {
    const failed = { code: err.code ?? 1, stdout: err.stdout ?? "", stderr: err.stderr ?? err.message };
    if (allowFailure) return failed;
    throw new Error(`${cmd} ${args.join(" ")} failed (exit ${failed.code})\n${failed.stderr || failed.stdout}`);
  }
}

const git = (args, opts) => run("git", args, opts);
// --literal-pathspecs: changed paths go to git as-is, never as glob or :(magic) pathspecs.
const dotfilesGit = (dotfiles, args, opts) => run("git", ["-C", dotfiles, "--literal-pathspecs", ...args], opts);

function hasCommand(name) {
  return spawnSync("/bin/sh", ["-c", `command -v -- ${name}`], { encoding: "utf8" }).status === 0;
}

function writeInRepo(relPath, text) {
  const abs = resolve(ROOT, relPath);
  if (abs !== ROOT && !abs.startsWith(ROOT + sep)) {
    throw new Error(`refusing to write outside llm-wiki: ${relPath}`);
  }
  writeFileSync(abs, text);
}

function truncate(text, limit) {
  return text.length <= limit ? text : `${text.slice(0, limit)}\n… [truncated ${text.length - limit} chars]`;
}

function loadManifest() {
  let manifest;
  try {
    manifest = JSON.parse(readFileSync(join(ROOT, MANIFEST_REL), "utf8"));
  } catch (err) {
    throw new Error(`${MANIFEST_REL}: cannot read manifest (${err.message})`);
  }
  if (!Array.isArray(manifest?.entries)) throw new Error(`${MANIFEST_REL}: entries must be an array`);
  return manifest;
}

function resolveDotfiles(manifest) {
  return (manifest.dotfiles || "~/dotfiles").replace(/^~(?=$|\/)/, homedir());
}

/** Every page a wikilink may target: all wiki pages, by "dir/slug" and bare slug. */
function resolvableKeys() {
  const keys = new Set();
  for (const entry of readdirSync(join(ROOT, "wiki"), { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    for (const file of readdirSync(join(ROOT, "wiki", entry.name))) {
      if (!file.endsWith(".md")) continue;
      const slug = file.slice(0, -3);
      keys.add(`${entry.name}/${slug}`);
      keys.add(slug);
    }
  }
  return keys;
}

/** Docs the model may propose in a mapping answer (design scope). */
function inScopeCatalog() {
  const docs = readdirSync(join(ROOT, "docs")).filter((f) => f.endsWith(".md")).map((f) => `docs/${f}`);
  docs.push("GUIDE.md");
  for (const dir of CATALOG_DIRS) {
    for (const file of readdirSync(join(ROOT, "wiki", dir))) {
      if (file.endsWith(".md")) docs.push(`wiki/${dir}/${file}`);
    }
  }
  return docs.sort();
}

async function pool(items, limit, worker) {
  const results = [];
  let next = 0;
  const runners = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (next < items.length) {
      const index = next++;
      results[index] = await worker(items[index]);
    }
    return results;
  });
  await Promise.all(runners);
  return results;
}

// pi runs as pure text-in/text-out: no tools, no session, no extensions. The
// prompt goes in argv (budgeted, PROMPT_BUDGET) and execClosed ends stdin, so pi
// reads EOF — the design's `< /dev/null`.
async function runPi(prompt) {
  try {
    const { stdout } = await execClosed("pi", [...PI_ARGS, prompt], {
      cwd: ROOT, maxBuffer: MAX_BUFFER, timeout: PI_TIMEOUT_MS,
    });
    return stdout;
  } catch (err) {
    if (err.killed) throw new Error(`pi timed out after ${PI_TIMEOUT_MS / 60_000} min`);
    throw new Error(`pi failed (exit ${err.code ?? 1})\n${err.stderr || err.message}`);
  }
}

// ---------------------------------------------------------------------------
// 1. preflight

function acquireLock() {
  const lockPath = join(tmpdir(), "llm-wiki-docs-sync.lock");
  try {
    closeSync(openSync(lockPath, "wx"));
  } catch (err) {
    if (err.code === "EEXIST") throw new Error(`another docs-sync run holds ${lockPath}`);
    throw err;
  }
  return lockPath;
}

async function preflight(dotfiles) {
  const branch = (await git(["rev-parse", "--abbrev-ref", "HEAD"])).stdout.trim();
  if (branch !== "main") throw new Error(`llm-wiki is on "${branch}", expected main`);
  const dirty = (await git(["status", "--porcelain"])).stdout.trim();
  if (dirty) throw new Error(`llm-wiki working tree is dirty; commit or stash first:\n${dirty}`);
  for (const command of ["pi", "pele-render", "node", "bun"]) {
    if (!hasCommand(command)) throw new Error(`required command not found on PATH: ${command}`);
  }
  if (!existsSync(join(dotfiles, ".git"))) throw new Error(`dotfiles repo not found: ${dotfiles}`);
  await git(["pull", "--ff-only"]);
}

// ---------------------------------------------------------------------------
// 2. range

async function resolveRange(dotfiles, manifest, since) {
  const ref = manifest.last_synced_sha || since;
  if (!ref) throw new Error(`no baseline: first run needs --since <ref> (or set last_synced_sha in ${MANIFEST_REL})`);
  const base = (await dotfilesGit(dotfiles, ["rev-parse", ref])).stdout.trim();
  const head = (await dotfilesGit(dotfiles, ["rev-parse", "main"])).stdout.trim();
  const names = (await dotfilesGit(dotfiles, ["diff", "--name-only", `${base}..main`])).stdout;
  const changed = names.split("\n").map((line) => line.trim()).filter((line) => line && !isExcluded(line, manifest.ignore));
  return { base, head, changed };
}

// ---------------------------------------------------------------------------
// 3. map — auto-grow the manifest for uncovered paths

function mapPrompt(paths, catalog) {
  return `You maintain the mapping between a dotfiles repo and an llm-wiki docs repo.

Dotfiles paths changed but covered by no manifest entry:
${paths.map((p) => `- ${p}`).join("\n")}

In-scope llm-wiki docs (the only allowed targets):
${catalog.map((d) => `- ${d}`).join("\n")}

Propose manifest entries that route those dotfiles paths to the docs that describe them.
A dotfiles glob may cover several paths; a doc may appear more than once.
Return ONLY a JSON object, no prose and no code fence, shaped like:
{"<dotfiles glob>": ["<llm-wiki doc path>", ...]}`;
}

async function proposeEntries({ uncovered, manifest }) {
  const reply = await runPi(mapPrompt(uncovered, inScopeCatalog()));
  const start = reply.indexOf("{");
  const end = reply.lastIndexOf("}");
  if (start === -1 || end <= start) {
    throw new Error(`map call returned no JSON object; reply starts: ${JSON.stringify(reply.slice(0, 200))}`);
  }
  let proposals;
  try {
    proposals = JSON.parse(reply.slice(start, end + 1));
  } catch (err) {
    throw new Error(`map call returned invalid JSON: ${err.message}`);
  }

  const catalog = new Set(inScopeCatalog());
  const added = [];
  for (const [glob, docs] of Object.entries(proposals)) {
    if (typeof glob !== "string" || !glob || !Array.isArray(docs)) continue;
    if (/^[*!]/.test(glob)) continue; // model globs need a literal first segment: no catch-alls
    const covered = uncovered.some((path) => globMatch(path, glob));
    const valid = docs.filter((doc) => typeof doc === "string" && catalog.has(doc) && existsSync(join(ROOT, doc)));
    if (!covered || !valid.length) continue;
    added.push({ paths: [glob], docs: [...new Set(valid)] });
  }
  manifest.entries.push(...added);
  const stillUncovered = uncovered.filter(
    (path) => !added.some((entry) => entry.paths.some((glob) => globMatch(path, glob))),
  );
  return { added, uncovered: stillUncovered };
}

// ---------------------------------------------------------------------------
// 4. rewrite

function rewritePrompt({ doc, body, commits, diff }) {
  return `You maintain the llm-wiki knowledge base, which documents a personal agent harness.
A dotfiles change landed in the repositories and paths this page describes. Rewrite the page
body so it matches the change.

Rules:
- Return only the new body, wrapped in ${SENTINEL_OPEN} and ${SENTINEL_CLOSE}. No frontmatter:
  the script owns it.
- Then add one last line: INDEX: <one-line description of the page, max 200 chars>.
- Keep the page's conventions: heading style, tables, lists, and [[dir/slug]] wikilinks stay
  wikilinks. Do not invent link targets.
- Update prose, workflow descriptions and Mermaid diagrams; you may add or restructure
  diagrams. Every \`\`\`mermaid block must render with Mermaid 12.
- Never invent model names, versions, flags, file paths or measurements that are not in the
  input. Mark unverifiable claims from memory as "(training data — verify)".
- Keep the page's scope and length; integrate the change instead of appending a status note.

Page: ${doc}

Relevant dotfiles commit messages:
${commits || "(none)"}

Dotfiles diff (possibly truncated):
${diff || "(no textual diff)"}

Current body:
${body}`;
}

async function rewriteOne({ dotfiles, base, item, keys, originals }) {
  const raw = readFileSync(join(ROOT, item.doc), "utf8");
  const { body } = splitFrontmatter(raw);
  originals.set(item.doc, raw);

  const commits = truncate(
    (await dotfilesGit(dotfiles, ["log", "--format=%h %s", `${base}..main`, "--", ...item.paths])).stdout.trim(),
    4_000,
  );
  const fullDiff = (await dotfilesGit(dotfiles, ["diff", "--unified=2", `${base}..main`, "--", ...item.paths])).stdout;
  if (hasSecretContent(fullDiff) || hasSecretContent(commits)) return { doc: item.doc, ok: false, reason: "secret-like content in diff; not sent" };
  const diff = truncate(fullDiff, PROMPT_BUDGET);

  let reply;
  try {
    reply = await runPi(rewritePrompt({ doc: item.doc, body, commits, diff }));
  } catch (err) {
    // One failed call (provider content filter, timeout) skips its page, not the run.
    return { doc: item.doc, ok: false, reason: failureReason(err) };
  }
  return { doc: item.doc, ...acceptRewrite(body, reply, keys) };
}

/** One-line skip reason from a pi error: "pi failed (exit 1): Provider finish_reason: ...". */
export function failureReason(err) {
  const lines = String(err?.message ?? err).split("\n").map((line) => line.trim()).filter(Boolean);
  return lines.join(": ").slice(0, 160);
}

// ---------------------------------------------------------------------------
// 6. bookkeeping

function updateIndexLine(indexText, doc, description) {
  const target = doc.replace(/^wiki\//, "").replace(/\.md$/, "");
  const pattern = new RegExp(
    `^(- \\[\\[${target.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\](?:\\s*\\*\\([^)]*\\)\\*)?\\s*—\\s*).*$`,
    "m",
  );
  if (!pattern.test(indexText) || !description) return indexText;
  return indexText.replace(pattern, (_match, prefix) => `${prefix}${description}`);
}

function logEntry({ base, head, accepted, skipped, uncovered, newEntries }) {
  const lines = [
    `## [${today()}] docs-sync | dotfiles ${base.slice(0, 7)}..${head.slice(0, 7)}`,
    "",
    "Updated:",
  ];
  if (accepted.length) {
    for (const item of accepted) lines.push(`- \`${item.doc}\`${item.index ? ` — ${item.index}` : ""}`);
  } else {
    lines.push("- (none)");
  }
  lines.push("", "Skipped:");
  if (skipped.length) for (const item of skipped) lines.push(`- \`${item.doc}\` — ${item.reason}`);
  else lines.push("- (none)");
  if (newEntries.length) {
    lines.push("", "Manifest entries added:");
    for (const entry of newEntries) {
      lines.push(`- \`${entry.paths.join("`, `")}\` → \`${entry.docs.join("`, `")}\``);
    }
  }
  if (uncovered.length) {
    lines.push("", "Uncovered dotfiles paths:");
    for (const path of uncovered) lines.push(`- \`${path}\``);
  }
  return `${lines.join("\n")}\n`;
}

// ---------------------------------------------------------------------------
// 7. build + lint

async function buildAndLint(docs, originals) {
  await run("node", [BUILD_SCRIPT]);
  if (!docs.length) return { reverted: [] };
  const lint = await run("bunx", [LINT_PIN, ...docs], { allowFailure: true });
  if (lint.code === 0) return { reverted: [] };

  const failing = new Set();
  for (const line of `${lint.stdout}\n${lint.stderr}`.split("\n")) {
    const match = line.match(/^(\S+\.md):\d+/);
    if (match) failing.add(match[1].replace(/^\.\//, ""));
  }
  // If the report cannot be attributed, be conservative and revert every rewrite.
  const attributable = docs.filter((doc) => failing.has(doc));
  if (failing.size && !attributable.length) {
    throw new Error(`markdownlint failed outside the rewritten pages\n${lint.stdout || lint.stderr}`);
  }
  const toRevert = failing.size ? attributable : docs;
  for (const doc of toRevert) writeInRepo(doc, originals.get(doc));
  if (toRevert.length) {
    console.log(`! markdownlint failed; reverted ${toRevert.length} page(s) and rebuilt`);
    await run("node", [BUILD_SCRIPT]);
  }
  return { reverted: toRevert };
}

// ---------------------------------------------------------------------------
// 8. ship
async function ship({ manifest, base, head, docs, dryRun, summary }) {
  const message = [
    `docs-sync: dotfiles ${base.slice(0, 7)}..${head.slice(0, 7)}`,
    "",
    ...summary,
    "",
    `Baseline: ${base}..${head}`,
  ].join("\n");

  if (dryRun) {
    console.log("\n--dry-run: no manifest update, no commit, no push. Proposed commit:");
    console.log(message.split("\n").map((line) => `  ${line}`).join("\n"));
    return;
  }

  manifest.last_synced_sha = head;
  writeInRepo(MANIFEST_REL, `${JSON.stringify(manifest, null, 2)}\n`);
  await git(["add", "--", ...docs, "docs-site", "log.md", "index.md", MANIFEST_REL]);
  const messageFile = join(tmpdir(), `docs-sync-${process.pid}.txt`);
  writeFileSync(messageFile, message);
  try {
    await git(["commit", "-F", messageFile]);
  } finally {
    rmSync(messageFile, { force: true });
  }
  try {
    await git(["push", "origin", "main"]);
  } catch (err) {
    // Baseline only advances on a successful push: put the old sha back into the
    // still-unpushed commit so a rerun retries the same range.
    manifest.last_synced_sha = base;
    writeInRepo(MANIFEST_REL, `${JSON.stringify(manifest, null, 2)}\n`);
    await git(["add", "--", MANIFEST_REL]);
    await git(["commit", "--amend", "--no-edit"]);
    throw new Error(`push failed; baseline kept at ${base.slice(0, 7)}, rerun retries the range\n${err.message}`);
  }
}

// ---------------------------------------------------------------------------
// orchestration

async function main() {
  const { values } = parseArgs({
    options: { since: { type: "string" }, "dry-run": { type: "boolean" }, help: { type: "boolean", short: "h" } },
    allowPositionals: false,
  });
  if (values.help) {
    console.log(USAGE);
    return;
  }
  const dryRun = Boolean(values["dry-run"]);
  const manifest = loadManifest();
  const dotfiles = resolveDotfiles(manifest);
  const lockPath = acquireLock();
  // Ctrl+C skips `finally`; drop the lock so the next run is not refused.
  for (const signal of ["SIGINT", "SIGTERM"]) {
    process.once(signal, () => {
      rmSync(lockPath, { force: true });
      process.exit(130);
    });
  }
  try {
    await preflight(dotfiles);
    const { base, head, changed } = await resolveRange(dotfiles, manifest, values.since);
    console.log(`range ${base.slice(0, 7)}..${head.slice(0, 7)}: ${changed.length} relevant dotfiles path(s)`);
    if (!changed.length) {
      console.log("nothing to sync");
      return;
    }

    const mapped = mapToDocs(changed, manifest.entries);
    let uncovered = mapped.uncovered;
    let newEntries = [];
    if (uncovered.length) {
      // A failed map call leaves the manifest as it was; the run goes on with existing entries.
      const proposed = await proposeEntries({ uncovered, manifest }).catch((err) => {
        console.log(`! map call failed, continuing with the existing manifest: ${failureReason(err)}`);
        return { added: [], uncovered };
      });
      newEntries = proposed.added;
      uncovered = proposed.uncovered;
      for (const entry of newEntries) console.log(`+ manifest ${entry.paths.join(", ")} -> ${entry.docs.join(", ")}`);
      if (!newEntries.length) console.log(`! no manifest entry proposed for ${uncovered.length} path(s)`);
    }
    const docs = mapToDocs(changed, manifest.entries).docs
      .filter((item) => existsSync(join(ROOT, item.doc)))
      .sort((a, b) => a.doc.localeCompare(b.doc));

    const keys = resolvableKeys();
    const originals = new Map();
    const rewritten = docs.length
      ? await pool(docs, PI_CONCURRENCY, (item) => rewriteOne({ dotfiles, base, item, keys, originals }))
      : [];
    const accepted = rewritten.filter((item) => item.ok);
    const skipped = rewritten.filter((item) => !item.ok);
    for (const item of skipped) console.log(`- skipped ${item.doc}: ${item.reason}`);

    // Lint the rewrites before bookkeeping so a reverted page never lands in
    // index.md or log.md as "updated".
    for (const item of accepted) {
      writeInRepo(item.doc, replaceBody(bumpUpdated(originals.get(item.doc), today()), item.rewrite));
    }
    const { reverted } = await buildAndLint(accepted.map((item) => item.doc), originals);
    const shipped = accepted.filter((item) => !reverted.includes(item.doc));
    for (const doc of reverted) skipped.push({ doc, reason: "markdownlint" });

    for (const item of shipped) {
      if (item.doc.startsWith("wiki/")) {
        const indexText = readFileSync(join(ROOT, "index.md"), "utf8");
        writeInRepo("index.md", updateIndexLine(indexText, item.doc, item.index));
      }
    }
    const before = readFileSync(join(ROOT, "log.md"), "utf8").replace(/\s*$/, "");
    writeInRepo("log.md", `${before}\n\n${logEntry({
      base, head, accepted: shipped, skipped, uncovered, newEntries,
    })}`);

    // log.md and index.md are script-generated, so a lint error there is a bug
    // in this script: fail loudly instead of reverting.
    const metaLint = await run("bunx", [LINT_PIN, "log.md", "index.md"], { allowFailure: true });
    if (metaLint.code !== 0) {
      throw new Error(`markdownlint failed on log.md/index.md\n${metaLint.stdout || metaLint.stderr}`);
    }

    console.log(`\nupdated ${shipped.length}, skipped ${skipped.length}, uncovered ${uncovered.length}`);
    await ship({
      manifest, base, head, docs: shipped.map((item) => item.doc), dryRun,
      summary: [
        ...shipped.map((item) => `updated: ${item.doc}`),
        ...skipped.map((item) => `skipped: ${item.doc} (${item.reason})`),
        ...(uncovered.length ? [`uncovered: ${uncovered.join(", ")}`] : []),
      ],
    });
  } finally {
    rmSync(lockPath, { force: true });
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((err) => {
    console.error(`docs-sync: ${err.message}`);
    process.exitCode = 1;
  });
}
