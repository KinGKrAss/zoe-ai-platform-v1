# ZOE TOOL SYSTEM – Design V1.0

## Architecture

```
Zoë (reasoning/orchestration)
        │
        ▼
   Tool Router
        │
        ▼
  Permission Check
        │        ╲
        ▼          ▼
  [allowed]    [denied → audit_log DENIED]
        │
        ▼
      Tool
        │
        ▼
  External System (via zoe-connectors)
        │
        ▼
  audit_log (SUCCESS / FAILURE)
```

## Dangerous action confirmation flow

```
Zoë requests dangerous tool (DELETE / TRANSFER / PUBLISH / DEPLOY)
        │
        ▼
Permission Check (ADMIN level required)
        │
        ▼
Confirmation Request → User
        │
        ▼
User confirms (explicit approval + optional reason)
        │
        ▼
Tool executes
        │
        ▼
audit_log (actor, action, target, changes, result)
```

## Tool registry

See [Architecture Blueprint – Tool System](../../docs/architecture/ZOE-BLUEPRINT-V1.0.md#6-zoe-tool-system)

Implementation will live in `services/zoe-core/orchestration/` with tool definitions referenced here.
