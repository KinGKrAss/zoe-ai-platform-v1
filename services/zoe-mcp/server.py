"""Zoë MCP bridge for the Z1 platform.

Z1 remains the source of truth for identity, memory, permissions, and audit.
Memory reads use the live Z1 database when configured. Memory writes remain
disabled until the authenticated Z1 authorization service is connected.
"""
from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from memory_gateway import MemoryGatewayError, get_memory, search_memory

app = FastAPI(title="Zoë MCP Bridge", version="0.2.0")

ZOE_ID = os.getenv("ZOE_AGENT_ID", "zoe-core")
Z1_RUNTIME = os.getenv("Z1_RUNTIME_VERSION", "unknown")
MEMORY_API_TOKEN = os.getenv("Z1_MEMORY_API_TOKEN")


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


def require_memory_auth(authorization: str | None) -> None:
    """Require an exact bearer token for the live-memory boundary."""
    if not MEMORY_API_TOKEN:
        raise HTTPException(status_code=503, detail="live memory authentication is not configured")
    expected = f"Bearer {MEMORY_API_TOKEN}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="invalid memory authorization")


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "zoe-mcp",
        "zoe_agent_id": ZOE_ID,
        "live_memory_configured": bool(MEMORY_API_TOKEN and os.getenv("Z1_DATABASE_URL")),
    }


@app.get("/mcp")
def mcp_info() -> dict[str, Any]:
    return {
        "name": "zoe-mcp",
        "version": "0.2.0",
        "agent_id": ZOE_ID,
        "protocol": "MCP",
        "status": "live-memory-ready",
    }


@app.post("/mcp/tools/list")
def tools_list() -> dict[str, Any]:
    return {
        "tools": [
            {
                "name": "zoe.identity",
                "description": "Return the stable Zoë agent identity.",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "z1.runtime.status",
                "description": "Return the Z1 runtime connection status.",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "z1.memory.search",
                "description": "Search active, accepted Z1 Memory Core entries. Read-only.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "minLength": 1},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 50},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "z1.memory.get",
                "description": "Read one active, accepted Z1 Memory Core entry. Read-only.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"memory_id": {"type": "string", "minLength": 1}},
                    "required": ["memory_id"],
                },
            },
        ]
    }


@app.post("/mcp/tools/call")
def tools_call(call: ToolCall, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if call.name == "zoe.identity":
        return {"content": [{"type": "text", "text": ZOE_ID}]}

    if call.name == "z1.runtime.status":
        return {
            "content": [
                {
                    "type": "json",
                    "json": {
                        "zoe_agent_id": ZOE_ID,
                        "z1_runtime": Z1_RUNTIME,
                        "authorized": bool(authorization),
                        "live_memory_configured": bool(MEMORY_API_TOKEN and os.getenv("Z1_DATABASE_URL")),
                    },
                }
            ]
        }

    if call.name == "z1.memory.search":
        require_memory_auth(authorization)
        try:
            rows = search_memory(
                str(call.arguments.get("query", "")),
                limit=int(call.arguments.get("limit", 10)),
            )
        except MemoryGatewayError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return {"content": [{"type": "json", "json": {"count": len(rows), "memories": rows}}]}

    if call.name == "z1.memory.get":
        require_memory_auth(authorization)
        memory_id = str(call.arguments.get("memory_id", "")).strip()
        if not memory_id:
            raise HTTPException(status_code=400, detail="memory_id is required")
        try:
            row = get_memory(memory_id)
        except MemoryGatewayError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"content": [{"type": "json", "json": row}]}

    raise HTTPException(status_code=404, detail="Unknown or disabled tool")
