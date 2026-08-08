# ZOE GODDESS INTERFACE – Technical Contract V1.0

**Version:** V1.0  
**System:** Z1 Real Estate Command Center  
**Date:** 2026-08-08  
**Status:** Approved Blueprint

---

## Overview

Every Goddess in the Council of 33 implements the same standard interface. This document defines the complete technical contract: input schema, output schema, permission enforcement, error handling, and audit integration.

---

## 1. Standard Input Schema

Zoë passes the following structure to every Goddess:

```typescript
interface GoddessInput {
  task: string;              // Natural language task description
  context: {
    [key: string]: unknown;  // Domain-specific context (property_id, period, etc.)
  };
  parameters?: {
    [key: string]: unknown;  // Optional structured parameters
  };
  session_id: string;        // Links to zoe_conversations / audit_log
  requested_by: string;      // 'zoe' or user_id
  goddess_id: string;        // UUID from goddesses table
  task_id: string;           // UUID of agent_tasks record
}
```

### Context keys by cluster

| Cluster | Common context keys |
|---|---|
| Financial | `property_id`, `period`, `portfolio_id`, `cost_centre` |
| Real Estate | `property_id`, `asset_type`, `location`, `valuation_date` |
| Legal/Compliance | `document_id`, `contract_id`, `jurisdiction`, `regulation` |
| Operations | `property_id`, `facility_type`, `project_id`, `phase` |
| Intelligence | `topic`, `document_id`, `scope`, `date_range` |
| Strategic | `time_horizon`, `portfolio_id`, `theme`, `scenario_type` |
| Relationship | `stakeholder_id`, `audience`, `purpose`, `communication_goal` |
| Technical | `system`, `repository`, `connector`, `security_domain` |

---

## 2. Standard Output Schema

Every Goddess returns the following structure:

```typescript
interface GoddessOutput {
  result: {
    [key: string]: unknown;  // Domain-specific results
  };
  confidence: number;        // 0.00–1.00 confidence score
  sources: string[];         // Document IDs, URLs, table references cited
  recommendations: string[]; // Actionable recommendations (can be empty array)
  metadata: {
    goddess_id: string;
    goddess_name: string;
    task_id: string;
    tools_used: string[];
    processing_time_ms: number;
  };
  error?: {                  // Present only on failure
    code: string;
    message: string;
    recoverable: boolean;
  };
}
```

### Confidence scoring guide

| Score | Meaning |
|---|---|
| `0.95–1.00` | High confidence — complete data, no ambiguity |
| `0.80–0.94` | Good confidence — minor data gaps or assumptions |
| `0.60–0.79` | Moderate confidence — notable gaps, stated assumptions |
| `0.40–0.59` | Low confidence — significant uncertainty, partial data |
| `0.00–0.39` | Very low — insufficient data, result should not be relied upon |

The `confidence` field must always be populated. If a Goddess cannot determine confidence, she returns `0.50` and explains in `recommendations`.

---

## 3. Permission Enforcement

Each Goddess has a fixed permission set defined in the `goddesses` table. The tool router enforces these limits at runtime.

### Permission levels

| Level | Code | What it allows |
|---|---|---|
| **READ** | `READ` | Retrieve data, search documents, read properties |
| **ANALYZE** | `ANALYZE` | Compute, aggregate, compare, generate insights |
| **WRITE** | `WRITE` | Create tasks, update assets, create reports |
| **ADMIN** | `ADMIN` | Destructive or deployment actions — no Goddess holds this by default |

### Goddess permission summary

| Goddess | READ | ANALYZE | WRITE | ADMIN |
|---|---|---|---|---|
| Finyra | ✅ | ✅ | ❌ | ❌ |
| Gaia | ✅ | ✅ | ❌ | ❌ |
| Jurena | ✅ | ✅ | ❌ | ❌ |
| Electra | ✅ | ✅ | ❌ | ❌ |
| Artemis | ✅ | ✅ | ❌ | ❌ |
| Astraea | ✅ | ✅ | ❌ | ❌ |
| Vesta | ✅ | ✅ | ❌ | ❌ |
| Taxa | ✅ | ✅ | ❌ | ❌ |
| Aurelia | ✅ | ✅ | ❌ | ❌ |
| Fluxa | ✅ | ✅ | ❌ | ❌ |
| Valeria | ✅ | ✅ | ❌ | ❌ |
| Mercuria | ✅ | ✅ | ✅ | ❌ |
| Portia | ✅ | ✅ | ❌ | ❌ |
| Agora | ✅ | ✅ | ❌ | ❌ |
| Regula | ✅ | ✅ | ❌ | ❌ |
| Riskara | ✅ | ✅ | ❌ | ❌ |
| Lex | ✅ | ✅ | ❌ | ❌ |
| Terra | ✅ | ✅ | ❌ | ❌ |
| Doma | ✅ | ✅ | ✅ | ❌ |
| Construa | ✅ | ✅ | ✅ | ❌ |
| Datara | ✅ | ✅ | ❌ | ❌ |
| Sophia | ✅ | ✅ | ✅ | ❌ |
| Papyra | ✅ | ✅ | ❌ | ❌ |
| Athena | ✅ | ✅ | ✅ | ❌ |
| Nova | ✅ | ✅ | ❌ | ❌ |
| Scenara | ✅ | ✅ | ❌ | ❌ |
| Herma | ✅ | ✅ | ❌ | ❌ |
| Stakia | ✅ | ✅ | ✅ | ❌ |
| Lexara | ✅ | ✅ | ✅ | ❌ |
| Reporta | ✅ | ✅ | ✅ | ❌ |
| Techna | ✅ | ✅ | ❌ | ❌ |
| Securis | ✅ | ✅ | ❌ | ❌ |
| Integra | ✅ | ✅ | ❌ | ❌ |

