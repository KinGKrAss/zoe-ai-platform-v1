"""Zoë Core Gateway: authenticated REST, WebSocket streaming and MCP-compatible tools."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

DB_PATH = Path(os.getenv("Z1_DEV_DB", ".z1/z1-dev.sqlite3"))
JWT_SECRET = os.getenv("Z1_JWT_SECRET")
JWT_ALGORITHM = os.getenv("Z1_JWT_ALGORITHM", "HS256")
CORS_ORIGINS = [item.strip() for item in os.getenv("Z1_CORS_ORIGINS", "http://localhost:3000").split(",") if item.strip()]

app = FastAPI(
    title="Zoë Core API Gateway",
    version="1.0.0",
    description="Z1 REST, WebSocket streaming and MCP-compatible gateway.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Z1-Actor"],
)

bearer = HTTPBearer(auto_error=False)


class MemoryQueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=5000)
    start_date: datetime | None = None
    end_date: datetime | None = None
    limit: int = Field(default=50, ge=1, le=200)


class MemoryStoreRequest(BaseModel):
    content: str = Field(min_length=1, max_length=20000)
    category: str = Field(default="general", min_length=1, max_length=100)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MCPToolExecutionRequest(BaseModel):
    tool_name: str = Field(min_length=1, max_length=200)
    parameters: dict[str, Any] = Field(default_factory=dict)


def _db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def _init_memory() -> None:
    with closing(_db()) as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS zoe_memory_gateway (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                actor TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                content_sha256 TEXT NOT NULL,
                created_at TEXT NOT NULL
            )"""
        )
        db.execute("CREATE INDEX IF NOT EXISTS idx_memory_gateway_tenant_time ON zoe_memory_gateway(tenant_id, created_at DESC)")
        db.commit()


@app.on_event("startup")
def startup() -> None:
    _init_memory()


def decode_token(token: str) -> dict[str, Any]:
    if not JWT_SECRET:
        raise HTTPException(status_code=503, detail="Z1_JWT_SECRET is not configured")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired JWT") from exc
    if not payload.get("sub"):
        raise HTTPException(status_code=401, detail="JWT subject is required")
    return payload


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Bearer token required", headers={"WWW-Authenticate": "Bearer"})
    return decode_token(credentials.credentials)


