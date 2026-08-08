# ZOE SECURITY – Model V1.0

## Permission Levels

| Level | Code | Scope |
|---|---|---|
| Read | `READ` | View and retrieve data |
| Analyze | `ANALYZE` | Compute, aggregate, summarise |
| Write | `WRITE` | Create or modify records |
| Admin | `ADMIN` | Destructive or deployment actions |

## Permission matrix

| Action | Level | Confirmation |
|---|---|---|
| View property | READ | No |
| Search documents | READ | No |
| Analyse portfolio | ANALYZE | No |
| Calculate cashflow | ANALYZE | No |
| Generate report | ANALYZE | No |
| Create task | WRITE | No |
| Update asset | WRITE | No |
| Archive document | WRITE | Yes |
| Delete record | ADMIN | Yes + reason |
| Modify GitHub code | ADMIN | Yes |
| Deploy service | ADMIN | Yes + explicit approval |
| Transfer ownership | ADMIN | Yes + reason |

## Enforcement

- Permission level is resolved from: user role + session context + tool definition
- Denied actions are logged to `audit_log` with result `'DENIED'`
- Confirmation flow is triggered by the orchestration layer before executing dangerous tools

See: [Architecture Blueprint – Security](../../docs/architecture/ZOE-BLUEPRINT-V1.0.md#7-zoe-security)
