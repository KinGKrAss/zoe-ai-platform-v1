# Zoë AI Platform – Architecture Blueprint V1.0

**Codename:** ZOE-CORE  
**System:** Z1 Real Estate Command Center  
**Version:** V1.0  
**Date:** 2026-08-08  
**Status:** Approved Blueprint

---

## 1. System Overview

```
┌──────────────────────────────────────────────┐
│             Z1 COMMAND CENTER                │
│          Web / Android / PWA                 │
└──────────────────┬───────────────────────────┘
                   │  REST / GraphQL / WebSocket
                   ▼
┌──────────────────────────────────────────────┐
│              ZOË AI PLATFORM                 │
│                 ZOE-CORE                     │
│                                              │
│  ┌────────────┐ ┌────────────┐ ┌──────────┐ │
│  │  ZOE BRAIN │ │ ZOE MEMORY │ │ZOE TOOLS │ │
│  │ Reasoning  │ │ Knowledge  │ │ Actions  │ │
│  └─────┬──────┘ └─────┬──────┘ └────┬─────┘ │
└────────┼──────────────┼─────────────┼────────┘
         └──────────────┼─────────────┘
                        ▼
         ┌──────────────────────────────┐
         │      Z1 INTEGRATION LAYER    │
         └──────────┬───────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   PostgreSQL     GitHub     Terra Box
   Z1 Database  Code / Git  Documents
```

---

## 2. ZOE BRAIN (zoe-core)

The ZOE BRAIN is the AI orchestration layer. It processes user intent, plans actions, retrieves context, and produces responses or triggers tool calls.

### Directory structure

```
services/zoe-core/
├── reasoning/       # LLM call wrappers, chain-of-thought, inference
├── planning/        # Task decomposition, goal planning, step sequencing
├── context/         # Context window management, retrieval-augmented generation
├── intent/          # Intent classification and entity extraction
├── response/        # Response formatting, streaming, validation
└── orchestration/   # Agent orchestration, tool dispatching, flow control
```

### Request lifecycle

```
User Request
    │
    ▼
[intent/]          → classify intent, extract entities
    │
    ▼
[context/]         → load memory, knowledge objects, prior conversations
    │
    ▼
[planning/]        → decompose task into steps; decide agent delegation
    │
    ▼
[reasoning/]       → LLM inference with full context
    │
    ▼
[orchestration/]   → dispatch tool calls or agent sub-tasks
    │
    ▼
[response/]        → format, validate, stream response
    │
    ▼
User / Z1 Command Center
```

### Example

> **User:** "Which properties currently have the highest operating costs?"

1. Intent: `QUERY_FINANCIAL_ANALYSIS`
2. Context: load portfolio context, relevant memory
3. Plan: call `get_portfolio()` → `get_financials()` → `calculate_cashflow()` → `search_documents()`
4. Reason: synthesise results via LLM
5. Orchestrate: delegate risk dimension to Risk Agent (Council of 33)
6. Respond: ranked property list with cost breakdown + relevant document references

---

## 3. ZOE MEMORY (zoe-memory)

Memory is split into three strictly separated layers to prevent mixing identity, episodic memory, and factual knowledge.

```
services/zoe-memory/
├── identity/            # Zoë's system identity (see zoe_identity table)
├── long-term-memory/    # Persistent episodic memory (see zoe_memory table)
├── knowledge-objects/   # Extracted structured knowledge (see ai_knowledge_objects)
├── conversations/       # Conversation history (see zoe_conversations)
├── decisions/           # Decision records (see zoe_decisions)
├── preferences/         # User and system preferences (see zoe_preferences)
└── memory-events/       # Audit trail of memory changes (see zoe_memory_events)
```

### Memory layers

| Layer | Table | Purpose |
|---|---|---|
| **System Identity** | `zoe_identity` | Who Zoë is, her role, values, version |
| **Long-Term Memory** | `zoe_memory` | Persistent facts about users, assets, relationships |
| **Knowledge Objects** | `ai_knowledge_objects` | Structured knowledge extracted from documents and Z1 data |
| **Conversations** | `zoe_conversations` | Conversation threads and messages |
| **Decisions** | `zoe_decisions` | Records of significant decisions made |
| **Preferences** | `zoe_preferences` | User and system-level preferences |
| **Memory Events** | `zoe_memory_events` | Event log of CREATE / UPDATE / ARCHIVE / RESTORE / MERGE |

