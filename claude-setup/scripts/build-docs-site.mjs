#!/usr/bin/env node
// build-docs-site.mjs — transpile the LLM wiki (.md + [[wikilinks]]) into a
// Mintlify-ready MDX site under docs-site/.
//
// Scope: "Reference + guides" — concepts, patterns, syntheses, comparisons,
// systems, entities, plus the onboarding/reference/architecture/workflow guides.
// Per-source summaries/ and the mistakes/ system are intentionally excluded.
//
// What it does:
//   - slims each page's frontmatter to { title, description } (Mintlify's fields)
//   - rewrites [[dir/slug]] and [[dir/slug|alias]] into MDX links, SKIPPING fenced
//     and inline code spans (the wiki contains bash `[[ ... ]]` inside code blocks)
//   - unresolved links (e.g. to excluded summaries) degrade to plain text
//   - generates a landing index.mdx and a docs.json with sidebar navigation
//
// Usage:  node claude-setup/scripts/build-docs-site.mjs
// Source of truth stays in wiki/*.md; this only writes docs-site/.

import { readFileSync, writeFileSync, mkdirSync, rmSync, readdirSync, existsSync } from "node:fs";
import { dirname, join, basename } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const OUT = join(ROOT, "docs-site");

// Wiki subdirectories to publish, in sidebar order, with display labels.
const WIKI_DIRS = [
  ["concepts", "Concepts"],
  ["patterns", "Patterns"],
  ["systems", "Systems"],
  ["syntheses", "Syntheses"],
  ["comparisons", "Comparisons"],
  ["entities", "Entities"],
];

// Standalone guide pages: { src relative to ROOT, out site-path (no extension) }.
const GUIDES = [
  { src: "ONBOARDING.md", out: "guides/onboarding" },
  { src: "GUIDE.md", out: "guides/reference" },
  { src: "docs/architecture.md", out: "guides/architecture" },
  { src: "docs/workflows.md", out: "guides/workflows" },
];

// ---------------------------------------------------------------------------
// helpers

