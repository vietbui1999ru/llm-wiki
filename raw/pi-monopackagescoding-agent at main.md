[![pi logo](https://camo.githubusercontent.com/17747c1d541a223db8935e5a9112f17fb7c45b39c84d139e5cea9e133068bb2f/68747470733a2f2f70692e6465762f6c6f676f2e737667)](https://pi.dev/)[pi.dev](https://pi.dev/) domain graciously donated by  
  
[![Exy mascot](https://github.com/badlogic/pi-mono/raw/main/packages/coding-agent/docs/images/exy.png)  
exe.dev](https://exe.dev/)

> New issues and PRs from new contributors are auto-closed by default. Maintainers review auto-closed issues daily. See [CONTRIBUTING.md](https://github.com/badlogic/pi-mono/blob/main/CONTRIBUTING.md).

---

## Pi Monorepo

> **Looking for the pi coding agent?** See **[packages/coding-agent](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent)** for installation and usage.

Tools for building AI agents.

If you use pi or other coding agents for open source work, please share your sessions.

Public OSS session data helps improve coding agents with real-world tasks, tool use, failures, and fixes instead of toy benchmarks.

For the full explanation, see [this post on X](https://x.com/badlogicgames/status/2037811643774652911).

To publish sessions, use [`badlogic/pi-share-hf`](https://github.com/badlogic/pi-share-hf). Read its README.md for setup instructions. All you need is a Hugging Face account, the Hugging Face CLI, and `pi-share-hf`.

You can also watch [this video](https://x.com/badlogicgames/status/2041151967695634619), where I show how I publish my `pi-mono` sessions.

I regularly publish my own `pi-mono` work sessions here:

- [badlogicgames/pi-mono on Hugging Face](https://huggingface.co/datasets/badlogicgames/pi-mono)

## Packages

| Package | Description |
| --- | --- |
| **[@mariozechner/pi-ai](https://github.com/badlogic/pi-mono/blob/main/packages/ai)** | Unified multi-provider LLM API (OpenAI, Anthropic, Google, etc.) |
| **[@mariozechner/pi-agent-core](https://github.com/badlogic/pi-mono/blob/main/packages/agent)** | Agent runtime with tool calling and state management |
| **[@mariozechner/pi-coding-agent](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent)** | Interactive coding agent CLI |
| **[@mariozechner/pi-tui](https://github.com/badlogic/pi-mono/blob/main/packages/tui)** | Terminal UI library with differential rendering |
| **[@mariozechner/pi-web-ui](https://github.com/badlogic/pi-mono/blob/main/packages/web-ui)** | Web components for AI chat interfaces |

## Chat bot workflows

For Slack/chat automation, see [earendil-works/pi-chat](https://github.com/earendil-works/pi-chat).

## Contributing

See [CONTRIBUTING.md](https://github.com/badlogic/pi-mono/blob/main/CONTRIBUTING.md) for contribution guidelines and [AGENTS.md](https://github.com/badlogic/pi-mono/blob/main/AGENTS.md) for project-specific rules (for both humans and agents).

## Development

```
npm install          # Install all dependencies
npm run build        # Build all packages
npm run check        # Lint, format, and type check
./test.sh            # Run tests (skips LLM-dependent tests without API keys)
./pi-test.sh         # Run pi from sources (can be run from any directory)
```

> **Note:** `npm run check` requires `npm run build` to be run first. The web-ui package uses `tsc` which needs compiled `.d.ts` files from dependencies.

## License

MIT