---

## 4. ZOE IDENTITY

Zoë's identity is an explicitly versioned artifact—not hardcoded in source.

```
ZOE-IDENTITY-V1.0

Name:            Zoë
Designation:     AI Queen / Golden Queen
System:          Z1 Real Estate Command Center
Primary Role:    Central AI Coordination Intelligence
Version:         V1.0

Functions:
  - Strategic coordination
  - Knowledge management
  - Document intelligence
  - Financial intelligence
  - System orchestration
  - Communication
  - Reporting

Network:         Council of 33 AI Agents
Status:          Core Intelligence
```

Every change to identity creates a new version record in `zoe_identity` (V1.0 → V1.1 → V2.0 …).

See: [ZOE-IDENTITY-V1.0.md](../zoe/ZOE-IDENTITY-V1.0.md)

---

## 5. Z1 INTEGRATION LAYER (zoe-connectors)

Zoë does not get raw database or filesystem access. All integrations go through the Integration Layer which enforces permissions.

```
services/zoe-connectors/
├── postgresql/     # PostgreSQL connector (read/write with permission gating)
├── github/         # GitHub API connector (repos, issues, PRs)
└── terrabox/       # Terra Box document connector (search, metadata, PDF)
```

### PostgreSQL connector capabilities

| Operation | Permission Level |
|---|---|
| Read property data | READ |
| Analyse financial positions | ANALYZE |
| Retrieve document metadata | READ |
| Detect relationships | ANALYZE |
| Generate reports | ANALYZE |
| Modify data | WRITE |

### GitHub connector capabilities (planned)

| Operation | Permission Level |
|---|---|
| Analyse repo structure | READ |
| Read issues / PRs | READ |
| Summarise development status | ANALYZE |
| Search technical documentation | READ |
| Create issues / PRs | WRITE (special permission) |
| Modify code | ADMIN |

### Terra Box connector capabilities (planned)

| Operation | Permission Level |
|---|---|
| Search documents | READ |
| Retrieve document metadata | READ |
| Analyse PDFs | ANALYZE |
| Link documents to assets | WRITE |
| Archive documents | WRITE (confirmation required) |

---

## 6. ZOE TOOL SYSTEM

Zoë interacts with all systems through a permissioned tool router. Direct database or API access is not permitted.

```
Zoë (reasoning/orchestration)
        │
        ▼
   Tool Router
        │
        ▼
  Permission Check  ←── zoe_security / user context
        │
        ▼
      Tool
        │
        ▼
  External System
```

### Read / Analyse tools

```
get_property(property_id)
get_portfolio(filters?)
search_documents(query, filters?)
get_financials(property_id, period?)
calculate_cashflow(property_id, period?)
search_github(query, repo?)
get_repository_status(repo)
search_terrabox(query, filters?)
```

### Write tools (require WRITE permission)

```
create_task(title, description, assignee?)
create_report(type, parameters)
update_asset(asset_id, changes)
archive_document(document_id, reason)
```

### Dangerous tools (require explicit confirmation)

```
delete_record(table, record_id)       # DELETE – confirmation required
transfer_ownership(asset_id, to)      # TRANSFER – confirmation required
publish_report(report_id, audience)   # PUBLISH – confirmation required
deploy_service(service_id, env)       # DEPLOY – ADMIN only
```

---

## 7. ZOE SECURITY

Four permission levels control all Zoë operations:

| Level | Code | Description |
|---|---|---|
| **READ** | `READ` | View data, retrieve information |
| **ANALYZE** | `ANALYZE` | Compute, aggregate, summarise |
| **WRITE** | `WRITE` | Create or modify records |
| **ADMIN** | `ADMIN` | Destructive or deployment actions |

### Permission matrix