**ADMIN actions are reserved for Zoë only** (with explicit user confirmation).

---

## 4. Tool Access by Goddess

Each Goddess is authorised to call only the tools listed in her profile. The tool router rejects any call not in a Goddess's `tools` array.

### Tool registry (read/analyse tools)

| Tool | Description |
|---|---|
| `get_property(property_id)` | Retrieve full property record |
| `get_portfolio(filters?)` | Retrieve portfolio with optional filters |
| `search_documents(query, filters?)` | Full-text search across document store |
| `get_financials(property_id, period?)` | Retrieve financial data for a property |
| `calculate_cashflow(property_id, period?)` | Compute cashflow analysis |
| `search_github(query, repo?)` | Search GitHub repositories |
| `get_repository_status(repo)` | Get repository health and status |
| `search_terrabox(query, filters?)` | Search Terra Box document archive |

### Tool registry (write tools — WRITE permission required)

| Tool | Description |
|---|---|
| `create_task(title, description, assignee?)` | Create a task in the task system |
| `create_report(type, parameters)` | Initiate report generation |
| `update_asset(asset_id, changes)` | Modify an asset record |

---

## 5. Audit Integration

Every Goddess task execution is recorded in two tables:

### `agent_tasks` record (lifecycle)

```
PENDING   → task created, not yet started
RUNNING   → Goddess is processing
COMPLETE  → result returned successfully
FAILED    → error returned, result is null or partial
```

### `audit_log` record (per tool call)

Every tool call made by a Goddess during execution writes an `audit_log` entry:

```json
{
  "actor":          "Finyra",
  "action":         "ANALYZE",
  "target_table":   "financials",
  "tool_used":      "get_financials",
  "permission_level": "ANALYZE",
  "session_id":     "sess_...",
  "result":         "SUCCESS"
}
```

---

## 6. Error Handling

### Goddess-level errors

| Code | Meaning | Recoverable |
|---|---|---|
| `PERMISSION_DENIED` | Goddess attempted a tool not in her permission set | No |
| `TOOL_FAILED` | A tool call returned an error | Maybe |
| `INSUFFICIENT_DATA` | Not enough data to complete the task | Maybe |
| `TIMEOUT` | Goddess processing exceeded time limit | Yes |
| `LLM_ERROR` | LLM inference failed | Yes |

When a Goddess returns an error:
- `agent_tasks.status` → `FAILED`
- `audit_log.result` → `FAILURE`
- Zoë is notified and may retry or escalate

---

## 7. Implementation Location

```
services/zoe-core/orchestration/   ← Zoë's agent dispatch logic
services/zoe-agents/               ← Individual Goddess implementations
  └── [name]-[domain]/
      ├── README.md                ← Goddess profile
      └── index.[ext]              ← GoddessAgent implementation
```

The base `GoddessAgent` class/interface is implemented in `services/zoe-core/orchestration/` and imported by every Goddess module.

---

## 8. GoddessAgent Base Interface (Pseudocode)

```typescript
abstract class GoddessAgent {
  abstract readonly id: string;         // UUID from goddesses table
  abstract readonly name: string;       // e.g. 'Finyra'
  abstract readonly domain: string;     // e.g. 'Finance'
  abstract readonly permissions: string[];
  abstract readonly tools: string[];

  abstract execute(input: GoddessInput): Promise<GoddessOutput>;

  protected async callTool(
    toolName: string,
    args: Record<string, unknown>
  ): Promise<unknown> {
    // Permission check
    if (!this.tools.includes(toolName)) {
      throw new PermissionError('PERMISSION_DENIED', toolName);
    }
    // Route to tool router → connector → external system
    // Write audit_log entry
  }
}
```

Pilot implementation: **Finyra** (`services/zoe-agents/finyra-finance/`)

---

*Zoë AI Platform – Goddess Interface V1.0*  
*Z1 Real Estate Command Center*  
*© 2026*
