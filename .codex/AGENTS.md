# Codex Project Layer

Supplement root `AGENTS.md` with Codex-native assets for this repo.

## Native surfaces

- Subagents live in `.codex/agents/*.toml`
- Skills live in `skills/<name>/SKILL.md`
- Skill UI metadata lives in `skills/<name>/agents/openai.yaml`

## Repo skills

Prefer explicit skill invocation when relevant:

- `$wiki-context` — load llm-wiki context before technical work
- `$council` — run multi-model council with Codex as an explicit voice
- `$agent-orchestration` — choose skill vs subagent vs team shape
- `$security-patterns` — structured OWASP + agent-security review

## Council

Codex must participate as a council voice, not only as local harness.

Preferred invocations:

- Fast pass: `python3 templates/council.py --add openai/gpt-5.3-codex "question"`
- Full pass: `python3 templates/council.py --chairman --add openai/gpt-5.3-codex "question"`

If you want Codex as Chairman too, override `OPENCODE_MODEL_COUNCIL_CODE` in the shell before running council.

## Hooks and plugins

Do not try to import Claude plugin or hook config directly from `claude-setup/`.
Treat `claude-setup/settings.json` as Claude-specific.
For this repo, port behavior through Codex skills and subagents first.
