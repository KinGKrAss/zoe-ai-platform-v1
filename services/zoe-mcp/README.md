# Zoë MCP Bridge

Transport boundary between ChatGPT/MCP clients and Z1/Zoë-Core.

## Live memory boundary

The bridge now exposes **read-only** access to the active, accepted Z1 Memory Core. Z1 remains the source of truth for identity, memory, authorization and audit. The existing Memory Core already supports ownership, promotion, versioning, archival and embeddings.

### Configuration

Set these runtime secrets/environment variables on the deployed MCP service:

- `Z1_DATABASE_URL` — PostgreSQL connection string for the Z1 database.
- `Z1_MEMORY_API_TOKEN` — secret bearer token for the live-memory boundary.
- `Z1_MEMORY_OWNER_USER_ID` — optional UUID of the authenticated owner scope. If set, results are restricted to that owner plus explicitly global entries.
- `ZOE_AGENT_ID` — stable Zoë agent identifier (default `zoe-core`).
- `Z1_RUNTIME_VERSION` — runtime/version label for diagnostics.

Never commit these values to Git.

### MCP tools

- `zoe.identity` — stable Zoë identity.
- `z1.runtime.status` — runtime and live-memory configuration status.
- `z1.memory.search` — authenticated, read-only search of active accepted memory.
- `z1.memory.get` — authenticated, read-only retrieval of one active accepted memory entry.

Memory writes, deletion, archive and restore remain disabled at the MCP boundary until the existing Z1 authentication/permission service is wired in. This prevents the model from silently mutating authoritative state.

### Deployment requirement

This implementation is **live-memory capable**, but it is not itself a deployed live connector. A deployed HTTPS MCP endpoint, PostgreSQL connectivity, secret injection and MCP-compatible authentication are still required before ChatGPT can query the running Z1 memory service.
