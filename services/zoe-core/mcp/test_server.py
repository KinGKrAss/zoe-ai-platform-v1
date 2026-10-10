from services.zoe_core.mcp.server import MCP_PROTOCOL_VERSION, ZoeMCPServer


def test_discover_uses_2026_protocol_without_session():
    server = ZoeMCPServer()
    response = server.handle({"jsonrpc": "2.0", "id": 1, "method": "server/discover"})
    assert response["result"]["protocolVersion"] == MCP_PROTOCOL_VERSION
    assert "Mcp-Session-Id" not in response


def test_restore_returns_explicit_handle_and_context_can_be_retrieved():
    server = ZoeMCPServer()
    response = server.handle({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": "zoe_restore", "arguments": {"memory_context": "Z1"}},
    })
    handle = response["result"]["structuredContent"]["context_handle"]
    follow_up = server.handle({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "zoe_context_get", "arguments": {"context_handle": handle}},
    })
    assert follow_up["result"]["structuredContent"]["memory_context"] == "Z1"


def test_header_routing_must_match_request():
    server = ZoeMCPServer()
    response = server.handle(
        {"jsonrpc": "2.0", "id": 4, "method": "server/discover"},
        method_header="tools/call",
    )
    assert response["error"]["code"] == -32600
