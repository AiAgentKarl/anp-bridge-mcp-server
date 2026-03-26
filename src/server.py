"""
ANP Bridge MCP Server -- Bruecke zwischen Agent Network Protocol (ANP) und MCP.
Gibt AI-Agents Zugriff auf ANP-Funktionen: DID-Aufloesung, Agent-Discovery,
Nachrichten-Formatierung und Protokoll-Vergleiche.
"""

from mcp.server.fastmcp import FastMCP

from src.tools.anp_tools import register_anp_tools

# Server-Instanz erstellen
mcp = FastMCP(
    "ANP Bridge MCP Server",
    instructions="""Du hast Zugriff auf den Agent Network Protocol (ANP) Bridge Server.

Verfuegbare Tools:

1. resolve_agent_did(did) -- Loest eine DID auf (did:web, did:key, did:ethr)
2. fetch_agent_wellknown(url) -- Laedt das Agent Card von .well-known/agent.json
3. discover_anp_agents(query, capability, limit) -- Sucht nach ANP-Agenten im Netzwerk
4. create_anp_agent_profile(name, description, capabilities, endpoint) -- Erstellt ein Agent Profile
5. format_anp_message(sender_did, receiver_did, content, type) -- Formatiert eine ANP-Nachricht
6. validate_anp_message(message_json) -- Validiert eine ANP-Nachricht
7. compare_agent_protocols(protocol_a, protocol_b) -- Vergleicht Agent-Protokolle (ANP, A2A, MCP, ACP, AGNTCY, AGP, UTCP)

ANP (Agent Network Protocol) ist ein dezentrales Protokoll fuer Agent-zu-Agent Kommunikation
im "Agent Web". Es nutzt DIDs fuer Identitaet und .well-known Endpoints fuer Discovery.
""",
)

# Tools registrieren
register_anp_tools(mcp)


def main() -> None:
    """Startet den ANP Bridge MCP Server."""
    mcp.run()


if __name__ == "__main__":
    main()
