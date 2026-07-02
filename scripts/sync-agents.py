#!/usr/bin/env python3
"""sync-agents.py — single-source-of-truth agent generator for llm-wiki.

Reads canonical agent bodies from claude-setup/agents/<name>.md and emits
.opencode/agents/<name>.md with OpenCode frontmatter + the shared body.

This ends the drift between claude-setup/agents and .opencode/agents: the body
lives once in claude-setup (Claude's source), and OpenCode gets the SAME body
with only the frontmatter swapped to OpenCode's vocabulary (mode/model/color/
permission). harness-agnostic by construction.

Per-harness overrides: if .opencode/agents/<name>.md.overrides-body exists,
that file's body replaces the canonical body for the OpenCode emit only — used
for agents whose routing is irreducibly harness-specific (e.g. agent-delegator's
model-ID routing table). The override file is body-only (no frontmatter).

Idempotent: re-running produces byte-identical output. Unsafe changes (body
edits made directly in .opencode/agents that diverge from canonical) are
detected and reported before overwrite — run with --force to accept.

Usage:
  scripts/sync-agents.py            # generate, fail on drift
  scripts/sync-agents.py --force    # generate, overwrite drift
  scripts/sync-agents.py --check    # dry-run, report drift, exit nonzero if any
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "claude-setup" / "agents"      # canonical source (Claude frontmatter + body)
OC = ROOT / ".opencode" / "agents"            # emit target (OpenCode frontmatter + body)

# Per-agent OpenCode frontmatter. Mirrors the existing .opencode/agents/*.md
# frontmatter so the swap is mechanical. Keys: model (opencode-go full ID),
# color, temperature (optional), permission {edit,websearch,bash}. mode is
# always "subagent". description is pulled from the canonical file (kept in
# sync by the description-rewrite pass) so it's never duplicated here.
OC_FRONTMATTER: dict[str, dict] = {
    "agent-delegator":          {"model": "opencode-go/deepseek-v4-pro",   "color": "#673AB7", "permission": {"edit": "deny",  "websearch": "deny"}},
    "architecture-reviewer":    {"model": "opencode-go/deepseek-v4-pro",   "color": "#7E57C2", "permission": {"edit": "deny",  "websearch": "deny"}},
    "backend-debug-tester":     {"model": "opencode-go/kimi-k2.7-code",   "color": "#26A69A", "permission": {"edit": "allow", "websearch": "deny", "bash": "allow"}},
    "cmd-executor":             {"model": "opencode-go/deepseek-v4-flash", "color": "#8BC34A", "permission": {"edit": "deny",  "websearch": "deny", "bash": "allow"}},
    "code-reviewer":            {"model": "opencode-go/deepseek-v4-pro",   "color": "#EF5350", "permission": {"edit": "deny",  "websearch": "deny"}},
    "code-writer-fast":         {"model": "opencode-go/deepseek-v4-flash", "color": "#66BB6A", "permission": {"edit": "allow", "websearch": "deny", "bash": "allow"}},
    "code-writer":              {"model": "opencode-go/kimi-k2.7-code",   "color": "#2196F3", "permission": {"edit": "allow", "websearch": "deny", "bash": "allow"}},
    "design-critic":            {"model": "opencode-go/kimi-k2.7-code",   "color": "#FF7043", "permission": {"edit": "deny",  "websearch": "deny"}, "temperature": 0.6},
    "design-explorer":          {"model": "opencode-go/kimi-k2.7-code",   "color": "#9C27B0", "permission": {"edit": "deny",  "websearch": "deny"}, "temperature": 0.7},
    "docs-writer":              {"model": "opencode-go/kimi-k2.7-code",   "color": "#78909C", "permission": {"edit": "allow", "websearch": "deny", "bash": "allow"}},
    "explore":                  {"model": "opencode-go/deepseek-v4-flash", "color": "#B0BEC5", "permission": {"edit": "deny",  "websearch": "deny", "bash": "allow"}},
    "frontend-debug-tester":    {"model": "opencode-go/kimi-k2.7-code",   "color": "#42A5F5", "permission": {"edit": "allow", "websearch": "deny", "bash": "allow"}},
    "infra-decision-maker":     {"model": "opencode-go/deepseek-v4-pro",   "color": "#5C6BC0", "permission": {"edit": "deny",  "websearch": "deny"}},
    "production-platform-devops":{"model": "opencode-go/kimi-k2.7-code",   "color": "#FFA726", "permission": {"edit": "allow", "websearch": "deny", "bash": "allow"}},
    "project-health-monitor":   {"model": "opencode-go/deepseek-v4-flash", "color": "#26C6DA", "permission": {"edit": "deny",  "websearch": "deny", "bash": "allow"}},
    "security-auditor":         {"model": "opencode-go/deepseek-v4-pro",   "color": "#E53935", "permission": {"edit": "deny",  "websearch": "deny"}},
    "session-report-generator": {"model": "opencode-go/deepseek-v4-flash", "color": "#78909C", "permission": {"edit": "deny",  "websearch": "deny", "bash": "allow"}},
    "visual-verifier":          {"model": "opencode-go/kimi-k2.7-code",   "color": "#E91E63", "permission": {"edit": "deny",  "websearch": "deny", "bash": "allow"}},
    # plan-writer: OpenCode-only (no Claude canonical). Lives as a real file in
    # .opencode/agents only; generator passes it through unchanged.
}

OC_ONLY = {"plan-writer"}  # OpenCode-only agents, not emitted from canonical


def split_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter lines joined, body) — frontmatter is the raw block between --- lines."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return "", text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return "", text
    fm = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1 :]).lstrip("\n")
    return fm, body


def fm_field(fm_text: str, key: str) -> str | None:
    for line in fm_text.split("\n"):
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip()
    return None


def render_oc_frontmatter(name: str, description: str) -> str:
    spec = OC_FRONTMATTER[name]
    lines = ["---", f'name: "{name}"', f"description: {description}", "mode: subagent", f'model: "{spec["model"]}"', f'color: "{spec["color"]}"']
    if "temperature" in spec:
        lines.append(f"temperature: {spec['temperature']}")
    perm = spec["permission"]
    lines.append("permission:")
    for k in ("edit", "bash", "websearch"):
        if k in perm:
            lines.append(f"  {k}: {perm[k]}")
    lines.append("---")
    return "\n".join(lines)


def project_health_monitor_reconcile(body: str) -> str:
    """project-health-monitor had drifted; canonical is the source of truth.
    No body transform needed — canonical already reconciled. Kept as a seam
    in case future per-agent body normalization is required."""
    return body


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="overwrite even if .opencode body drifted from canonical")
    ap.add_argument("--check", action="store_true", help="dry-run: report drift, exit nonzero if any")
    args = ap.parse_args()

    OC.mkdir(parents=True, exist_ok=True)
    drift: list[str] = []
    emitted: list[str] = []
    skipped: list[str] = []

    for name in sorted(OC_FRONTMATTER):
        canon_path = CANON / f"{name}.md"
        if not canon_path.exists():
            skipped.append(f"{name}: canonical missing")
            continue
        canon_text = canon_path.read_text(encoding="utf-8")
        canon_fm, canon_body = split_frontmatter(canon_text)
        desc = fm_field(canon_fm, "description")
        if not desc:
            skipped.append(f"{name}: no description in canonical")
            continue

        body = project_health_monitor_reconcile(canon_body)

        # per-harness body override
        override = OC / f"{name}.md.overrides-body"
        if override.exists():
            body = override.read_text(encoding="utf-8").lstrip("\n")

        out = render_oc_frontmatter(name, desc) + "\n\n" + body.rstrip() + "\n"

        oc_path = OC / f"{name}.md"
        if oc_path.exists():
            existing = oc_path.read_text(encoding="utf-8")
            _, existing_body = split_frontmatter(existing)
            # drift = existing body differs from what we'd emit (and no override)
            if not override.exists() and existing_body.rstrip() != canon_body.rstrip() and existing.rstrip() != out.rstrip():
                drift.append(f"{name}: .opencode body drifted from canonical (use --force to overwrite, or commit the body edit into claude-setup/agents/{name}.md)")
                if not args.force:
                    continue
        oc_path.write_text(out, encoding="utf-8")
        emitted.append(name)

    for name in sorted(OC_ONLY):
        p = OC / f"{name}.md"
        if p.exists():
            emitted.append(f"{name} (opencode-only, passthrough)")

    print(f"emitted: {len(emitted)}")
    for e in emitted:
        print(f"  ✓ {e}")
    if skipped:
        print(f"skipped: {len(skipped)}")
        for s in skipped:
            print(f"  - {s}")
    if drift:
        print(f"DRIFT: {len(drift)}")
        for d in drift:
            print(f"  ! {d}")
        if args.check or not args.force:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())