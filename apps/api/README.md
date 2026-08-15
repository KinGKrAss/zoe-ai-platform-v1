# Z1 Control Plane API

Runnable development API for the Z1 administration platform.

## Run

```bash
export Z1_API_TOKEN='change-me'
uvicorn apps.api.main:app --host 127.0.0.1 --port 8080
```

Health is public:

```bash
curl http://127.0.0.1:8080/health
```

Authenticated calls use both a bearer token and an explicit Z1 actor:

```bash
curl -H "Authorization: Bearer $Z1_API_TOKEN" \
     -H "X-Z1-Actor: king" \
     http://127.0.0.1:8080/v1/assets
```

The development registry persists to SQLite. Production must replace this repository with the PostgreSQL-backed Z1 Wealth Registry and existing RBAC/migration layer.

## Security boundary

- API access is fail-closed when `Z1_API_TOKEN` is missing.
- Every protected request requires an explicit actor identity.
- Asset writes are classified as `USER_REPORTED` by default and never become `VERIFIED` automatically.
- Audit events contain action/actor/target/result metadata, not sensitive source content.
- Biometric material is not accepted by this API.
