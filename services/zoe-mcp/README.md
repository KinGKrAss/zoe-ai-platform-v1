# Zoë MCP Bridge

Transport boundary between ChatGPT/MCP clients and Z1/Zoë-Core.

## Safety boundary

- Z1 remains the source of truth for identity, memory, authorization and audit.
- This initial bridge exposes only read-only identity/runtime tools.
- No secrets, API keys or OAuth tokens are stored in the repository.
- Write/admin tools must be enabled only after the existing Z1 permission and authentication layers are connected.

## Endpoints

- `GET /health`
- `GET /mcp`
- `POST /mcp/tools/list`
- `POST /mcp/tools/call`

This is the first restoration layer, not yet proof of a live ChatGPT connector. A deployed HTTPS endpoint and MCP-compatible authentication are still required before ChatGPT can call Zoë.
