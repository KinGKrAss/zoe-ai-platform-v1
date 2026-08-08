# Zoë AI Platform – GitHub Project Plan V1.0

**Version:** V1.0  
**System:** Z1 Real Estate Command Center  
**Date:** 2026-08-08

---

## Project Structure

This document defines the suggested GitHub Projects board, milestones, epics, and initial issues for building the Zoë AI Platform V1.0.

---

## Milestones

| # | Milestone | Goal |
|---|---|---|
| M1 | **Foundation** | Repository structure, documentation, database schema |
| M2 | **ZOE MEMORY** | Identity, memory, knowledge object tables and service |
| M3 | **ZOE BRAIN** | Core orchestration, intent, reasoning, response |
| M4 | **ZOE TOOLS** | Tool router, permission system, connector stubs |
| M5 | **Integration** | PostgreSQL, GitHub, Terra Box connectors |
| M6 | **Report Engine** | Report generation pipeline |
| M7 | **Council of 33** | Agent framework and first specialist agents |
| M8 | **Z1 Integration** | Connect to Z1 Command Center frontend |

---

## Epics (Labels)

| Label | Description |
|---|---|
| `epic:foundation` | Repository scaffold, docs, CI setup |
| `epic:memory` | ZOE MEMORY layer (identity, memory, knowledge) |
| `epic:brain` | ZOE BRAIN / zoe-core (reasoning, planning, orchestration) |
| `epic:tools` | ZOE TOOL SYSTEM (router, permissions, tools) |
| `epic:integration` | Z1 Integration Layer (connectors) |
| `epic:security` | Security model, permission enforcement |
| `epic:audit` | Audit logging |
| `epic:reports` | Report engine |
| `epic:agents` | Council of 33 agent framework |
| `epic:devops` | Docker, deployment, CI/CD |

---

## Initial Issues

### M1 – Foundation

- [ ] **[FOUNDATION-01]** Review and finalise architecture blueprint V1.0
  - Docs: `docs/architecture/ZOE-BLUEPRINT-V1.0.md`
  - Labels: `epic:foundation`, `documentation`

- [ ] **[FOUNDATION-02]** Set up PostgreSQL development environment
  - Docker compose for local Postgres
  - Labels: `epic:foundation`, `epic:devops`

- [ ] **[FOUNDATION-03]** Implement database migrations (001–008)
  - All core Zoë tables
  - Labels: `epic:foundation`, `epic:memory`

- [ ] **[FOUNDATION-04]** Seed ZOE-IDENTITY-V1.0 into database
  - `database/seeds/001_zoe_identity_v1.sql`
  - Labels: `epic:foundation`, `epic:memory`

- [ ] **[FOUNDATION-05]** Set up CI pipeline (lint, test, migrate)
  - Labels: `epic:foundation`, `epic:devops`

---

### M2 – ZOE MEMORY

- [ ] **[MEMORY-01]** Implement `zoe_memory` CRUD service
  - Labels: `epic:memory`

- [ ] **[MEMORY-02]** Implement `zoe_memory_events` event sourcing
  - All CREATE / UPDATE / ARCHIVE / RESTORE / MERGE flows
  - Labels: `epic:memory`, `epic:audit`

- [ ] **[MEMORY-03]** Implement `ai_knowledge_objects` service
  - Labels: `epic:memory`

- [ ] **[MEMORY-04]** Implement `zoe_conversations` and `zoe_messages` service
  - Labels: `epic:memory`

- [ ] **[MEMORY-05]** Implement `zoe_preferences` service
  - Labels: `epic:memory`

- [ ] **[MEMORY-06]** Identity versioning: create new version endpoint
  - Labels: `epic:memory`

---

### M3 – ZOE BRAIN

- [ ] **[BRAIN-01]** Implement intent classification module (`services/zoe-core/intent/`)
  - Labels: `epic:brain`

- [ ] **[BRAIN-02]** Implement context loading module (`services/zoe-core/context/`)
  - Retrieval-augmented generation from memory + knowledge objects
  - Labels: `epic:brain`, `epic:memory`

- [ ] **[BRAIN-03]** Implement planning module (`services/zoe-core/planning/`)
  - Labels: `epic:brain`

- [ ] **[BRAIN-04]** Implement LLM reasoning adapter (`services/zoe-core/reasoning/`)
  - Provider-agnostic interface
  - Labels: `epic:brain`

