# Zoë AI Platform – Architecture Blueprint V1.0

**Codename:** ZOE-CORE  
**System:** Z1 Real Estate Command Center  
**Version:** V1.0  
**Date:** 2026-08-14  
**Status:** Approved Blueprint

---

## 1. Executive Summary

This document is the architectural baseline for the Zoë AI Platform V1.0. It combines the original ZOE-CORE design with the enforced five-pillar contract: **Zoë Identity, Tool Contracts, Memory Core, FORTUNA, and Z1 API**.

The architecture enforces strict separation of identity, permissions, persistent memory, financial/market data, and security orchestration.

## 2. Five-Pillar Platform Architecture

```text
                 ┌─────────────────────┐
                 │   Zoë Identity      │
                 │  "Wer ist Zoë?"     │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │    Tool Contracts   │
                 │ "Was darf Zoë?"     │
                 └──────────┬──────────┘
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
    ┌─────────────────┐          ┌─────────────────┐
    │   Memory Core   │          │     FORTUNA     │
    │ "Was weiß Zoë?" │          │ Finanz-/Marktdaten│
    └────────┬────────┘          └────────┬────────┘
             │                            │
             └──────────────┬─────────────┘
                            ▼
                 ┌─────────────────────┐
                 │       Z1 API        │
                 │ Security + Routing  │
                 │ + Orchestration     │
                 └──────────┬──────────┘
                            │
                            ▼
                      Z1 Android
```

## 3. System Components

### 3.1 ZOE BRAIN (`services/zoe-core`)

The reasoning and coordination layer processes user intent, retrieves context, plans actions, invokes permitted tools, and formats responses.

```text
services/zoe-core/
├── reasoning/
├── planning/
├── context/
├── intent/
├── response/
└── orchestration/
```

### 3.2 Zoë Identity

**Core question:** Who is Zoë?

`docs/zoe/ZOE-IDENTITY-V1.0.md` is the authoritative human-readable identity record. Version 1.0 remains immutable; changes require a new identity version.

The database seed `database/seeds/001_zoe_identity_v1.sql` provides the controlled V1.0 persistence layer.

```text
Identity
├── version
├── role
├── functions
├── values
├── network
└── status
```

### 3.3 Memory Core (`services/zoe-memory`)

**Core question:** What may become durable Zoë knowledge?

Memory is strictly separated into identity, long-term memory, knowledge objects, conversations, decisions, preferences, and memory events.

```text
Observation
    ↓
Memory Candidate
    ↓
Review / Policy
    ↓
Durable Memory
```

Short-lived API data does not become durable memory automatically. Ownership, review state, source, timestamps, and audit context must be preserved.

### 3.4 Tool Contracts

**Core question:** What may Zoë do?

Every capability is explicit and permissioned.

```text
Tool
├── name
├── permission
├── description
├── input_schema
├── output_schema
└── audit_required
```

Canonical contracts live under `docs/zoe/contracts/`.

### 3.5 FORTUNA

**Core question:** Which financial and market data is available?

```text
FORTUNA
│
├── Portfolio
├── Financial Intelligence
├── Asset Data
└── CryptoMarketData
       │
       └── CoinMarketCap
```

Provider credentials such as `COINMARKETCAP_API_KEY` remain exclusively in the backend secret store. They are never shipped to Android, stored in tool definitions, or persisted as Memory Core content.

### 3.6 Z1 API Gateway

**Core question:** Who may execute what, and through which path?

```text
Request
  → JWT
  → Authentication
  → Authorization
  → PolicyEngine
  → Orchestrator
  → Tool / Service
  → Audit
  → Response
```

The OpenAPI blueprint is maintained at `docs/architecture/Z1-API-GATEWAY-V1.0.yaml`.

## 4. Z1 Security and Orchestration

```text
Z1 API Gateway
      ↓
Security
      ↓
Orchestrator
      ↓
TaskRegistry
      ↓
Audit Log
      ↓
Memory Core / FORTUNA / Tools
```

### Security model

JWT claims may include `sub`, `role`, `scopes`, and `device_id`.

Base roles:

```text
OPERATOR  → READ, ANALYZE
ANALYST   → READ, ANALYZE, restricted WRITE
ADMIN     → READ, ANALYZE, WRITE, ADMIN
KI-SYSTEM → ZOEREAD, ZOEANALYZE, ZOEWRITEMEMORY, tool-specific scopes
```

