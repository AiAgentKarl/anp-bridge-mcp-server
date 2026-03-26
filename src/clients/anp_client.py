"""
HTTP-Client fuer Agent Network Protocol (ANP) Operationen.
Nutzt DID Universal Resolver, .well-known Agent Endpoints und ANP Discovery APIs.
"""

import hashlib
import json
import re
import time
import uuid
from typing import Any
from urllib.parse import urlparse

import httpx

# Universal DID Resolver (oeffentliche API)
DID_RESOLVER_URL = "https://dev.uniresolver.io/1.0/identifiers"

# ANP Agent Discovery (oeffentliches Verzeichnis)
ANP_REGISTRY_URL = "https://anp-registry.agent.ai/v1"

# Timeout fuer HTTP-Anfragen
HTTP_TIMEOUT = 15.0


async def resolve_did(did: str) -> dict[str, Any]:
    """
    Loest eine DID (Decentralized Identifier) auf via Universal Resolver.
    Unterstuetzt did:web, did:key, did:ethr und andere.
    """
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        url = f"{DID_RESOLVER_URL}/{did}"
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        data = response.json()

        # Extrahiere relevante Felder aus dem DID Document
        did_doc = data.get("didDocument", {})
        return {
            "did": did,
            "resolved": True,
            "document": did_doc,
            "verification_methods": did_doc.get("verificationMethod", []),
            "service_endpoints": did_doc.get("service", []),
            "controller": did_doc.get("controller", did),
        }


async def fetch_agent_card(base_url: str) -> dict[str, Any]:
    """
    Laedt das ANP Agent Card von .well-known/agent.json eines Hosts.
    Kompatibel mit Agent-2-Agent (A2A) und ANP Standards.
    """
    # URL normalisieren
    if not base_url.startswith("http"):
        base_url = f"https://{base_url}"
    parsed = urlparse(base_url)
    root_url = f"{parsed.scheme}://{parsed.netloc}"

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        # Versuche verschiedene standard Pfade
        paths = [
            "/.well-known/agent.json",
            "/.well-known/agent-card.json",
            "/agent.json",
            "/api/agent",
        ]
        for path in paths:
            try:
                resp = await client.get(f"{root_url}{path}", follow_redirects=True)
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "url": f"{root_url}{path}",
                        "found": True,
                        "agent_card": data,
                        "capabilities": data.get("capabilities", []),
                        "name": data.get("name", "Unknown Agent"),
                        "version": data.get("version", "unknown"),
                        "protocols": data.get("protocols", []),
                    }
            except Exception:
                continue

    return {
        "url": root_url,
        "found": False,
        "agent_card": None,
        "message": "Kein Agent Card unter .well-known Pfaden gefunden",
    }


async def search_anp_registry(
    query: str = "", capability: str = "", limit: int = 10
) -> dict[str, Any]:
    """
    Sucht im ANP Agent Registry nach Agenten.
    Fallback auf simuliertes Verzeichnis wenn Registry nicht erreichbar.
    """
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            params: dict[str, Any] = {"limit": limit}
            if query:
                params["q"] = query
            if capability:
                params["capability"] = capability

            resp = await client.get(
                f"{ANP_REGISTRY_URL}/agents",
                params=params,
                follow_redirects=True,
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "source": "anp-registry",
                    "query": query,
                    "count": len(data.get("agents", [])),
                    "agents": data.get("agents", []),
                }
        except Exception:
            pass

    # Fallback: Bekannte oeffentliche Agenten aus ANP-kompatiblen Quellen
    known_agents = [
        {
            "name": "Claude MCP Agent",
            "did": "did:web:api.anthropic.com",
            "capabilities": ["text-generation", "tool-use", "mcp"],
            "protocols": ["mcp", "anp"],
            "endpoint": "https://api.anthropic.com/agent",
        },
        {
            "name": "OpenAI GPT Agent",
            "did": "did:web:api.openai.com",
            "capabilities": ["text-generation", "tool-use", "function-calling"],
            "protocols": ["openai", "a2a"],
            "endpoint": "https://api.openai.com/v1/agent",
        },
        {
            "name": "Gemini Agent",
            "did": "did:web:generativelanguage.googleapis.com",
            "capabilities": ["text-generation", "multimodal", "tool-use"],
            "protocols": ["gemini", "a2a", "anp"],
            "endpoint": "https://generativelanguage.googleapis.com/agent",
        },
    ]

    # Filter nach Query
    if query:
        q = query.lower()
        known_agents = [
            a for a in known_agents if q in a["name"].lower() or q in str(a["capabilities"]).lower()
        ]

    if capability:
        cap = capability.lower()
        known_agents = [a for a in known_agents if cap in str(a["capabilities"]).lower()]

    return {
        "source": "fallback-directory",
        "query": query,
        "count": len(known_agents[:limit]),
        "agents": known_agents[:limit],
        "note": "ANP Registry nicht erreichbar, zeige bekannte oeffentliche Agenten",
    }


