import os

os.environ["Z1_JWT_SECRET"] = "test-secret"

from datetime import datetime, timedelta, timezone

import jwt
from fastapi.testclient import TestClient

from apps.api.zoe_core_gateway import app


TOKEN = jwt.encode(
    {
        "sub": "test-user",
        "tenant_id": "tenant-a",
        "scopes": ["memory:read", "memory:write", "mcp:execute", "stream:read"],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    },
    "test-secret",
    algorithm="HS256",
)
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def test_status_requires_auth() -> None:
    with TestClient(app) as client:
        assert client.get("/v1/system/status").status_code == 401
        assert client.get("/v1/system/status", headers=HEADERS).status_code == 200


def test_memory_store_and_query() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/v1/memory/store",
            headers=HEADERS,
            json={"content": "Z1 gateway test memory", "category": "test", "metadata": {"source": "ci"}},
        )
        assert created.status_code == 200
        found = client.post("/v1/memory/query", headers=HEADERS, json={"query": "gateway test"})
        assert found.status_code == 200
        assert any("Z1 gateway test memory" in row["content"] for row in found.json()["results"])


def test_mcp_tools_and_call() -> None:
    with TestClient(app) as client:
        tools = client.get("/v1/mcp/tools", headers=HEADERS)
        assert tools.status_code == 200
        assert {item["name"] for item in tools.json()["tools"]} >= {"z1_system_status", "z1_memory_search", "z1_memory_write"}
        rpc = client.post(
            "/mcp",
            headers=HEADERS,
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        )
        assert rpc.status_code == 200
        assert rpc.json()["result"]["tools"]


def test_websocket_stream() -> None:
    with TestClient(app) as client:
        with client.websocket_connect(f"/v1/ws/stream?token={TOKEN}") as websocket:
            connected = websocket.receive_json()
            assert connected["event"] == "connected"
            websocket.send_json({"event": "ping"})
            response = websocket.receive_json()
            assert response["event"] == "response"