Every tool invocation must satisfy both the task's `tools_allowed` list and the actor's effective scopes.

### Task lifecycle

```text
PENDING → RUNNING → DONE
                  ↘ FAILED
```

`zoe_tasks` is the TaskRegistry persistence model. `audit_log` records significant actions and request correlation.

## 5. Critical Data Isolation

Memory Core and FORTUNA do not write directly into each other.

```text
CoinMarketCap
      ↓
FORTUNA
      ↓
Observation
      ↓
Zoë Analysis
      ↓
Memory Candidate
      ↓
Policy / Review
      ↓
Durable Memory
```

This prevents live market feeds from polluting durable memory.

## 6. Z1 Client Boundary

```text
Android
   │ HTTPS + JWT
   ▼
Z1 API Gateway
   │
   ├── Security
   ├── Policy Engine
   ├── Audit
   │
   ▼
Z1 Orchestrator
   │
   ├── Zoë Core
   ├── Memory Core
   ├── FORTUNA
   └── Tool Registry
```

Android is a client only. It must never access PostgreSQL directly and must never contain provider API keys.

## 7. Original ZOE Memory Layers

| Layer | Table | Purpose |
|---|---|---|
| **System Identity** | `zoe_identity` | Who Zoë is, role, values, version |
| **Long-Term Memory** | `zoe_memory` | Persistent facts and relationships |
| **Knowledge Objects** | `ai_knowledge_objects` | Structured extracted knowledge |
| **Conversations** | `zoe_conversations` | Conversation threads/messages |
| **Decisions** | `zoe_decisions` | Significant decision records |
| **Preferences** | `zoe_preferences` | User/system preferences |
| **Memory Events** | `zoe_memory_events` | CREATE / UPDATE / ARCHIVE / RESTORE / MERGE events |

## 8. Integration Layer

Zoë does not receive raw database or filesystem access. Integrations are permission-gated.

```text
services/zoe-connectors/
├── postgresql/
├── github/
└── terrabox/
```

The GitHub connector is the intended boundary for repository, issue, PR, and Project operations; direct uncontrolled GitHub access is not part of the Zoë core.

## 9. Audit and Observability

Every significant action records:

```text
request_id
actor_type
actor_id
action
resource
result
metadata
created_at
```

A request ID should propagate from Android through the Gateway and Orchestrator into downstream services. Write operations should support idempotency keys where duplicate execution could be harmful.

Recommended Prometheus metrics include:

```text
z1_requests_total
z1_request_duration_seconds
z1_zoe_tasks_total
z1_memory_writes_total
z1_tool_calls_total
```

## 10. Repository Service Map

```text
apps/
└── android/

services/
├── z1-gateway/
├── z1-orchestrator/
├── zoe-core/
├── zoe-memory/
├── zoe-connectors/
├── zoe-reports/
├── zoe-agents/
└── fortuna/
    └── crypto-market-data/

docs/
├── architecture/
└── zoe/
    ├── contracts/
    └── architecture/

database/
├── migrations/
└── seeds/
```

## 11. Full Request / Data Flow

```text
Z1 Android
    │
    ▼
Z1 API Gateway
    │
    ├── JWT / Security
    ├── Policy
    └── Audit
    │
    ▼
Z1 Orchestrator
    │
    ├── Zoë Core ──────── Memory Core
    │                         ▲
    │                         │ reviewed candidates
    ├── Tool Registry        │
    │       │                │
    │       └──── FORTUNA ───┘
    │                │
    │                └── CryptoMarketData → CoinMarketCap
    │
    └── other Z1 services
```

## 12. Implementation Status

This document is the **architectural baseline**, not a claim that every component is production-ready.

Implemented foundations on the active feature branch include:

- Zoë Identity V1.0 documentation and seed
- Identity / Memory / Tool contract schemas
- Z1 API Gateway OpenAPI blueprint
- Z1 Orchestrator core skeleton
- Gateway security policy skeleton
- TaskRegistry and audit database migration
- FORTUNA CryptoMarketData integration foundation
- Z1 Android client scaffold

Production hardening still requires real JWT verification, persistent repositories, complete API route wiring, database integration, observability deployment, automated tests, and deployment configuration.

---

*Zoë AI Platform V1.0 – Architecture Blueprint*  
*Z1 Real Estate Command Center*  
*© 2026*
