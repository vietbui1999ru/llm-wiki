// Tests for the pure helpers in docs-sync.mjs. Run:
//   node --test claude-setup/scripts/docs-sync.test.mjs
import test from "node:test";
import assert from "node:assert/strict";

import {
  acceptRewrite,
  bumpUpdated,
  deletionRatio,
  execClosed,
  isExcluded,
  mapToDocs,
  parseSentinels,
  unresolvedWikilinks,
} from "./docs-sync.mjs";

const ENTRIES = [
  { paths: ["shared/skills/delegate-pi/**"], docs: ["wiki/entities/pi-agent.md", "docs/workflows.md"] },
  { paths: ["scripts/ac-run", "scripts/floor-guard"], docs: ["docs/workflows.md"] },
];

test("mapToDocs: globs route changed paths to their docs", () => {
  const { docs, uncovered } = mapToDocs(
    [
      "shared/skills/delegate-pi/SKILL.md",
      "shared/skills/delegate-pi/nested/deep.md",
      "scripts/floor-guard",
      "README.md",
    ],
    ENTRIES,
  );
  assert.deepEqual(docs.map((item) => item.doc), ["wiki/entities/pi-agent.md", "docs/workflows.md"]);
  assert.deepEqual(docs[0].paths, [
    "shared/skills/delegate-pi/SKILL.md",
    "shared/skills/delegate-pi/nested/deep.md",
  ]);
  assert.deepEqual(docs[1].paths, [
    "scripts/floor-guard",
    "shared/skills/delegate-pi/SKILL.md",
    "shared/skills/delegate-pi/nested/deep.md",
  ]);
  assert.deepEqual(uncovered, ["README.md"]);
});

test("mapToDocs: no entries means everything is uncovered", () => {
  const { docs, uncovered } = mapToDocs(["shared/skills/pele/SKILL.md"], []);
  assert.deepEqual(docs, []);
  assert.deepEqual(uncovered, ["shared/skills/pele/SKILL.md"]);
});

test("mapToDocs: a prefix glob does not swallow sibling directories", () => {
  const { uncovered } = mapToDocs(["shared/skills/delegate-pi-old/SKILL.md"], ENTRIES);
  assert.deepEqual(uncovered, ["shared/skills/delegate-pi-old/SKILL.md"]);
});

test("isExcluded: worktrees, superpowers specs and backups are out of scope", () => {
  assert.equal(isExcluded(".claude/worktrees/foo/docs/x.md"), true);
  assert.equal(isExcluded("docs/superpowers/specs/x.md"), true);
  assert.equal(isExcluded("scripts/ac-run.bak"), true);
  assert.equal(isExcluded("top.bak"), true);
  assert.equal(isExcluded("docs/workflows.md"), false);
  assert.equal(isExcluded("scripts/ac-run"), false);
});

test("parseSentinels: body between the markers plus the INDEX line", () => {
  const reply = [
    "Here is the rewrite:",
    "<<<DOCS_SYNC_BODY>>>",
    "# Title",
    "",
    "Body paragraph.",
    "<<<DOCS_SYNC_END>>>",
    "INDEX: How the harness provisions each agent config",
  ].join("\n");
  assert.deepEqual(parseSentinels(reply), {
    body: "# Title\n\nBody paragraph.\n",
    index: "How the harness provisions each agent config",
  });
});

test("parseSentinels: missing INDEX yields an empty description", () => {
  assert.deepEqual(parseSentinels("<<<DOCS_SYNC_BODY>>>\nx\n<<<DOCS_SYNC_END>>>"), { body: "x\n", index: "" });
});

test("parseSentinels: malformed or absent markers yield null", () => {
  assert.equal(parseSentinels("no markers at all"), null);
  assert.equal(parseSentinels("<<<DOCS_SYNC_BODY>>>\nbody without an end"), null);
  assert.equal(parseSentinels(undefined), null);
});

