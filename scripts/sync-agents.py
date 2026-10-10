#!/usr/bin/env python3
"""sync-agents.py — single-source-of-truth agent generator for llm-wiki.

The canonical directory claude-setup/agents/ IS the roster: every
claude-setup/agents/<name>.md is emitted as .opencode/agents/<name>.md with
OpenCode frontmatter + the same body. A name with no canonical file simply
does not exist here — the generator iterates the directory, not a remembered
name list.

OC_PRESETS holds remembered OpenCode settings (model/color/permission/
temperature) keyed by name, for agents that used to exist. When a canonical
file reappears under a preset's name, the preset is applied automatically.
Presets are not a list of agents that must exist.

A canonical file whose name has no preset gets conservative defaults:
mode: subagent, permission all-deny, no color, and a model translated from the
canonical frontmatter's model: field — a Claude tier such as "sonnet" maps
through TIER_TO_OC_MODEL, a provider/model ID passes through, anything else
falls back to DEFAULT_MODEL. A newly added agent never acquires write or shell
access merely because nobody specified it.

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

# Remembered OpenCode settings for agents that used to exist, keyed by name.
# Applied automatically when a canonical claude-setup/agents/<name>.md of that
# name reappears. NOT a list of agents that must exist — the canonical
# directory is the roster. Keys: model (opencode-go full ID), color,
# temperature (optional), permission {edit,websearch,bash}. mode is always
# "subagent". description is pulled from the canonical file so it's never
# duplicated here.
OC_PRESETS: dict[str, dict] = {
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

# Canonical files write a Claude Code tier ("model: sonnet"), not an OpenCode
# model ID, so the tier has to be translated on the way out. Table is
# claude-setup/README.md "Model mapping"; keep the two in step.
TIER_TO_OC_MODEL = {
    "opus": "opencode-go/deepseek-v4-pro",
    "sonnet": "opencode-go/kimi-k2.7-code",
    "haiku": "opencode-go/deepseek-v4-flash",
    "planning": "opencode-go/glm-5.2",
}

# Medium (Sonnet) tier default for a canonical file with no preset and no
# model: field of its own.
DEFAULT_MODEL = TIER_TO_OC_MODEL["sonnet"]


def oc_model(canon_model: str | None) -> str:
    """Translate a canonical model: field to an OpenCode model ID.

    A tier name maps through TIER_TO_OC_MODEL. A value that already looks like
    a provider/model ID passes through, so a canonical file can pin one
    explicitly. Anything else falls back to the default rather than emitting a
    model ID OpenCode cannot resolve.
    """
    if not canon_model:
        return DEFAULT_MODEL
    value = canon_model.strip().strip('"').strip("'")
    if value in TIER_TO_OC_MODEL:
        return TIER_TO_OC_MODEL[value]
    if "/" in value:
        return value
    return DEFAULT_MODEL


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


def render_oc_frontmatter(name: str, description: str, spec: dict) -> str:
    lines = ["---", f'name: "{name}"', f"description: {description}", "mode: subagent", f'model: "{spec["model"]}"']
    if "color" in spec:
        lines.append(f'color: "{spec["color"]}"')
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

    canonical_files = sorted(CANON.glob("*.md"))
    if not canonical_files:
        print("canonical directory is empty — add claude-setup/agents/<name>.md to register an agent")
        return 0

    OC.mkdir(parents=True, exist_ok=True)
    drift: list[str] = []
    emitted: list[tuple[str, str]] = []
    skipped: list[str] = []

    for canon_path in canonical_files:
        name = canon_path.stem
        canon_text = canon_path.read_text(encoding="utf-8")
        canon_fm, canon_body = split_frontmatter(canon_text)
        desc = fm_field(canon_fm, "description")
        if not desc:
            skipped.append(f"{name}: no description in canonical")
            continue

        preset = OC_PRESETS.get(name)
        if preset is not None:
            spec = preset
            source = "preset"
        else:
            spec = {
                "model": oc_model(fm_field(canon_fm, "model")),
                "permission": {"edit": "deny", "websearch": "deny", "bash": "deny"},
            }
            source = "default"

        body = canon_body
        if name == "project-health-monitor":
            body = project_health_monitor_reconcile(canon_body)

        # per-harness body override
        override = OC / f"{name}.md.overrides-body"
        if override.exists():
            body = override.read_text(encoding="utf-8").lstrip("\n")

        out = render_oc_frontmatter(name, desc, spec) + "\n\n" + body.rstrip() + "\n"

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
        emitted.append((name, source))

    for name in sorted(OC_ONLY):
        p = OC / f"{name}.md"
        if p.exists():
            emitted.append((name, "opencode-only, passthrough"))

    print(f"emitted: {len(emitted)}")
    for name, source in emitted:
        print(f"  ✓ {name} ({source})")
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
