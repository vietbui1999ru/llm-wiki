## Cloud Agents

Cloud agents leverage the same [agent fundamentals](https://cursor.com/learn/agents) but run in isolated environments in the cloud instead of on your local machine.

## Why use Cloud Agents?

You can run as many agents as you want in parallel, and they do not require your local machine to be connected to the internet.

Because they have access to their own virtual machine, cloud agents can build, test, and interact with the changed software. They can also use computers to control the desktop and browser. Cloud agents support [MCP servers](https://cursor.com/docs/mcp), giving them access to external tools and data sources like databases, APIs, and third-party services.

## How to access

You can kick off cloud agents from wherever you work:

1. **Cursor Web**: Start and manage agents from [cursor.com/agents](https://cursor.com/agents) on any device
2. **Cursor Desktop**: Select **Cloud** in the dropdown under the agent input
3. **Slack**: Use the @cursor command to kick off an agent
4. **GitHub**: Comment `@cursor` on a PR or issue to kick off an agent
5. **Linear**: Use the @cursor command to kick off an agent
6. **API**: Use the API to kick off an agent

For a native-feeling mobile experience, install Cursor as a Progressive Web App (PWA). On **iOS**, open [cursor.com/agents](https://cursor.com/agents) in Safari, tap the share button, then "Add to Home Screen". On **Android**, open the URL in Chrome, tap the menu, then "Install App".

[

Use Cursor in Slack

Learn more about setting up and using the Slack integration, including triggering agents and receiving notifications.

](https://cursor.com/docs/integrations/slack)

## How it works

### GitHub or GitLab connection

Cloud agents clone your repo from GitHub or GitLab and work on a separate branch, then push changes to your repo for handoff.

You need read-write privileges to your repo and any dependent repos or submodules. Support for other providers like Bitbucket is coming later.

## Models

Cloud Agents use a curated selection of models that always run in [Max Mode](https://cursor.com/docs/models-and-pricing#max-mode).

There is no toggle to turn Max Mode off for Cloud Agents.

## MCP support

Cloud agents can use [MCP (Model Context Protocol)](https://cursor.com/docs/mcp) servers configured for your team. Add and manage MCP servers through the MCP dropdown in [cursor.com/agents](https://cursor.com/agents).

Both HTTP and stdio transports are supported. OAuth is supported for MCP servers that need it. See [Cloud Agent capabilities](https://cursor.com/docs/cloud-agent/capabilities) for setup details.

## Hooks support

Cloud agents run project hooks from `.cursor/hooks.json`. On Enterprise plans, they also run team hooks and enterprise-managed hooks.

This lets you keep formatters, audit scripts, and policy checks active when work runs in the cloud whether you manage them in the repo or from the dashboard.

See [Hooks](https://cursor.com/docs/hooks) for the hook model and configuration format.

## Artifacts and remote desktop control

Cloud agents produce merge-ready PRs with artifacts to demo their changes. You can also control the agent's remote desktop to use the modified software.

- **Artifacts**: Agents produce screenshots, videos, and logs so you can see exactly what changed and how the agent verified its work.
- **Remote desktop control**: Take control of the agent's desktop to test the software yourself in a full development environment without checking out the branch locally. Release control back to the agent for it to keep working.

See [Cloud agent capabilities](https://cursor.com/docs/cloud-agent/capabilities) for details on artifacts, computer use, and remote desktop control.

## Related pages

- Learn more about [Cloud agent capabilities](https://cursor.com/docs/cloud-agent/capabilities).
- Learn more about [Cloud agent security](https://cursor.com/docs/cloud-agent/security-network).
- Learn more about [Cloud agent settings](https://cursor.com/docs/cloud-agent/settings).

## Billing

Cloud Agents are charged at API pricing for the selected [model](https://cursor.com/docs/models-and-pricing#model-pricing). You'll be asked to set a spend limit when you first start using them.

## Troubleshooting

## Naming History

Cloud Agents were formerly called Background Agents.