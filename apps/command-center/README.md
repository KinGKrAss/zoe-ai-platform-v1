# Z1 Command Center Runtime

This is the executable web/control surface for Z1. It provides:

- Zoë Core orchestration API: `POST /api/zoe/run`
- PostgreSQL-backed Zoë Memory API
- registration/login with scrypt password hashes and signed JWT sessions
- permission checks from the Z1 RBAC tables
- MCP JSON-RPC endpoint at `POST /mcp`
- system and identity endpoints

## Required runtime configuration

```text
DATABASE_URL=postgresql://zoe:zoe_dev_password@localhost:5432/zoe
Z1_JWT_SECRET=<long-random-secret>
```

`Z1_JWT_SECRET` is mandatory in production. Never commit it.

## Start

```bash
npm install
Z1_JWT_SECRET='local-development-secret-change-me' npm start
```

The runtime expects the PostgreSQL migrations from `database/migrations` to have been initialized.

## MCP

The MCP endpoint is authenticated with the same bearer JWT used by the Command Center. Available tools:

- `z1_system_status`
- `z1_memory_search`
- `z1_memory_write`

Memory writes require `memory.write`; reads require `memory.read`.