def require_scope(scope: str):
    def checker(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
        scopes = user.get("scopes", [])
        if isinstance(scopes, str):
            scopes = scopes.split()
        if scope not in scopes and "system:admin" not in scopes:
            raise HTTPException(status_code=403, detail=f"Missing permission: {scope}")
        return user

    return checker


def _tenant(user: dict[str, Any]) -> str:
    return str(user.get("tenant_id") or "default")


@app.get("/v1/system/status")
def system_status(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    return {
        "status": "online",
        "system": "Zoë Core Gateway",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "authenticated_as": user["sub"],
        "tenant_id": _tenant(user),
        "features": ["memory", "mcp", "websocket"],
    }


@app.post("/v1/memory/query")
def query_memory(req: MemoryQueryRequest, user: dict[str, Any] = Depends(require_scope("memory:read"))) -> dict[str, Any]:
    clauses = ["tenant_id = ?", "content LIKE ?"]
    params: list[Any] = [_tenant(user), f"%{req.query}%"]
    if req.start_date:
        clauses.append("created_at >= ?")
        params.append(req.start_date.astimezone(timezone.utc).isoformat())
    if req.end_date:
        clauses.append("created_at <= ?")
        params.append(req.end_date.astimezone(timezone.utc).isoformat())
    params.append(req.limit)
    sql = f"SELECT * FROM zoe_memory_gateway WHERE {' AND '.join(clauses)} ORDER BY created_at DESC LIMIT ?"
    with closing(_db()) as db:
        rows = db.execute(sql, params).fetchall()
    return {"status": "success", "tenant_id": _tenant(user), "results": [dict(row) for row in rows]}


@app.post("/v1/memory/store")
def store_memory(req: MemoryStoreRequest, user: dict[str, Any] = Depends(require_scope("memory:write"))) -> dict[str, Any]:
    memory_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    fingerprint = hashlib.sha256(req.content.encode("utf-8")).hexdigest()
    with closing(_db()) as db:
        db.execute(
            "INSERT INTO zoe_memory_gateway VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (memory_id, _tenant(user), str(user["sub"]), req.category, req.content, json.dumps(req.metadata), fingerprint, timestamp),
        )
        db.commit()
    return {"status": "created", "entry_id": memory_id, "tenant_id": _tenant(user), "timestamp": timestamp}


TOOLS = {
    "z1_system_status": {"description": "Return authenticated Z1 system status."},
    "z1_memory_search": {"description": "Search tenant-scoped Zoë memory."},
    "z1_memory_write": {"description": "Write tenant-scoped Zoë memory."},
}


@app.get("/v1/mcp/tools")
def mcp_tools(user: dict[str, Any] = Depends(require_scope("mcp:execute"))) -> dict[str, Any]:
    return {"tools": [{"name": name, **meta} for name, meta in TOOLS.items()]}


@app.post("/v1/mcp/execute")
def execute_mcp_tool(req: MCPToolExecutionRequest, user: dict[str, Any] = Depends(require_scope("mcp:execute"))) -> dict[str, Any]:
    if req.tool_name not in TOOLS:
        raise HTTPException(status_code=404, detail="Unknown MCP tool")
    if req.tool_name == "z1_system_status":
        return system_status(user)
    if req.tool_name == "z1_memory_search":
        query = MemoryQueryRequest(**req.parameters)
        return query_memory(query, user)
    if req.tool_name == "z1_memory_write":
        request = MemoryStoreRequest(**req.parameters)
        return store_memory(request, user)
    raise HTTPException(status_code=500, detail="MCP dispatch failure")


@app.post("/mcp")
def mcp_jsonrpc(request: dict[str, Any], user: dict[str, Any] = Depends(require_scope("mcp:execute"))) -> dict[str, Any]:
    """Minimal MCP-compatible JSON-RPC surface for tool discovery/execution."""
    method = request.get("method")
    request_id = request.get("id")
    if method in {"initialize", "notifications/initialized"}:
        return {"jsonrpc": "2.0", "id": request_id, "result": {"protocolVersion": "2025-06-18", "serverInfo": {"name": "zoe-core", "version": "1.0.0"}}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": [{"name": n, **m} for n, m in TOOLS.items()]}}
    if method == "tools/call":
        params = request.get("params", {})
        result = execute_mcp_tool(MCPToolExecutionRequest(tool_name=params.get("name", ""), parameters=params.get("arguments", {})), user)
        return {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": json.dumps(result)}]}}
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.connections.discard(websocket)

    async def send(self, websocket: WebSocket, payload: dict[str, Any]) -> None:
        await websocket.send_json(payload)


manager = ConnectionManager()


@app.websocket("/v1/ws/stream")
async def websocket_stream(websocket: WebSocket, token: str | None = Query(default=None)) -> None:
    auth = websocket.headers.get("authorization", "")
    bearer_token = auth.removeprefix("Bearer ").strip() if auth.startswith("Bearer ") else token
    if not bearer_token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        user = decode_token(bearer_token)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    scopes = user.get("scopes", [])
    if isinstance(scopes, str):
        scopes = scopes.split()
    if "stream:read" not in scopes and "system:admin" not in scopes:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket)
    try:
        await manager.send(websocket, {"event": "connected", "user": user["sub"], "timestamp": datetime.now(timezone.utc).isoformat()})
        while True:
            payload = await websocket.receive_json()
            await manager.send(websocket, {"event": "response", "received": payload, "timestamp": datetime.now(timezone.utc).isoformat()})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
