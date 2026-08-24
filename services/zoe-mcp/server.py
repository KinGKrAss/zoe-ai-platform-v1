"""Zoë MCP bridge for the Z1 platform.

Z1 remains the source of truth for identity, memory, authorization and audit.
This bridge exposes read-only memory access; writes remain disabled.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from auth import verify_z1_token
from memory_gateway import MemoryGateway

app = FastAPI(title="Zoë MCP Bridge", version="0.3.0")

ZOE_ID = os.getenv("ZOE_AGENT_ID", "zoe-core")
Z1_RUNTIME = os.getenv("Z1_RUNTIME_VERSION", "unknown")
MEMORY = MemoryGateway()


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class MemorySearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=50)


def _legacy_memory_auth_disabled() -> None:
    """Prevent the old header-presence mechanism from being used for memory."""
    raise HTTPException(status_code=410, detail="use Z1 Auth service for memory authorization")


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
        "version": "0.3.0",
        "agent_id": ZOE_ID,
        "protocol": "MCP",
        "status": "live-memory-ready",
        "read_only": True,
        "authorization": "z1-auth-service",
    }


@app.post("/mcp/tools/list")
def tools_list() -> dict[str, Any]:
    return {
        "tools": [
            {"name": "zoe.identity", "description": "Return the stable Zoë agent identity.", "inputSchema": {"type": "object", "properties": {}}},
            {"name": "z1.runtime.status", "description": "Return the Z1 runtime connection status.", "inputSchema": {"type": "object", "properties": {}}},
            {
                "name": "z1.memory.search",
                "description": "Search active, accepted Zoë memory using Z1 authorization context.",
                "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 50}}, "required": ["query"]},
            },
            {
                "name": "z1.memory.get",
                "description": "Read one owner-scoped Zoë memory entry by UUID using Z1 authorization context.",
                "inputSchema": {"type": "object", "properties": {"memory_id": {"type": "string"}}, "required": ["memory_id"]},
            },
        ]
    }


@app.post("/mcp/v1/tools/z1.memory.search")
async def mcp_memory_search(
    request: MemorySearchRequest,
    auth_context: dict[str, Any] = Depends(verify_z1_token),
) -> dict[str, Any]:
    """Search memory only after successful Z1 Auth introspection."""
    user_id = str(auth_context["user_id"])
    gateway = MemoryGateway(owner_user_id=user_id)
    try:
        results = gateway.search(request.query, request.limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {
        "status": "success",
        "authenticated_as": auth_context.get("sub", user_id),
        "tenant_id": auth_context.get("tenant_id"),
        "data": results,
    }


@app.post("/mcp/tools/call")
async def tools_call(call: ToolCall, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if call.name == "zoe.identity":
        return {"content": [{"type": "text", "text": ZOE_ID}]}

    if call.name == "z1.runtime.status":
        return {"content": [{"type": "json", "json": {"zoe_agent_id": ZOE_ID, "z1_runtime": Z1_RUNTIME, "memory_configured": MEMORY.configured}}]}

    if call.name in {"z1.memory.search", "z1.memory.get"}:
        _legacy_memory_auth_disabled()

    raise HTTPException(status_code=404, detail="Unknown or disabled tool")
