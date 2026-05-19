# earn-it

Gym mode for Claude Code. Instead of writing code for you, Claude scaffolds exercises, watches you implement, and reviews your work.

> "AI amplifies existing ability. If you can't evaluate the output, you can't use it safely. Earn the shortcut first."

Inspired by [SpotMe](https://github.com/wtfzambo/spotme).

---

## Activation

```
/earn-it [hard|medium|lite]
/earn-it [1|2|3]
```

Default level: **medium** if not specified.

---

## Levels

| Level | Alias | Claude provides | You write |
|---|---|---|---|
| L1 | `hard` | Nothing — questions only | Everything, from a verbal spec |
| L2 | `medium` | Signature + `# EARN-IT:` spec comment | All logic |
| L3 | `lite` | Nothing — you write first, Claude reviews | Everything |

---

## Commands

| Command | Description |
|---|---|
| `/earn-it:rep` | Request an on-demand drill exercise |
| `/earn-it:done` | Signal you're done — trigger review |
| `/earn-it:hint` | Get one targeted hint (Socratic question at hard) |
| `/earn-it:solve` | Concede — Claude completes the exercise and closes the loop |
| `/earn-it:skip` | Skip current exercise, no note |
| `/earn-it:status` | Show current level and exercise state |
| `exit earn-it` | Deactivate, resume normal behavior |

---

## How it works

1. Invoke `/earn-it [level]` at the start of a task or drill session
2. Claude scaffolds the next unit (at L2) or waits for your code (at L1/L3)
3. You implement in your editor
4. `/earn-it:done` → Claude reviews with inline comments, not rewrites
5. Claude closes the loop and moves on

Use `/earn-it:rep` anytime to request a drill on a specific topic.

---

## Install

Skill is already installed if this file is here. No additional setup needed for Claude Code.

The `SKILL.md` is also portable — copy it to any harness that supports AgentSkills (OpenCode, etc.).