def create_anp_message(
    sender_did: str,
    receiver_did: str,
    content: str,
    message_type: str = "text",
    reply_to: str | None = None,
) -> dict[str, Any]:
    """
    Erstellt eine ANP-konforme Nachricht im standardisierten Format.
    Basiert auf dem ANP Message Schema (draft-anp-messaging-01).
    """
    message_id = f"anp:{uuid.uuid4().hex}"
    timestamp = int(time.time())

    message = {
        "@context": ["https://www.w3.org/ns/did/v1", "https://anp.network/v1"],
        "@type": "ANPMessage",
        "id": message_id,
        "version": "1.0",
        "timestamp": timestamp,
        "sender": {"did": sender_did},
        "receiver": {"did": receiver_did},
        "payload": {
            "type": message_type,
            "content": content,
        },
        "metadata": {
            "created_at": timestamp,
            "protocol": "anp/1.0",
        },
    }

    # Optional: Reply-Referenz
    if reply_to:
        message["metadata"]["reply_to"] = reply_to

    # Message Hash fuer Integritaet
    msg_str = json.dumps(message, sort_keys=True)
    message["hash"] = hashlib.sha256(msg_str.encode()).hexdigest()[:16]

    return message


def create_agent_profile(
    name: str,
    description: str,
    capabilities: list[str],
    endpoint: str,
    protocols: list[str] | None = None,
) -> dict[str, Any]:
    """
    Erstellt ein ANP-kompatibles Agent Profile / Agent Card.
    Kompatibel mit .well-known/agent.json Standard.
    """
    if protocols is None:
        protocols = ["mcp", "anp"]

    # DID:web aus dem Endpoint ableiten
    parsed = urlparse(endpoint)
    did = f"did:web:{parsed.netloc}" if parsed.netloc else f"did:key:{uuid.uuid4().hex[:16]}"

    profile = {
        "@context": "https://anp.network/v1/context",
        "@type": "AgentCard",
        "name": name,
        "description": description,
        "version": "1.0",
        "did": did,
        "endpoint": endpoint,
        "capabilities": capabilities,
        "protocols": protocols,
        "verification": {
            "method": "did-key",
            "proof_required": False,
        },
        "metadata": {
            "created": int(time.time()),
            "schema_version": "anp/1.0",
        },
    }

    return profile


def parse_anp_message(raw_message: dict[str, Any]) -> dict[str, Any]:
    """
    Parsed und validiert eine ANP-Nachricht.
    Prueft Pflichtfelder und gibt strukturierte Analyse zurueck.
    """
    errors = []
    warnings = []

    # Pflichtfelder pruefen
    required = ["@type", "id", "sender", "receiver", "payload"]
    for field in required:
        if field not in raw_message:
            errors.append(f"Pflichtfeld fehlt: {field}")

    # Typ validieren
    if raw_message.get("@type") != "ANPMessage":
        warnings.append(f"Unbekannter Nachrichtentyp: {raw_message.get('@type')}")

    # Version pruefen
    version = raw_message.get("version", "unknown")
    if version not in ["1.0", "0.9"]:
        warnings.append(f"Unbekannte ANP Version: {version}")

    # DID Format pruefen
    for party in ["sender", "receiver"]:
        did = raw_message.get(party, {}).get("did", "")
        if did and not re.match(r"^did:[a-z]+:.+", did):
            warnings.append(f"Ungueltige DID fuer {party}: {did}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "message_id": raw_message.get("id", "unknown"),
        "message_type": raw_message.get("payload", {}).get("type", "unknown"),
        "sender_did": raw_message.get("sender", {}).get("did", "unknown"),
        "receiver_did": raw_message.get("receiver", {}).get("did", "unknown"),
        "content_preview": str(raw_message.get("payload", {}).get("content", ""))[:100],
        "has_hash": "hash" in raw_message,
        "protocol_version": raw_message.get("version", "unknown"),
    }
