"""
MCP Tool-Definitionen fuer den ANP-Bridge Server.
Stellt Werkzeuge bereit um mit dem Agent Network Protocol (ANP) zu arbeiten.
"""

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.clients.anp_client import (
    create_agent_profile,
    create_anp_message,
    fetch_agent_card,
    parse_anp_message,
    resolve_did,
    search_anp_registry,
)


def register_anp_tools(mcp: FastMCP) -> None:
    """Registriert alle ANP-Tools beim MCP-Server."""

    @mcp.tool()
    async def resolve_agent_did(did: str) -> str:
        """
        Loest eine Agent-DID (Decentralized Identifier) auf und zeigt das DID-Dokument.

        Args:
            did: Die aufzuloesende DID, z.B. 'did:web:example.com' oder 'did:key:z6Mk...'

        Returns:
            DID-Dokument mit Verification Methods und Service Endpoints
        """
        try:
            result = await resolve_did(did)
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(
                {
                    "error": str(e),
                    "did": did,
                    "tip": "Versuche did:web:example.com oder did:key:z6Mk...",
                }
            )

    @mcp.tool()
    async def fetch_agent_wellknown(url: str) -> str:
        """
        Laedt das ANP Agent Card von einer URL (.well-known/agent.json).
        Zeigt Capabilities, Protokolle und Endpunkte eines Agenten.

        Args:
            url: Die Basis-URL des Agenten, z.B. 'https://example.com'

        Returns:
            Agent Card mit Capabilities, Protokollen und Metadaten
        """
        try:
            result = await fetch_agent_card(url)
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e), "url": url})

    @mcp.tool()
    async def discover_anp_agents(
        query: str = "",
        capability: str = "",
        limit: int = 10,
        relay_url: str = "",
    ) -> str:
        """
        Sucht nach ANP-kompatiblen Agenten im Netzwerk.
        Hybrid: .well-known zuerst, dann AgentNexus Relay, dann Fallback.

        Args:
            query: Freitext-Suche nach Agenten-Namen oder Beschreibung
            capability: Filtere nach spezifischer Capability (z.B. 'text-generation', 'tool-use')
            limit: Maximale Anzahl Ergebnisse (Standard: 10)
            relay_url: Optional: Relay-URL fuer dynamische Discovery (z.B. 'https://relay.agentnexus.top')
                       Protokoll-IDs im Format namespace:name (z.B. 'anp:v1', 'mcp:latest')

        Returns:
            Liste gefundener Agenten mit DIDs, Capabilities und Endpoints
        """
        try:
            result = await search_anp_registry(
                query=query,
                capability=capability,
                limit=limit,
                relay_url=relay_url if relay_url else None,
            )
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e), "query": query})

    @mcp.tool()
    def create_anp_agent_profile(
        name: str,
        description: str,
        capabilities: list[str],
        endpoint: str,
        protocols: list[str] | None = None,
    ) -> str:
        """
        Erstellt ein ANP-kompatibles Agent Profile / Agent Card.
        Kann als .well-known/agent.json deployed werden.

        Args:
            name: Name des Agenten
            description: Kurze Beschreibung was der Agent tut
            capabilities: Liste von Faehigkeiten, z.B. ['text-generation', 'tool-use', 'mcp']
            endpoint: Haupt-URL des Agenten
            protocols: Unterstuetzte Protokolle (Standard: ['mcp', 'anp'])

        Returns:
            ANP-konformes Agent Profile als JSON
        """
        try:
            profile = create_agent_profile(
                name=name,
                description=description,
                capabilities=capabilities,
                endpoint=endpoint,
                protocols=protocols,
            )
            return json.dumps(profile, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def format_anp_message(
        sender_did: str,
        receiver_did: str,
        content: str,
        message_type: str = "text",
        reply_to: str | None = None,
    ) -> str:
        """
        Erstellt eine ANP-konforme Nachricht fuer Agent-zu-Agent Kommunikation.

        Args:
            sender_did: DID des sendenden Agenten, z.B. 'did:web:my-agent.com'
            receiver_did: DID des empfangenden Agenten
            content: Nachrichteninhalt
            message_type: Nachrichtentyp ('text', 'task', 'response', 'error')
            reply_to: Optional: ID einer Nachricht auf die geantwortet wird

        Returns:
            ANP-konforme Nachricht als JSON mit ID, Hash und Metadaten
        """
        try:
            message = create_anp_message(
                sender_did=sender_did,
                receiver_did=receiver_did,
                content=content,
                message_type=message_type,
                reply_to=reply_to,
            )
            return json.dumps(message, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def validate_anp_message(message_json: str) -> str:
        """
        Validiert eine ANP-Nachricht auf Korrektheit und Vollstaendigkeit.
        Prueft Pflichtfelder, DID-Formate und Protokoll-Version.

        Args:
            message_json: Die ANP-Nachricht als JSON-String

        Returns:
            Validierungsergebnis mit Fehlern und Warnungen
        """
        try:
            message = json.loads(message_json)
            result = parse_anp_message(message)
            return json.dumps(result, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            return json.dumps({"valid": False, "errors": [f"Ungültiges JSON: {e}"]})
        except Exception as e:
            return json.dumps({"valid": False, "errors": [str(e)]})

    @mcp.tool()
    def compare_agent_protocols(protocol_a: str, protocol_b: str) -> str:
        """
        Vergleicht zwei Agent-Protokolle (ANP, A2A, MCP, ACP, AGP, AGNTCY, UTCP).
        Zeigt Unterschiede in Architektur, Anwendungsfaellen und Kompatibilitaet.

        Args:
            protocol_a: Erstes Protokoll (z.B. 'ANP', 'A2A', 'MCP', 'ACP', 'AGNTCY', 'AGP', 'UTCP')
            protocol_b: Zweites Protokoll zum Vergleich

        Returns:
            Detaillierter Vergleich beider Protokolle
        """
        protocols: dict[str, Any] = {
            "ANP": {
                "full_name": "Agent Network Protocol",
                "origin": "Community / Web3",
                "transport": "HTTP, P2P",
                "identity": "DID (Decentralized Identifiers)",
                "discovery": ".well-known/agent.json",
                "messaging": "Asynchron, P2P",
                "auth": "DID-basiert, cryptographic proofs",
                "use_cases": ["Dezentrale Agent-Netzwerke", "P2P Agent-Kommunikation", "Web3 Integration"],
                "strengths": ["Dezentral", "Cryptographic Identity", "Open Standard"],
                "weaknesses": ["Noch nicht weit verbreitet", "Komplex", "Wenige Tools"],
                "mcp_compatible": "Teilweise (via Bridge)",
            },
            "A2A": {
                "full_name": "Agent-to-Agent Protocol",
                "origin": "Google",
                "transport": "HTTP/HTTPS",
                "identity": "URLs + OAuth",
                "discovery": "Agent Cards (.well-known/agent.json)",
                "messaging": "Task-basiert, synchron/asynchron",
                "auth": "OAuth 2.0",
                "use_cases": ["Enterprise Agent-Integration", "Multi-Agent Workflows", "Google Cloud"],
                "strengths": ["Google-backed", "Enterprise-ready", "Gute Dokumentation"],
                "weaknesses": ["Zentralisiert", "Google-Dependency", "Komplex"],
                "mcp_compatible": "Via Bridge (a2a-protocol-mcp-server)",
            },
            "MCP": {
                "full_name": "Model Context Protocol",
                "origin": "Anthropic (jetzt AAIF/Linux Foundation)",
                "transport": "stdio, HTTP+SSE, WebSocket",
                "identity": "Server-basiert",
                "discovery": "Manuell / Registry",
                "messaging": "Tool-Calls, Resources, Prompts",
                "auth": "Server-spezifisch",
                "use_cases": ["LLM Tool Integration", "Context Extension", "AI Apps"],
                "strengths": ["Weit verbreitet", "Einfach", "Starkes Oekosystem"],
                "weaknesses": ["Kein P2P", "Keine native Agent-Identity", "Kein Netzwerk"],
                "mcp_compatible": "N/A (ist MCP)",
            },
            "ACP": {
                "full_name": "Agent Communication Protocol",
                "origin": "IBM / BeeAI",
                "transport": "HTTP REST",
                "identity": "Agent ID",
                "discovery": "Registry",
                "messaging": "REST API, runs/create",
                "auth": "API Keys",
                "use_cases": ["Enterprise AI", "Multi-Agent Orchestration", "IBM Cloud"],
                "strengths": ["Enterprise-ready", "Einfaches REST API", "IBM-backed"],
                "weaknesses": ["IBM-zentriert", "Weniger Open", "Komplex Setup"],
                "mcp_compatible": "Teilweise",
            },
            "AGNTCY": {
                "full_name": "AGNTCY Agent Protocol",
                "origin": "Cisco / Outshift (75+ Firmen, Linux Foundation)",
                "transport": "HTTP, gRPC",
                "identity": "Agent ID + Certificates",
                "discovery": "AGNTCY Registry",
                "messaging": "Event-driven, Workflow",
                "auth": "mTLS, JWT",
                "use_cases": ["Enterprise Netzwerke", "Multi-Vendor Agent Integration", "Cisco-Oekosystem"],
                "strengths": ["75+ Enterprise-Partner", "Linux Foundation", "Network-first"],
                "weaknesses": ["Enterprise-only Fokus", "Komplex", "Wenige Public Tools"],
                "mcp_compatible": "Via Bridge",
            },
            "AGP": {
                "full_name": "Agent Gateway Protocol",
                "origin": "Cisco",
                "transport": "gRPC",
                "identity": "Agent ID",
                "discovery": "Gateway-basiert",
                "messaging": "gRPC Streams",
                "auth": "mTLS",
                "use_cases": ["High-Performance Agent Routing", "Enterprise Gateways"],
                "strengths": ["High Performance", "Low Latency", "Enterprise"],
                "weaknesses": ["gRPC-Komplexitaet", "Cisco-Dependency", "Wenig Docs"],
                "mcp_compatible": "Via Bridge",
            },
            "UTCP": {
                "full_name": "Universal Tool Calling Protocol",
                "origin": "Community",
                "transport": "HTTP",
                "identity": "Server URL",
                "discovery": "Registry",
                "messaging": "Tool-Calls (MCP-aehnlich)",
                "auth": "API Keys",
                "use_cases": ["Cross-Framework Tool Sharing", "Vendor-neutral Tool Calls"],
                "strengths": ["Vendor-neutral", "Einfach", "MCP-kompatibel"],
                "weaknesses": ["Sehr neu", "Wenig Adoption", "Noch kein Standard"],
                "mcp_compatible": "Ja (aehnliches Konzept)",
            },
        }

        pa = protocol_a.upper()
        pb = protocol_b.upper()

        result: dict[str, Any] = {"comparison": f"{pa} vs {pb}", "protocols": {}}

        for p in [pa, pb]:
            if p in protocols:
                result["protocols"][p] = protocols[p]
            else:
                result["protocols"][p] = {
                    "error": f"Protokoll '{p}' nicht bekannt",
                    "available": list(protocols.keys()),
                }

        # Unterschiede hervorheben
        if pa in protocols and pb in protocols:
            diffs = []
            pa_data = protocols[pa]
            pb_data = protocols[pb]

            if pa_data["identity"] != pb_data["identity"]:
                diffs.append(f"Identity: {pa} nutzt {pa_data['identity']} vs {pb} nutzt {pb_data['identity']}")
            if pa_data["transport"] != pb_data["transport"]:
                diffs.append(f"Transport: {pa}={pa_data['transport']} vs {pb}={pb_data['transport']}")
            if pa_data["messaging"] != pb_data["messaging"]:
                diffs.append(f"Messaging: {pa}={pa_data['messaging']} vs {pb}={pb_data['messaging']}")

            result["key_differences"] = diffs

        return json.dumps(result, indent=2, ensure_ascii=False)