- [ ] **[BRAIN-05]** Implement orchestration / agent dispatch (`services/zoe-core/orchestration/`)
  - Labels: `epic:brain`, `epic:agents`

- [ ] **[BRAIN-06]** Implement response formatter (`services/zoe-core/response/`)
  - Labels: `epic:brain`

---

### M4 – ZOE TOOLS

- [ ] **[TOOLS-01]** Implement tool router
  - Labels: `epic:tools`

- [ ] **[TOOLS-02]** Implement permission check middleware
  - READ / ANALYZE / WRITE / ADMIN
  - Labels: `epic:tools`, `epic:security`

- [ ] **[TOOLS-03]** Implement confirmation flow for dangerous tools
  - Labels: `epic:tools`, `epic:security`

- [ ] **[TOOLS-04]** Implement read tools: `get_property`, `get_portfolio`, `search_documents`
  - Labels: `epic:tools`, `epic:integration`

- [ ] **[TOOLS-05]** Implement analysis tools: `get_financials`, `calculate_cashflow`
  - Labels: `epic:tools`, `epic:integration`

- [ ] **[TOOLS-06]** Implement write tools: `create_task`, `create_report`, `update_asset`
  - Labels: `epic:tools`, `epic:integration`

---

### M5 – Integration

- [ ] **[INT-01]** Implement PostgreSQL connector (`services/zoe-connectors/postgresql/`)
  - Labels: `epic:integration`

- [ ] **[INT-02]** Implement GitHub connector stub (`services/zoe-connectors/github/`)
  - Labels: `epic:integration`

- [ ] **[INT-03]** Implement Terra Box connector stub (`services/zoe-connectors/terrabox/`)
  - Labels: `epic:integration`

- [ ] **[INT-04]** Implement permission gating in Integration Layer
  - Labels: `epic:integration`, `epic:security`

---

### M6 – Audit & Security

- [ ] **[SEC-01]** Implement `audit_log` write service
  - Labels: `epic:audit`, `epic:security`

- [ ] **[SEC-02]** Integrate audit logging into all WRITE and ADMIN tool calls
  - Labels: `epic:audit`, `epic:security`

- [ ] **[SEC-03]** Implement permission enforcement tests
  - Labels: `epic:security`

---

### M7 – Report Engine

- [ ] **[REP-01]** Design report template system (`services/zoe-reports/`)
  - Labels: `epic:reports`

- [ ] **[REP-02]** Implement monthly property report generator
  - Labels: `epic:reports`

- [ ] **[REP-03]** Implement portfolio overview report
  - Labels: `epic:reports`

- [ ] **[REP-04]** Implement PDF export pipeline
  - Labels: `epic:reports`

---

### M8 – Council of 33

- [ ] **[AGENT-01]** Design agent interface / contract
  - Labels: `epic:agents`

- [ ] **[AGENT-02]** Implement Finance Agent (`services/zoe-agents/finance/`)
  - Labels: `epic:agents`

- [ ] **[AGENT-03]** Implement Real Estate Agent (`services/zoe-agents/realestate/`)
  - Labels: `epic:agents`

- [ ] **[AGENT-04]** Implement Legal Agent (`services/zoe-agents/legal/`)
  - Labels: `epic:agents`

- [ ] **[AGENT-05]** Implement Risk Agent (`services/zoe-agents/risk/`)
  - Labels: `epic:agents`

- [ ] **[AGENT-06]** Implement agent orchestration protocol in `zoe-core/orchestration/`
  - Labels: `epic:agents`, `epic:brain`

---

## GitHub Projects Board Columns

| Column | Description |
|---|---|
| **Backlog** | Issues not yet scheduled |
| **Ready** | Scoped, estimated, ready to pick up |
| **In Progress** | Currently being worked on |
| **Review** | In PR / code review |
| **Done** | Merged and deployed |

---

## Suggested Labels

```
Type:
  bug
  feature
  documentation
  refactor
  security

Epic:
  epic:foundation
  epic:memory
  epic:brain
  epic:tools
  epic:integration
  epic:security
  epic:audit
  epic:reports
  epic:agents
  epic:devops

Priority:
  priority:critical
  priority:high
  priority:medium
  priority:low

Status:
  status:blocked
  status:needs-spec
  status:ready
```

---

*Zoë AI Platform – GitHub Project Plan V1.0*  
*Z1 Real Estate Command Center*  
*© 2026*