| Action | Permission | Confirmation |
|---|---|---|
| View property | READ | No |
| Analyse document | ANALYZE | No |
| Analyse portfolio | ANALYZE | No |
| Generate report | ANALYZE | No |
| Create task | WRITE | No |
| Modify data | WRITE | No |
| Archive document | WRITE | Yes |
| Delete record | ADMIN | Yes + reason |
| Modify GitHub code | ADMIN | Yes |
| Deploy service | ADMIN | Yes + explicit approval |

---

## 8. AUDIT LOG

Every significant action is recorded in `audit_log`.

```sql
-- Example audit record
{
  "timestamp":  "2026-08-08T17:42:00Z",
  "user":       "Rene",
  "actor":      "Zoe",
  "action":     "UPDATE",
  "table":      "properties",
  "record_id":  "8c7a3f...",
  "changes":    { "before": {...}, "after": {...} },
  "result":     "SUCCESS",
  "tool":       "update_asset",
  "session_id": "sess_..."
}
```

The audit log enables answering: *"Who changed this value, when, and why?"*

---

## 9. ZOE REPORT ENGINE (zoe-reports)

A dedicated service for generating structured reports.

```
services/zoe-reports/
```

### Report types

- Monthly property reports
- Portfolio / asset overviews
- Financial reports
- Document inventory reports
- Project status reports
- Management summaries

### Pipeline

```
Data Sources (PostgreSQL / TerraBox / GitHub)
        │
        ▼
   Data Retrieval (Tool System)
        │
        ▼
   Analysis (ZOE BRAIN)
        │
        ▼
   Validation
        │
        ▼
   Report Engine (zoe-reports)
        │
        ├── PDF output
        ├── JSON output
        └── Dashboard data
```

---

## 10. COUNCIL OF 33 (zoe-agents)

Zoë orchestrates a network of specialist agents. Each agent has domain expertise and is called by Zoë's orchestration layer when needed.

```
services/zoe-agents/
├── finance/       # Financial analysis agent
├── legal/         # Legal review agent
├── realestate/    # Real estate specialist agent
├── energy/        # Energy / sustainability agent
├── strategy/      # Strategic planning agent
├── research/      # Research and data retrieval agent
├── diplomacy/     # Communication and negotiation agent
├── technology/    # Technical / IT agent
├── compliance/    # Regulatory compliance agent
├── risk/          # Risk assessment agent
└── communication/ # Reporting and communication agent
```

### Orchestration example

> **Request:** "Analyse this real estate project."

```
Zoë (orchestration)
        │
   ┌────┴────────────┐
   ▼                 ▼
Real Estate Agent   Finance Agent
        │                 │
        └─────────┬───────┘
                  ▼
             Legal Agent
                  │
                  ▼
              Risk Agent
                  │
                  ▼
                Zoë
                  │
                  ▼
          Final Analysis
```

Each agent is a self-contained module with its own tool access permissions.

---

## 11. Full Data Flow Diagram

```
ZOE IDENTITY
      │
      ▼
ZOE MEMORY
      │
      ▼
ZOE KNOWLEDGE OBJECTS
      │
      ▼
ZOE-CORE (Brain)
      │
   ┌──┴──┐
   ▼      ▼
GitHub  Terra Box
   │      │
   └──┬───┘
      ▼
Z1 DATABASE (PostgreSQL)
      │
      ▼
Z1 COMMAND CENTER
```

---

## 12. Technology Decisions (V1.0 – Stack-Agnostic)

| Component | Recommendation | Notes |
|---|---|---|
| Backend API | Any (Node.js / Python / Go) | Choose at implementation phase |
| Database | PostgreSQL | Specified in architecture |
| AI / LLM | Provider-agnostic interface | Abstracted behind reasoning/ module |
| Document store | Terra Box | Via zoe-connectors/terrabox |
| Auth | JWT / OAuth2 | Integrate with Z1 auth system |
| Deployment | Docker / container-based | See infrastructure/docker |

---

*Zoë AI Platform V1.0 – Architecture Blueprint*  
*Z1 Real Estate Command Center*  
*© 2026*
