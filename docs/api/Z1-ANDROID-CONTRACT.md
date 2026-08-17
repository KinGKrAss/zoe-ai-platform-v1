# Z1 Android API Contract

The Android client treats Z1 as the authoritative control/state plane.
Local Android storage is cache only.

## Endpoints

### `GET /health`

Returns any successful 2xx JSON/text response when the Z1 API is reachable.

### `GET /api/v1/z1/continuity/zoe`

Expected JSON:

```json
{
  "data": {
    "identity_id": "zoe",
    "identity_version": "1.0",
    "legacy_hash": "sha256:...",
    "state_version": "...",
    "authorized": true
  }
}
```

`identity_id`, `identity_version`, `legacy_hash`, and `state_version` are continuity metadata. The Android cache must never become authoritative for these values.

### `GET /api/v1/z1/council`

Expected JSON:

```json
{
  "data": [
    {
      "agent_code": "AGENT-01",
      "name": "...",
      "domain": "...",
      "title": "...",
      "version": "1.0",
      "is_active": true
    }
  ]
}
```

The client considers the registry complete only when 33 active agents are returned.

## Security boundary

- Z1 owns identity, legacy, state, authorization and audit.
- Zoë interprets authorized Z1 state.
- MCP mediates tools/resources/tasks/interactions.
- Model runtimes provide inference only.
- `agent_id` and `model_id` are intentionally separate concepts.

For production, the API must use HTTPS and an authenticated bearer token or an equivalent managed identity mechanism. No production secret is committed to the Android repository.