test("deletionRatio: unchanged, fully replaced and half replaced bodies", () => {
  assert.equal(deletionRatio("a\nb\nc\nd", "a\nb\nc\nd"), 0);
  assert.equal(deletionRatio("a\nb\nc\nd", "a\nb\nc\nd\ne"), 0);
  assert.equal(deletionRatio("a\nb\nc\nd", "x"), 1);
  assert.equal(deletionRatio("a\nb", "a\nx"), 0.5);
  assert.equal(deletionRatio("", "anything"), 0);
});

test("unresolvedWikilinks: resolves aliases and anchors, skips code", () => {
  const known = new Set(["concepts/agent-harness", "agent-harness", "docs/workflows"]);
  const body = [
    "See [[concepts/agent-harness]] and [[agent-harness|the harness]].",
    "Anchor: [[concepts/agent-harness#failure-modes]].",
    "Broken: [[concepts/missing]] here.",
    "```bash",
    "echo [[not-a-page]]",
    "```",
    "Inline `[[also-not-a-page]]` stays code.",
  ].join("\n");
  assert.deepEqual(unresolvedWikilinks(body, known), ["concepts/missing"]);
  assert.deepEqual(unresolvedWikilinks("[[docs/workflows]]", ["docs/workflows"]), []);
});

test("bumpUpdated: rewrites the frontmatter updated field only", () => {
  const page = [
    "---",
    'title: "X"',
    "type: concept",
    "created: 2026-10-01",
    "updated: 2026-10-02",
    "---",
    "",
    "# X",
    "",
    "updated: this body line is not frontmatter",
    "",
  ].join("\n");
  const bumped = bumpUpdated(page, "2026-10-20");
  assert.equal(bumped, page.replace("updated: 2026-10-02", "updated: 2026-10-20"));
  assert.match(bumped, /created: 2026-10-01/);
});

test("bumpUpdated: adds the field when the frontmatter lacks it", () => {
  assert.equal(
    bumpUpdated("---\ntitle: Y\n---\n\nBody\n", "2026-10-20"),
    "---\ntitle: Y\nupdated: 2026-10-20\n---\n\nBody\n",
  );
});

test("bumpUpdated: refuses a page without frontmatter", () => {
  assert.throws(() => bumpUpdated("# no frontmatter\n", "2026-10-20"), /no frontmatter/);
});

test("execClosed: a child that reads stdin to EOF returns instead of hanging", async () => {
  // `cat` waits for stdin EOF exactly like `pi -p`; an unclosed pipe hung docs-sync.
  const { stdout } = await execClosed("cat", [], { timeout: 5_000 });
  assert.equal(stdout, "");
});

const reply = (body) => `<<<DOCS_SYNC_BODY>>>\n${body}<<<DOCS_SYNC_END>>>\nINDEX: refreshed`;
const PAGE = Array.from({ length: 10 }, (_, i) => `line ${i} see [[pi-agent]]`).join("\n") + "\n";
const KEYS = new Set(["pi-agent"]);

test("acceptRewrite: accepts a modest edit and returns the index line", () => {
  const edited = PAGE.replace("line 0", "line zero");
  assert.deepEqual(acceptRewrite(PAGE, reply(edited), KEYS), { ok: true, rewrite: edited, index: "refreshed" });
});

test("acceptRewrite: rejects missing sentinels, no-op and truncation", () => {
  assert.equal(acceptRewrite(PAGE, "no markers", KEYS).reason, "sentinels missing");
  assert.equal(acceptRewrite(PAGE, reply(PAGE), KEYS).reason, "body unchanged");
  const cut = PAGE.split("\n").slice(0, 3).join("\n") + "\n";
  assert.match(acceptRewrite(PAGE, reply(cut), KEYS).reason, /likely truncated/);
});

test("acceptRewrite: rejects near-total replacement and invented wikilinks", () => {
  const replaced = PAGE.split("\n").map((l, i) => (i < 9 ? `new ${i}` : l)).join("\n");
  assert.match(acceptRewrite(PAGE, reply(replaced), KEYS).reason, /cap 75%/);
  const invented = PAGE.replace("[[pi-agent]]", "[[made-up-page]]");
  assert.match(acceptRewrite(PAGE, reply(invented), KEYS).reason, /made-up-page/);
});
