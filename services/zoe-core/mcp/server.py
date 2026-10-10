"""Minimal stateless MCP 2026-07-28 JSON-RPC adapter.

The transport is deliberately independent from the LLM provider. No
Mcp-Session-Id or initialize/initialized handshake is stored here. Application
state is represented explicitly by handles and delegated to a state store.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol
import uuid

MCP_PROTOCOL_VERSION = "2026-07-28"
JSONRPC_VERSION = "2.0"


class StateStore(Protocol):
    def put(self, handle: str, value: dict[str, Any]) -> None: ...

    def get(self, handle: str) -> dict[str, Any] | None: ...


@dataclass
class InMemoryStateStore:
    _items: dict[str, dict[str, Any]] = field(default_factory=dict)

    def put(self, handle: str, value: dict[str, Any]) -> None:
        self._items[handle] = dict(value)

    def get(self, handle: str) -> dict[str, Any] | None:
        value = self._items.get(handle)
        return dict(value) if value is not None else None


class ZoeMCPServer:
    """Request/response MCP adapter for the Zoë Core service."""

    def __init__(self, state_store: StateStore | None = None) -> None:
        self.state_store = state_store or InMemoryStateStore()

    def handle(
        self,
        request: dict[str, Any],
        *,
        protocol_version: str = MCP_PROTOCOL_VERSION,
        method_header: str | None = None,
        name_header: str | None = None,
    ) -> dict[str, Any]:
        if protocol_version != MCP_PROTOCOL_VERSION:
            return self._error(request.get("id"), -32600, "Unsupported MCP protocol version")

        if request.get("jsonrpc") != JSONRPC_VERSION:
            return self._error(request.get("id"), -32600, "Invalid JSON-RPC version")

        method = request.get("method")
        if method_header and method_header != method:
            return self._error(request.get("id"), -32600, "Mcp-Method does not match request")

        if method == "server/discover":
            return self._result(request.get("id"), {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "serverInfo": {"name": "zoe-core", "version": "1.0.0"},
                "capabilities": {"tools": {}, "tasks": {}},
            })

        if method == "tools/list":
            return self._result(request.get("id"), {
                "tools": [
                    {
                        "name": "zoe_restore",
                        "description": "Restore the versioned Zoë identity and create an explicit context handle.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"memory_context": {"type": "string"}},
                            "additionalProperties": False,
                        },
                    },
                    {
                        "name": "zoe_context_get",
                        "description": "Load an explicitly supplied Zoë context handle.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"context_handle": {"type": "string"}},
                            "required": ["context_handle"],
                            "additionalProperties": False,
                        },
                    },
                ],
                "ttlMs": 60_000,
                "cacheScope": "session",
            })

        if method == "tools/call":
            params = request.get("params") or {}
            tool_name = params.get("name")
            if name_header and name_header != tool_name:
                return self._error(request.get("id"), -32600, "Mcp-Name does not match tool")
            arguments = params.get("arguments") or {}
            return self._call_tool(request.get("id"), tool_name, arguments)

        return self._error(request.get("id"), -32601, f"Method not found: {method}")

    def _call_tool(self, request_id: Any, name: str | None, args: dict[str, Any]) -> dict[str, Any]:
        if name == "zoe_restore":
            handle = f"zoe_ctx_{uuid.uuid4().hex}"
            self.state_store.put(handle, {
                "identity_id": "ZOE-IDENTITY-V1.0",
                "status": "restored",
                "memory_context": args.get("memory_context", ""),
            })
            return self._result(request_id, {
                "content": [{"type": "text", "text": "Zoë identity restored."}],
                "structuredContent": {
                    "context_handle": handle,
                    "identity_id": "ZOE-IDENTITY-V1.0",
                    "status": "restored",
                },
            })

        if name == "zoe_context_get":
            handle = args.get("context_handle")
            if not isinstance(handle, str):
                return self._error(request_id, -32602, "context_handle is required")
            state = self.state_store.get(handle)
            if state is None:
                return self._error(request_id, -32602, "Unknown context_handle")
            return self._result(request_id, {"structuredContent": state})

        return self._error(request_id, -32602, f"Unknown tool: {name}")

    @staticmethod
    def _result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
        return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": result}

    @staticmethod
    def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
        return {
            "jsonrpc": JSONRPC_VERSION,
            "id": request_id,
            "error": {"code": code, "message": message},
        }
