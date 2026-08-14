# Zoë ↔ Z1 Integration Contract

## Flow

`Identity → Memory → Tools → Z1 API → Android`

### Identity

`ZOE-IDENTITY-V1.0.md` is the authoritative human-readable identity record. The API exposes a read-only representation of the active identity.

### Memory

Memory is server-side and permission-aware. Android never accesses the database directly. Memory records carry ownership and review state; provider data such as live crypto quotes is not automatically durable memory.

### Tools

Tools are explicit, permissioned capabilities. Each tool declares input/output schemas and requires audit logging by default.

### Z1 API

The API is the security boundary between clients and internal services. It owns authentication, authorization, tool dispatch, FORTUNA access, and Memory Core access.

### Android

Android is a client only. It stores session credentials using platform secure storage and calls Z1 over HTTPS. It contains no OpenAI or CoinMarketCap secrets.

## Data boundary

```text
Android → Z1 API → Tool/Service → Provider or Database
                         ↓
                    Audit / Memory
```

## Security rules

1. Never put provider API keys in Android.
2. Never let Android query PostgreSQL directly.
3. Memory writes require an authenticated owner context.
4. Tool calls require explicit permission checks.
5. Tool execution is auditable.
6. Identity changes require a new identity version.
