"""Zoë MCP bridge for the Z1 platform.

This is the transport boundary only: Z1 remains the source of truth for
identity, memory, permissions, and audit. The bridge intentionally exposes
read-only discovery/status tools until authentication and write-policy are
wired to the existing Z1 permission service.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Zoë MCP Bridge", version="0.1.0")

ZOE_ID = os.getenv("ZOE_AGENT_ID", "zoe-core")
Z1_RUNTIME = os.getenv("Z1_RUNTIME_VERSION", "unknown")


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "zoe-mcp", "zoe_agent_id": ZOE_ID}


@app.get("/mcp")
def mcp_info() -> dict[str, Any]:
    """Minimal discovery metadata for the bridge endpoint."""
    return {
        "name": "zoe-mcp",
        "version": "0.1.0",
        "agent_id": ZOE_ID,
        "protocol": "MCP",
        "status": "scaffold",
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
        ]
    }


@app.post("/mcp/tools/call")
def tools_call(call: ToolCall, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    # Keep execution read-only until the Z1 permission/auth service is wired.
    if call.name == "zoe.identity":
        return {"content": [{"type": "text", "text": ZOE_ID}]}
    if call.name == "z1.runtime.status":
        return {
            "content": [
                {
                    "type": "json",
                    "json": {"zoe_agent_id": ZOE_ID, "z1_runtime": Z1_RUNTIME, "authorized": bool(authorization)},
                }
            ]
        }
    raise HTTPException(status_code=404, detail="Unknown or disabled tool")
