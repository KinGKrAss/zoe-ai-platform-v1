"""Zoë MCP bridge for the Z1 platform.

Z1 remains the source of truth for identity, memory, authorization and audit.
This bridge exposes read-only memory access; writes remain disabled.
"""

from __future__ import annotations

import hmac
import os
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from memory_gateway import MemoryGateway

app = FastAPI(title="Zoë MCP Bridge", version="0.2.0")

ZOE_ID = os.getenv("ZOE_AGENT_ID", "zoe-core")
Z1_RUNTIME = os.getenv("Z1_RUNTIME_VERSION", "unknown")
MEMORY_TOKEN = os.getenv("Z1_MEMORY_API_TOKEN", "")
MEMORY = MemoryGateway()


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


def _authorized(authorization: str | None) -> bool:
    if not MEMORY_TOKEN or not authorization:
        return False
    scheme, _, token = authorization.partition(" ")
    return scheme.lower() == "bearer" and hmac.compare_digest(token, MEMORY_TOKEN)


def _require_memory_auth(authorization: str | None) -> None:
    if not _authorized(authorization):
        raise HTTPException(status_code=401, detail="valid Z1 memory bearer token required")


@app.get("/health")
def health() -> dict[str, Any]:
    database_ok = False
    if MEMORY.configured:
        try:
            with MEMORY.connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    database_ok = cursor.fetchone() is not None
        except Exception:
            database_ok = False
    return {
        "status": "ok" if database_ok else "degraded",
        "service": "zoe-mcp",
        "zoe_agent_id": ZOE_ID,
        "memory": {"configured": MEMORY.configured, "database_reachable": database_ok},
    }


@app.get("/mcp")
def mcp_info() -> dict[str, Any]:
    return {
        "name": "zoe-mcp",
        "version": "0.2.0",
        "agent_id": ZOE_ID,
        "protocol": "MCP",
        "status": "live-memory-ready",
        "read_only": True,
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
                "description": "Search active, accepted Zoë memory for the configured owner.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 50},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "z1.memory.get",
                "description": "Read one owner-scoped Zoë memory entry by UUID.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"memory_id": {"type": "string"}},
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
                        "memory_configured": MEMORY.configured,
                    },
                }
            ]
        }

    if call.name == "z1.memory.search":
        _require_memory_auth(authorization)
        try:
            rows = MEMORY.search(str(call.arguments.get("query", "")), int(call.arguments.get("limit", 20)))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return {"content": [{"type": "json", "json": {"memories": rows, "count": len(rows)}}]}

    if call.name == "z1.memory.get":
        _require_memory_auth(authorization)
        memory_id = str(call.arguments.get("memory_id", ""))
        if not memory_id:
            raise HTTPException(status_code=400, detail="memory_id is required")
        try:
            row = MEMORY.get(memory_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"content": [{"type": "json", "json": row}]}

    raise HTTPException(status_code=404, detail="Unknown or disabled tool")
