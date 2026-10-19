---
title: "Anthropic — frontend-design skill"
type: summary
tags: [frontend, design, typography, ux-writing, agent-skills, anthropic]
sources: ["claude-plugins-officialpluginsfrontend-designskillsfrontend-designSKILL.md at main.md"]
created: 2026-10-19
updated: 2026-10-19
---

# Anthropic — frontend-design skill

The `frontend-design` skill in Anthropic's `claude-plugins-official` marketplace is prompt guidance that pushes an agent away from templated, recognisably generated UI. It is all prose: nothing in it is enforced by code. This repo tailors it through the `design-brief` overlay skill (dotfiles, branch `feat/design-brief`), which adds code-level checks.

## Core method

1. **Ground the design in the subject.** If the brief does not name the product, its audience and its primary job, propose them and confirm. Distinctive choices come from the subject's industry, materials and vernacular.
2. **Two passes.** First write a compact token plan: 4–6 named hex colours, typefaces and their roles, a layout concept with ASCII wireframes and alignment guidance, and principles. Then review the plan for genericness: imagine a similar prompt, and revise any part you would have produced anyway. Code comes only after that review.
3. **Restraint.** Put the boldness in one element and keep the rest quiet ("look in the mirror and remove one accessory"). Build to a quality floor without announcing it: responsive, visible keyboard focus, reduced motion respected, accessible contrast.
4. **Self-critique with screenshots** where the environment allows, and keep notes of what was tried, because human designers remember their past attempts. The skill gives no place to store those notes.

## Named tells of generated pages

- A single accented word or phrase in a headline (italic, bold or colour).
- All-caps labels, and needless typographic labels (eyebrows) above content.
- Numbered markers (01 / 02 / 03) on content that is not a sequence.
- The big-number-plus-small-label hero with a gradient accent, used by default.
- Fade-and-slide-up entrances on every section and hover transitions on every card. One orchestrated motion moment beats scattered effects; motion that answers a user action is fine.
- Default font families reused across projects.

## Typography and copy

- One or two families; if two, clearly distinct. Use a type scale following *The Elements of Typographic Style*. Keep lines under about 80 characters, and give serif body text a little more line-height.
- Structural devices (borders, numbering, dividers) encode information, not decoration.
- UX writing: write from the user's side and name things by what users understand ("notifications", not "webhook config"). Use active-voice CTAs that say what happens, and keep one verb through a flow ("Publish" → "Published"). Errors explain the fix and never apologise. Empty states invite action. Sentence case, no filler.
- CSS caution: watch for selector specificity collisions between type-based and element-based classes, especially in section spacing.

## Assessment

- The genericness review is a self-check done inside the same model, so the model judges its own defaults. A second model's baseline plan gives an external reference point; `design-brief` uses `deepseek-v4-pro` for it. (Design rationale, not a measured result.)
- The tells list can be turned into regexes. That makes part of the guidance checkable by a hook, not just by reading.
- No evaluation data is published with the skill; its effect on output quality is (claimed, unverified).

## Wiki connections

- [[patterns/frontend]]: engineering patterns; its Agent Trigger now routes visual-design work here.
- [[concepts/mobile-design-patterns]]: overlapping quality floor (touch targets, responsive behaviour).
- [[concepts/preference-feedback-loop]]: the judge loop that `design-brief` adapts with non-Gemini voices.
