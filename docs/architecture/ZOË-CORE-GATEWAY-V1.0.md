# Zoë Core Gateway V1.0

The gateway is the central control plane between Z1 clients and Zoë services.

## Runtime flow

```text
Clients / Frontend
       |
 REST + WebSocket
       |
 Auth / JWT + RBAC
       |
 +-----+-----------+----------------+
 |                 |                |
Memory Engine   MCP Interface   Streaming Core
 |                 |                |
SQLite dev /    JSON-RPC       WebSocket events
PostgreSQL prod tools
```

## REST

- `GET /v1/system/status` – authenticated system state
- `POST /v1/memory/query` – tenant-scoped temporal/text memory search
- `POST /v1/memory/store` – tenant-scoped memory write
- `GET /v1/mcp/tools` – authenticated tool discovery
- `POST /v1/mcp/execute` – authenticated tool execution

## MCP

`POST /mcp` exposes a minimal JSON-RPC MCP-compatible surface for `initialize`, `tools/list`, and `tools/call`.
The implementation intentionally keeps the tool registry small and explicit; additional tools should be registered through reviewed code rather than arbitrary remote execution.

## WebSocket

`/v1/ws/stream` provides bidirectional JSON events. A JWT with `stream:read` (or `system:admin`) is required. The implementation accepts an Authorization header; the `token` query parameter is retained for development/client compatibility and should not be used in production logs or shared URLs.

## Security

- JWT signature and expiry are validated.
- Missing `Z1_JWT_SECRET` fails closed with HTTP 503.
- Permissions are scope-based and tenant context is taken from the authenticated JWT.
- Memory queries and writes are tenant-scoped.
- CORS defaults to localhost and is configured through `Z1_CORS_ORIGINS`.
- No wildcard CORS with credentials.
- MCP tool names are allowlisted; arbitrary shell or network execution is not exposed.

## Production note

The gateway's SQLite memory store is a development/test adapter. Production should bind the same gateway contracts to the repository's PostgreSQL memory schema and vector/embedding layer. This keeps the API contract stable while replacing the storage adapter.
