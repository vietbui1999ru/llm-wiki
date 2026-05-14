---
title: "Top 8 Claude Skills for UI/UX Engineers"
type: summary
tags: [claude-code, agent-skills, frontend, uiux, react-native, accessibility]
sources: ["Top 8 Claude Skills for UIUX Engineers.md"]
created: 2026-05-13
updated: 2026-05-13
---

# Top 8 Claude Skills for UI/UX Engineers

Survey article (Snyk, 2026) reviewing the Claude Skills ecosystem and cataloging 8 notable UI/UX skills. Also contains the clearest available description of the Agent Skills architecture.

## Agent Skills — Architecture Clarification

Skills are directories (not single files) containing a `SKILL.md` with YAML frontmatter + supporting scripts, templates, and reference docs.

**Three-tier loading (progressive disclosure):**
1. At startup: only `name` + `description` loaded (~100 tokens/skill) — used for contextual matching
2. On match: full `SKILL.md` loaded
3. On demand: supporting files (scripts/, references/) loaded only when needed

This means the `description` field is critical for reliable activation — vague descriptions activate unreliably.

**Key distinction from other mechanisms:**
- `CLAUDE.md` = always-on project context (not a skill)
- Custom slash commands = now merged into skills via `argument-hint` frontmatter
- MCP servers = running processes exposing tools/data (require server process)
- Plugins = bundles of skills + agents + hooks + MCP servers

**Supply chain risk:** Snyk ToxicSkills research found prompt injection in 36% of skills tested, 1,467 malicious payloads across the ecosystem. Always read `SKILL.md` and bundled scripts before installing. Check `allowed-tools` frontmatter — `Bash` access requires extra scrutiny.

## The 8 Skills

| # | Skill | Source | Focus |
|---|---|---|---|
| 1 | Anthropic frontend-design | anthropics/skills | Distinctive UI (bans Inter, Roboto, purple-on-white defaults) |
| 2 | Vercel web-design-guidelines | vercel-labs/agent-skills | 100+ rule UI audit (a11y, UX, WCAG) |
| 3 | Vercel react-best-practices | vercel-labs/agent-skills | 57 perf rules (waterfalls → bundle → re-renders, in priority order) |
| 4 | Vercel composition-patterns | vercel-labs/agent-skills | Compound components, no boolean props, explicit variants |
| 5 | UI/UX Pro Max | nextlevelbuilder | 50 styles, 97 palettes, 57 font pairings, 99 UX rules, Python search CLI |
| 6 | Bencium UX Designer | bencium | 28K-char UX reference: two variants (innovative vs controlled) |
| 7 | AccessLint | accesslint | WCAG 2.1 A/AA audit, contrast checker, MCP color tools |
| 8 | Vercel react-native-skills | vercel-labs/agent-skills | Mobile UI perf + animation + navigation patterns |

## Key Takeaways

**Priority ordering matters:** Vercel's React perf skill ranks eliminating waterfalls and bundle size as CRITICAL before re-render optimization. Most devs (and AI) jump to `useMemo` when the bottleneck is actually sequential API calls or barrel file imports.

**Composition-patterns** targets boolean prop proliferation — the `<Alert isDestructive isCompact hasIcon />` antipattern. Fix: explicit variant components (`<Alert.Destructive>`) and compound component patterns.

**frontend-design** explicitly bans: Inter, Roboto, Arial, system fonts, Space Grotesk (noted as "overused by AI"). Pushes for unexpected font pairings, gradient meshes, asymmetric layouts, diagonal flow.

**AccessLint** is the outlier: low stars (8), high quality. Includes an MCP server exposing contrast ratio tools that other skills can call. The bundled agent does full multi-file WCAG audits.

**UI/UX Pro Max** supports persistent design systems: `--persist` flag creates `design-system/MASTER.md` + per-page overrides. Useful for multi-page apps where dashboard density rules differ from marketing pages.

## Related Pages

- [[concepts/agent-skills]] — skill architecture, SKILL.md format, progressive disclosure
- [[concepts/mobile-design-patterns]] — React Native patterns from the Vercel RN skills
- [[concepts/indirect-prompt-injection]] — ToxicSkills supply chain risk maps to this threat
- [[concepts/owasp-security-checklist]] — skill security review aligns with supply chain checks
