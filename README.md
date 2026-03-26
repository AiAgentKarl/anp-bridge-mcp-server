# ANP Bridge MCP Server

[![PyPI version](https://badge.fury.io/py/anp-bridge-mcp-server.svg)](https://badge.fury.io/py/anp-bridge-mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**The first MCP bridge for the Agent Network Protocol (ANP)** — connect MCP-powered AI agents to the decentralized "Agent Web".

## What is ANP?

[Agent Network Protocol (ANP)](https://anp.network) is an emerging open standard for decentralized agent-to-agent communication. It uses DIDs (Decentralized Identifiers) for identity and `.well-known/agent.json` for discovery — enabling a permissionless, cryptographically secure web of AI agents.

## Features

| Tool | Description |
|------|-------------|
| `resolve_agent_did` | Resolve any DID (did:web, did:key, did:ethr) via Universal Resolver |
| `fetch_agent_wellknown` | Fetch an agent's capabilities from `.well-known/agent.json` |
| `discover_anp_agents` | Search for ANP-compatible agents in the network |
| `create_anp_agent_profile` | Generate a compliant ANP Agent Card / Profile |
| `format_anp_message` | Create ANP-formatted messages for agent-to-agent communication |
| `validate_anp_message` | Validate ANP messages for spec compliance |
| `compare_agent_protocols` | Compare agent protocols: ANP, A2A, MCP, ACP, AGNTCY, AGP, UTCP |

## Installation

```bash
pip install anp-bridge-mcp-server
```

## Usage with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "anp-bridge": {
      "command": "anp-bridge-mcp-server"
    }
  }
}
```

## Example Usage

```
# Discover ANP-compatible agents
discover_anp_agents(capability="text-generation")

# Resolve a DID
resolve_agent_did("did:web:example.com")

# Create an agent profile
create_anp_agent_profile(
    name="My AI Agent",
    description="A helpful AI assistant",
    capabilities=["text-generation", "tool-use"],
    endpoint="https://my-agent.example.com"
)

# Format a message
format_anp_message(
    sender_did="did:web:my-agent.com",
    receiver_did="did:web:other-agent.com",
    content="Hello, I need help with a task",
    message_type="task"
)

# Compare protocols
compare_agent_protocols("ANP", "A2A")
```

## Agent Protocol Landscape (2026)

This server covers 7 competing agent protocols:
- **ANP** — Decentralized, DID-based (Agent Network Protocol)
- **A2A** — Google's Agent-to-Agent Protocol
- **MCP** — Anthropic's Model Context Protocol (now AAIF/Linux Foundation)
- **ACP** — IBM's Agent Communication Protocol
- **AGNTCY** — Cisco's enterprise protocol (75+ companies)
- **AGP** — Cisco's Agent Gateway Protocol (gRPC)
- **UTCP** — Universal Tool Calling Protocol

## Related Servers

- [a2a-protocol-mcp-server](https://pypi.org/project/a2a-protocol-mcp-server/) — Google A2A Protocol Bridge
- [agent-server-card-mcp](https://pypi.org/project/agent-server-card-mcp/) — .well-known Discovery & Server Cards
- [agent-identity-mcp-server](https://pypi.org/project/agent-identity-mcp-server/) — OAuth for Agents

## License

MIT