const humanize = (slug) =>
  slug.replace(/[-_]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

function parseFrontmatter(raw) {
  if (!raw.startsWith("---\n")) return { fm: {}, body: raw };
  const end = raw.indexOf("\n---", 4);
  if (end === -1) return { fm: {}, body: raw };
  const block = raw.slice(4, end);
  const body = raw.slice(end + 4).replace(/^\r?\n/, "");
  const fm = {};
  for (const line of block.split("\n")) {
    const m = line.match(/^([A-Za-z_]+):\s*(.*)$/);
    if (m && m[2] !== "") fm[m[1]] = m[2].replace(/^["']|["']$/g, "");
  }
  return { fm, body };
}

// First real prose line → description. Strips markup; truncates ~160 chars.
function deriveDescription(body) {
  for (let line of body.split("\n")) {
    line = line.trim();
    if (!line || line.startsWith("#") || line.startsWith("```") ||
        line.startsWith("|") || line.startsWith(">") || line.startsWith("-")) continue;
    line = line
      .replace(/\[\[([^\]|]+)\|([^\]]+)\]\]/g, "$2")
      .replace(/\[\[([^\]]+)\]\]/g, (_, t) => humanize(basename(t)))
      .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
      .replace(/[`*_]/g, "")
      .replace(/\s+/g, " ")
      .trim();
    if (line.length < 20) continue;
    return (line.length > 160 ? line.slice(0, 157).trimEnd() + "…" : line)
      .replace(/"/g, "'");
  }
  return "";
}

// ---------------------------------------------------------------------------
// pass 1 — build the link map: every publishable page is a valid wikilink target.
// key forms: "dir/slug" and bare "slug" (no cross-dir collisions, verified).

const linkMap = new Map(); // key -> { path, title }
const files = []; // { absPath, outPath, title }

for (const [dir] of WIKI_DIRS) {
  const abs = join(ROOT, "wiki", dir);
  if (!existsSync(abs)) continue;
  for (const f of readdirSync(abs).sort()) { // sort → deterministic output across filesystems
    if (!f.endsWith(".md")) continue;
    const slug = f.replace(/\.md$/, "");
    const { fm } = parseFrontmatter(readFileSync(join(abs, f), "utf8"));
    const title = fm.title || humanize(slug);
    const sitePath = `/${dir}/${slug}`;
    const entry = { path: sitePath, title };
    linkMap.set(`${dir}/${slug}`, entry);
    if (!linkMap.has(slug)) linkMap.set(slug, entry);
    files.push({ absPath: join(abs, f), outPath: `${dir}/${slug}`, title, fm });
  }
}

// ---------------------------------------------------------------------------
// wikilink rewriting — operates only on non-code text.

function rewriteWikilinks(text) {
  return text.replace(/\[\[([^\]]+)\]\]/g, (_, inner) => {
    const [rawTarget, alias] = inner.split("|");
    const target = rawTarget.trim();
    const hit = linkMap.get(target) || linkMap.get(basename(target));
    const label = (alias && alias.trim()) || (hit && hit.title) || humanize(basename(target));
    return hit ? `[${label}](${hit.path})` : label; // unresolved → plain text
  });
}

// MDX parses bare `<` and `{` as JSX. Technical prose is full of `<10%`, `<5k`,
// `k << n`, `{...}` — escape them in non-code text so MDX renders them literally.
// (Real intent to render HTML/JSX in wiki prose: none — verified.)
function escapeMdx(text) {
  return text.replace(/</g, "&lt;").replace(/\{/g, "&#123;");
}

// Rewrite a single non-fenced line, protecting inline `code` spans.
function rewriteLine(line) {
  return line
    .split(/(`[^`]*`)/)
    .map((seg) => (seg.startsWith("`") ? seg : escapeMdx(rewriteWikilinks(seg))))
    .join("");
}

function transformBody(body) {
  let inFence = false;
  return body
    .split("\n")
    .map((line) => {
      if (/^\s*(```|~~~)/.test(line)) { inFence = !inFence; return line; }
      return inFence ? line : rewriteLine(line);
    })
    .join("\n");
}

// ---------------------------------------------------------------------------
// link graph — drives a per-page "local graph" side widget (Obsidian-style).

// internal wikilink targets in a body, skipping fenced + inline code.
function extractInternalLinks(body) {
  const out = new Set();
  let inFence = false;
  for (let line of body.split("\n")) {
    if (/^\s*(```|~~~)/.test(line)) { inFence = !inFence; continue; }
    if (inFence) continue;
    line = line.split(/(`[^`]*`)/).map((s) => (s.startsWith("`") ? "" : s)).join("");
    for (const m of line.matchAll(/\[\[([^\]]+)\]\]/g)) {
      const target = m[1].split("|")[0].trim();
      const hit = linkMap.get(target) || linkMap.get(basename(target));
      if (hit) out.add(hit.path.slice(1)); // -> "dir/slug"
    }
  }
  return out;
}

// resolve guide pages up front so guide↔wiki links join the graph.
const guideFiles = [];
for (const g of GUIDES) {
  const abs = join(ROOT, g.src);
  if (!existsSync(abs)) { console.warn(`! missing guide: ${g.src}`); continue; }
  const { fm, body } = parseFrontmatter(readFileSync(abs, "utf8"));
  const h1 = body.match(/^#\s+(.+)$/m);
  const title = fm.title || (h1 && h1[1]) || humanize(basename(g.out));
  guideFiles.push({ absPath: abs, outPath: g.out, title, group: "guides" });
}

const allPages = [
  ...files.map((f) => ({ absPath: f.absPath, outPath: f.outPath, title: f.title, group: f.outPath.split("/")[0] })),
  ...guideFiles,
];
const nodeMeta = new Map(allPages.map((p) => [p.outPath, { label: p.title, group: p.group }]));

// undirected adjacency (for client-side depth BFS) + directed links (for arrows).
const adj = new Map(allPages.map((p) => [p.outPath, new Set()]));
const directedLinks = [];
const seenEdge = new Set();
for (const p of allPages) {
  const { body } = parseFrontmatter(readFileSync(p.absPath, "utf8"));
  for (const tgt of extractInternalLinks(body)) {
    if (tgt === p.outPath || !nodeMeta.has(tgt)) continue;
    adj.get(p.outPath).add(tgt);
    adj.get(tgt).add(p.outPath);
    const k = `${p.outPath}>${tgt}`;
    if (!seenEdge.has(k)) { seenEdge.add(k); directedLinks.push({ source: p.outPath, target: tgt }); }
  }
}
const degree = new Map([...adj].map(([id, set]) => [id, set.size]));

// Every page embeds the FULL graph; the widget filters to a depth-N neighbourhood
// of the current node client-side. Root/landing (cur = null) shows the whole graph.
// Node size uses sqrt(degree) so hubs don't dominate. All visuals are slider-tunable.
const fullNodes = allPages.map((p) => ({
  id: p.outPath,
  label: p.title,
  group: p.group,
  val: 1 + Math.sqrt(degree.get(p.outPath) || 0),
}));

const FG_SRC = "https://cdn.jsdelivr.net/npm/force-graph@1.51.4/dist/force-graph.min.js";
const FG_SRI = "sha384-Hm6GpQcTNI5VqGgGS7lLxTGtEFcxu/kOVV0B7ozIZRu9blWVvigv5httJQZ2qZmY";

// Self-contained graph panel (one HTML doc per page; data + center + max-depth
// injected via tokens). Nested pages embed only their bounded neighbourhood; the
// root page (cur=null) embeds the whole graph. The animation loop pauses when the
// pointer is not over the widget, so it never repaints during page scroll.
const WIDGET_HTML = `<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;height:100%;background:#0f1117;overflow:hidden;font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}
#g{width:100%;height:100%}
#hd{position:absolute;top:0;left:0;right:30px;height:22px;display:flex;align-items:center;gap:6px;padding:0 10px;color:#aeb3c2;font-size:10px;letter-spacing:.08em;text-transform:uppercase;z-index:6;cursor:move;user-select:none;touch-action:none;background:linear-gradient(#0f1117cc,#0f111700)}
#gear{position:absolute;top:5px;right:7px;z-index:7;cursor:pointer;color:#aeb3c2;background:#1b1e27;border:1px solid #2b2f3a;border-radius:6px;width:22px;height:22px;display:flex;align-items:center;justify-content:center;font-size:12px;user-select:none}
#panel{position:absolute;top:31px;right:7px;z-index:7;background:rgba(22,25,34,.96);border:1px solid #2b2f3a;border-radius:8px;padding:6px 9px 9px;display:none;width:150px;color:#c9cdd8;font-size:10px}
#panel.open{display:block}
#panel label{display:flex;justify-content:space-between;margin:7px 0 1px;color:#9aa0b0}
#panel input[type=range]{width:100%;margin:0}
#panel .row{display:flex;align-items:center;gap:6px;margin-top:8px;color:#c9cdd8}
</style><script src="${FG_SRC}" integrity="${FG_SRI}" crossorigin="anonymous"></script></head>
<body><div id="hd">Graph</div><div id="gear">⚙</div>
<div id="panel">
<label>Node size<span id="vns"></span></label><input id="ns" type="range" min="0.6" max="6" step="0.2">
<label>Link width<span id="vlw"></span></label><input id="lw" type="range" min="0" max="3" step="0.1">
<label>Label size<span id="vts"></span></label><input id="ts" type="range" min="0" max="8" step="0.5">
<label>Label opacity<span id="vto"></span></label><input id="to" type="range" min="0" max="1" step="0.05">
<div id="depthRow"><label>Depth<span id="vd"></span></label><input id="dp" type="range" min="1" max="5" step="1"></div>
<div class="row"><input id="ar" type="checkbox"><span>Directional arrows</span></div>
</div>
<div id="g"></div>
<script>
const NODES=__NODES__,LINKS=__LINKS__,CUR=__CUR__,MAXD=__MAXD__;
const C={concepts:'#8B7CF6',patterns:'#0D9373',systems:'#E0567C',syntheses:'#E2A03F',comparisons:'#3B82F6',entities:'#14B8A6',guides:'#9CA3AF'};
function lid(x){return (x&&x.id!==undefined)?x.id:x;}
const ADJ=new Map(NODES.map(function(n){return [n.id,new Set()];}));
LINKS.forEach(function(l){var s=lid(l.source),t=lid(l.target);if(ADJ.has(s)&&ADJ.has(t)){ADJ.get(s).add(t);ADJ.get(t).add(s);}});
var opt={ns:1.8,lw:0.6,ts:3.5,to:0.75,dp:__DEPTH__,ar:false};
function visible(){
 if(!CUR)return {nodes:NODES,links:LINKS};
 var dist=new Map([[CUR,0]]),fr=[CUR];
 for(var d=1;d<=opt.dp;d++){var nx=[];fr.forEach(function(u){(ADJ.get(u)||[]).forEach(function(v){if(!dist.has(v)){dist.set(v,d);nx.push(v);}});});fr=nx;}
 var keep=new Set(dist.keys());
 return {nodes:NODES.filter(function(n){return keep.has(n.id);}),links:LINKS.filter(function(l){return keep.has(lid(l.source))&&keep.has(lid(l.target));})};
}
var el=document.getElementById('g');
var G=ForceGraph()(el).backgroundColor('#0f1117').nodeId('id')
 .warmupTicks(24).cooldownTicks(70).autoPauseRedraw(true)
 .nodeColor(function(n){return C[n.group]||'#9CA3AF';}).nodeLabel('label').nodeVal(function(n){return n.val;})
 .linkColor(function(){return 'rgba(255,255,255,0.12)';})
 .nodeRelSize(opt.ns).linkWidth(opt.lw)
 .linkDirectionalArrowLength(0).linkDirectionalArrowRelPos(1).linkDirectionalArrowColor(function(){return 'rgba(255,255,255,0.4)';})
 .nodeCanvasObjectMode(function(){return 'after';})
 .nodeCanvasObject(function(n,ctx,scale){var r=opt.ns*Math.sqrt(n.val||1);
  if(n.id===CUR){ctx.beginPath();ctx.arc(n.x,n.y,r+1.6,0,6.283);ctx.strokeStyle='#fff';ctx.lineWidth=1.2/scale;ctx.stroke();}
  if(opt.to>0&&opt.ts>0){var t=n.label.length>28?n.label.slice(0,26)+'…':n.label;ctx.globalAlpha=opt.to;ctx.font=((n.id===CUR?opt.ts+1:opt.ts))+'px ui-sans-serif,sans-serif';ctx.fillStyle=(n.id===CUR)?'#ffffff':'#aab0c0';ctx.textAlign='center';ctx.textBaseline='top';ctx.fillText(t,n.x,n.y+r+1.5);ctx.globalAlpha=1;}})
 .onNodeClick(function(n){if(window.top){window.top.location.href='/'+n.id;}});
G.graphData(visible());G.d3VelocityDecay(0.4);
function fit(){G.zoomToFit(400,20);}
setTimeout(fit,350);setTimeout(fit,1100);
// Stop the render/sim loop while idle so the fixed widget never repaints during
// parent-page scroll; resume only while the pointer is over the widget.
var pt;function pause(){G.pauseAnimation();}function resume(){G.resumeAnimation();}
function idle(ms){clearTimeout(pt);pt=setTimeout(pause,ms);}
document.body.addEventListener('pointerenter',function(){clearTimeout(pt);resume();});
document.body.addEventListener('pointerleave',function(){idle(250);});
addEventListener('resize',function(){resume();G.zoomToFit(0,20);idle(700);});
idle(2000);
function apply(re){resume();G.nodeRelSize(opt.ns).linkWidth(opt.lw).linkDirectionalArrowLength(opt.ar?2.6:0);if(re){G.graphData(visible());setTimeout(fit,450);}idle(re?2200:1400);}
function bind(id,key,fmt,re){var e=document.getElementById(id),o=document.getElementById('v'+id);e.value=opt[key];if(o)o.textContent=fmt(opt[key]);e.addEventListener('input',function(){opt[key]=parseFloat(e.value);if(o)o.textContent=fmt(opt[key]);apply(re);});}
bind('ns','ns',function(v){return v.toFixed(1);},false);
bind('lw','lw',function(v){return v.toFixed(1);},false);
bind('ts','ts',function(v){return v.toFixed(1);},false);
bind('to','to',function(v){return v.toFixed(2);},false);
var dE=document.getElementById('dp'),dO=document.getElementById('vd');dE.max=MAXD;dE.value=opt.dp;dO.textContent=opt.dp;dE.addEventListener('input',function(){opt.dp=parseInt(dE.value,10);dO.textContent=opt.dp;apply(true);});
if(!CUR)document.getElementById('depthRow').style.display='none';
var aE=document.getElementById('ar');aE.checked=opt.ar;aE.addEventListener('change',function(){opt.ar=aE.checked;apply(false);});
document.getElementById('gear').addEventListener('click',function(){document.getElementById('panel').classList.toggle('open');});
var hd=document.getElementById('hd');hd.textContent='⠿  '+(CUR?'Local graph':'Knowledge graph');
// free-form placement: drag by the header. Default is bottom-right (inline style);
// a moved position is saved per parent-origin and restored on every page.
function clampPos(fe,l,t){var TW=(window.top||window),r=fe.getBoundingClientRect();return [Math.min(Math.max(0,l),Math.max(0,TW.innerWidth-r.width)),Math.min(Math.max(0,t),Math.max(0,TW.innerHeight-r.height))];}
function place(fe,l,t){var p=clampPos(fe,l,t);fe.style.left=p[0]+'px';fe.style.top=p[1]+'px';fe.style.right='auto';fe.style.bottom='auto';}
try{var sp=JSON.parse(localStorage.getItem('llmwiki_graph_pos'));if(sp&&window.frameElement)place(window.frameElement,sp.l,sp.t);}catch(e){if(window.console)console.debug('graph: saved position unavailable',e);}
hd.addEventListener('pointerdown',function(e){var fe=window.frameElement;if(!fe)return;var rect=fe.getBoundingClientRect();var sx=e.screenX,sy=e.screenY,L=rect.left,T=rect.top;place(fe,L,T);hd.setPointerCapture(e.pointerId);
 function mv(ev){place(fe,L+ev.screenX-sx,T+ev.screenY-sy);}
 function up(){if(hd.hasPointerCapture(e.pointerId))hd.releasePointerCapture(e.pointerId);hd.removeEventListener('pointermove',mv);hd.removeEventListener('pointerup',up);try{localStorage.setItem('llmwiki_graph_pos',JSON.stringify({l:parseFloat(fe.style.left),t:parseFloat(fe.style.top)}));}catch(e2){if(window.console)console.debug('graph: could not persist position',e2);}}
 hd.addEventListener('pointermove',mv);hd.addEventListener('pointerup',up);e.preventDefault();});
</script></body></html>`;

// bounded depth-N neighbourhood around a page, for nested-page widgets.
const NEIGH_DEPTH = 3, NEIGH_MAX = 44, NEIGH_DEFAULT = 2;
function buildNeighborhood(id) {
  const dist = new Map([[id, 0]]);
  let fr = [id];
  for (let d = 1; d <= NEIGH_DEPTH; d++) {
    const nx = [];
    for (const u of fr) for (const v of adj.get(u) || []) {
      if (!dist.has(v)) { dist.set(v, d); nx.push(v); }
    }
    fr = nx;
  }
  let ids = [...dist.keys()];
  if (ids.length > NEIGH_MAX) {
    ids = ids.sort((a, b) =>
      (dist.get(a) - dist.get(b)) || ((degree.get(b) || 0) - (degree.get(a) || 0))
    ).slice(0, NEIGH_MAX);
  }
  const keep = new Set(ids);
  const nodes = ids.map((n) => ({
    id: n, label: nodeMeta.get(n).label, group: nodeMeta.get(n).group,
    val: 1 + Math.sqrt(degree.get(n) || 0),
  }));
  const links = directedLinks.filter((l) => keep.has(l.source) && keep.has(l.target));
  return { nodes, links };
}

// Fixed-position graph panel. id=null → whole-graph view (root); else local.
function widgetMarkup(id) {
  const data = id ? buildNeighborhood(id) : { nodes: fullNodes, links: directedLinks };
  const maxd = id ? NEIGH_DEPTH : 5;
  const depth = id ? Math.min(NEIGH_DEFAULT, maxd) : 5;
  const srcdoc = WIDGET_HTML
    .replace("__NODES__", JSON.stringify(data.nodes))
    .replace("__LINKS__", JSON.stringify(data.links))
    .replace("__CUR__", id ? `"${id}"` : "null")
    .replace("__MAXD__", String(maxd))
    .replace("__DEPTH__", String(depth))
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;");
  return `<iframe srcDoc="${srcdoc}" title="Knowledge graph" loading="lazy" style={{position:"fixed",right:"18px",bottom:"18px",width:"320px",height:"340px",border:0,borderRadius:"14px",boxShadow:"0 6px 28px rgba(0,0,0,0.38)",zIndex:50,background:"#0f1117"}} />`;
}

// ---------------------------------------------------------------------------
// emit

function yamlEscape(s) {
  return s.replace(/\\/g, "\\\\").replace(/"/g, '\\"'); // backslash first, then quote
}

function writePage(outPath, title, description, body) {
  const dest = join(OUT, `${outPath}.mdx`);
  mkdirSync(dirname(dest), { recursive: true });
  const fm = [
    "---",
    `title: "${yamlEscape(title)}"`,
    description ? `description: "${yamlEscape(description)}"` : null,
    "---",
    "",
  ].filter((l) => l !== null).join("\n");
  const widget = widgetMarkup(outPath);
  writeFileSync(dest, fm + transformBody(body) + "\n" + (widget ? "\n" + widget + "\n" : ""));
}

rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });

let count = 0;

// wiki pages
for (const file of files) {
  const { body } = parseFrontmatter(readFileSync(file.absPath, "utf8"));
  writePage(file.outPath, file.title, deriveDescription(body), body);
  count++;
}

// guide pages
for (const g of guideFiles) {
  const { body } = parseFrontmatter(readFileSync(g.absPath, "utf8"));
  writePage(g.outPath, g.title, deriveDescription(body), body);
  count++;
}

// landing page
const landing = `---
title: "LLM Wiki"
description: "A compounding, agent-maintained knowledge base on AI agent engineering."
---

<Card title="New here? Start with the onboarding guide" icon="rocket" href="/guides/onboarding">
  How to run this wiki as an agent-first knowledge harness — agent reads, writes, and links;
  you curate and decide.
</Card>

## Explore the knowledge base

<CardGroup cols={2}>
  <Card title="Concepts" icon="lightbulb" href="/concepts/agent-harness">
    Ideas, patterns, and techniques in agent engineering.
  </Card>
  <Card title="Patterns" icon="shapes" href="/patterns/principles">
    A parallel software-engineering reference track.
  </Card>
  <Card title="Systems" icon="diagram-project" href="/systems/distributed-systems">
    System-level design and architecture.
  </Card>
  <Card title="Syntheses" icon="layer-group" href="/syntheses/lean-agentic-workflow">
    Cross-source conclusions and theses.
  </Card>
  <Card title="Entities" icon="cube" href="/entities/opencode">
    Named tools, projects, and people.
  </Card>
  <Card title="Architecture" icon="sitemap" href="/guides/architecture">
    How the harness fits together (diagrams).
  </Card>
</CardGroup>
`;
writeFileSync(join(OUT, "index.mdx"), landing + "\n" + widgetMarkup(null) + "\n");
count++;

// ---------------------------------------------------------------------------
// docs.json navigation

const groups = [
  { group: "Get Started", pages: ["index", "guides/onboarding", "guides/reference"] },
  { group: "Architecture", pages: ["guides/architecture", "guides/workflows"] },
];
for (const [dir, label] of WIKI_DIRS) {
  const pages = files
    .filter((f) => f.outPath.startsWith(`${dir}/`))
    .map((f) => f.outPath)
    .sort();
  if (pages.length) groups.push({ group: label, pages });
}

const docsJson = {
  $schema: "https://mintlify.com/docs.json",
  theme: "mint",
  name: "LLM Wiki",
  description: "A compounding, agent-maintained knowledge base on AI agent engineering.",
  colors: { primary: "#6E56CF", light: "#9E8CFC", dark: "#4C3AAE" },
  navigation: { groups },
};
writeFileSync(join(OUT, "docs.json"), JSON.stringify(docsJson, null, 2) + "\n");

console.log(`✓ wrote ${count} pages + docs.json to docs-site/ (${linkMap.size} link targets)`);
