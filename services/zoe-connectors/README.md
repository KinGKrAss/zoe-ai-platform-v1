# zoe-connectors – Z1 Integration Layer

Permissioned connectors to external systems. Zoë never accesses external systems directly—all access is mediated through these connectors.

## Connectors

| Connector | System | Description |
|---|---|---|
| `postgresql/` | PostgreSQL / Z1 Database | Property, financial, and asset data |
| `github/` | GitHub | Repository analysis, issues, pull requests |
| `terrabox/` | Terra Box | Document management and PDF analysis |
| `openai_responses.py` | OpenAI Responses API | Server-side language-model inference for ZOE BRAIN |

The OpenAI connector is an inference adapter. It does not store identity or memory, and it does not execute tool calls. Z1's permissioned tool router remains responsible for all actions.

Configure it with the server environment variables documented in [OpenAI integration setup](../../integrations/openai/README.md). Never put an API key in a mobile app, browser bundle, or repository.

## Permission model

Every connector call is gated by the permission level of the requesting tool:

```
READ    → view data
ANALYZE → compute and aggregate
WRITE   → create or modify records (with audit log)
ADMIN   → destructive actions (with explicit confirmation + audit log)
```

See: [Architecture Blueprint – Integration Layer](../../docs/architecture/ZOE-BLUEPRINT-V1.0.md#5-z1-integration-layer-zoe-connectors)