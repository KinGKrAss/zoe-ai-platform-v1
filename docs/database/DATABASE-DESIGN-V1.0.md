# Zoë AI Platform – Database Design V1.0

**Version:** V1.0  
**System:** Z1 Real Estate Command Center  
**Date:** 2026-08-08  
**Status:** Design Document

---

## Overview

This document describes the core database tables for the Zoë AI Platform. All tables target **PostgreSQL**. The design prioritises:

- **Identity versioning** – Zoë's identity is a versionable record, not a config file
- **Memory continuity** – memory is never overwritten, only versioned (CREATE → UPDATE → ARCHIVE)
- **Full auditability** – every significant action is recorded in `audit_log`
- **Knowledge separation** – identity, episodic memory, and factual knowledge are separate concerns

---

## Table Overview

| Table | Purpose |
|---|---|
| `zoe_identity` | Zoë's versioned system identity |
| `zoe_memory` | Long-term episodic memory entries |
| `zoe_memory_events` | Audit trail of memory changes |
| `zoe_knowledge_objects` | Extracted factual knowledge objects |
| `zoe_conversations` | Conversation threads and messages |
| `zoe_decisions` | Significant decisions Zoë has made |
| `zoe_preferences` | User and system preferences |
| `audit_log` | System-wide action audit log |

---

## Schema

### zoe_identity

Stores Zoë's versioned identity. Only one record has `status = 'ACTIVE'` at any time.

```sql
CREATE TABLE zoe_identity (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  version                 VARCHAR(20)   NOT NULL,          -- e.g. 'V1.0', 'V1.1'
  name                    VARCHAR(100)  NOT NULL,
  designation             VARCHAR(200),
  system_name             VARCHAR(200)  NOT NULL,
  primary_role            TEXT          NOT NULL,
  functions               JSONB         NOT NULL DEFAULT '[]',
  values                  JSONB         NOT NULL DEFAULT '[]',
  communication_principles JSONB        NOT NULL DEFAULT '[]',
  network                 VARCHAR(200),
  status                  VARCHAR(20)   NOT NULL DEFAULT 'ACTIVE',  -- ACTIVE | ARCHIVED
  valid_from              TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  valid_to                TIMESTAMPTZ,
  created_at              TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  created_by              VARCHAR(100)  NOT NULL DEFAULT 'system',
  notes                   TEXT,
  CONSTRAINT zoe_identity_status_check CHECK (status IN ('ACTIVE','ARCHIVED','DRAFT'))
);

CREATE INDEX idx_zoe_identity_status  ON zoe_identity(status);
CREATE INDEX idx_zoe_identity_version ON zoe_identity(version);
```

---

### zoe_memory

Long-term persistent memory. Individual memory entries are never overwritten—updates create new versions via `zoe_memory_events`.

```sql
CREATE TABLE zoe_memory (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  memory_key    VARCHAR(200)  NOT NULL,       -- unique semantic key
  memory_type   VARCHAR(100)  NOT NULL,       -- e.g. 'FACT','RELATIONSHIP','PREFERENCE','CONTEXT'
  subject       VARCHAR(200),                 -- what/who this memory is about
  content       TEXT          NOT NULL,
  metadata      JSONB         NOT NULL DEFAULT '{}',
  confidence    NUMERIC(3,2)  NOT NULL DEFAULT 1.0,  -- 0.0–1.0
  source        VARCHAR(200),                 -- origin: user input, document, agent, etc.
  status        VARCHAR(20)   NOT NULL DEFAULT 'ACTIVE',  -- ACTIVE | ARCHIVED | MERGED
  version       INTEGER       NOT NULL DEFAULT 1,
  created_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  archived_at   TIMESTAMPTZ,
  CONSTRAINT zoe_memory_status_check CHECK (status IN ('ACTIVE','ARCHIVED','MERGED')),
  CONSTRAINT zoe_memory_confidence_check CHECK (confidence BETWEEN 0.0 AND 1.0)
);

CREATE UNIQUE INDEX idx_zoe_memory_key_active ON zoe_memory(memory_key) WHERE status = 'ACTIVE';
CREATE INDEX idx_zoe_memory_type    ON zoe_memory(memory_type);
CREATE INDEX idx_zoe_memory_subject ON zoe_memory(subject);
CREATE INDEX idx_zoe_memory_status  ON zoe_memory(status);
```

---

### zoe_memory_events

Event sourcing log for all memory changes. Enables full reconstruction of memory state at any point in time.

```sql
CREATE TYPE memory_event_type AS ENUM ('CREATE','UPDATE','ARCHIVE','RESTORE','MERGE','DELETE');

CREATE TABLE zoe_memory_events (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  memory_id     UUID          NOT NULL REFERENCES zoe_memory(id),
  event_type    memory_event_type NOT NULL,
  previous_content TEXT,                      -- snapshot before change
  new_content   TEXT,                         -- snapshot after change
  previous_metadata JSONB,
  new_metadata  JSONB,
  reason        TEXT,
  actor         VARCHAR(200)  NOT NULL,        -- 'zoe', 'user:Rene', 'agent:finance', etc.
  session_id    VARCHAR(200),
  created_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_zoe_memory_events_memory_id  ON zoe_memory_events(memory_id);
CREATE INDEX idx_zoe_memory_events_event_type ON zoe_memory_events(event_type);
CREATE INDEX idx_zoe_memory_events_created_at ON zoe_memory_events(created_at);
```

---

### ai_knowledge_objects

Structured factual knowledge extracted from documents, Z1 data, or agent analysis. Separate from episodic memory.

```sql
CREATE TABLE ai_knowledge_objects (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  object_type     VARCHAR(100)  NOT NULL,   -- 'PROPERTY','FINANCIAL','LEGAL','REGULATORY', etc.
  title           VARCHAR(300)  NOT NULL,
  content         TEXT          NOT NULL,
  structured_data JSONB         NOT NULL DEFAULT '{}',
  source_type     VARCHAR(100),             -- 'DOCUMENT','DATABASE','AGENT','USER'
  source_id       VARCHAR(200),             -- reference to originating record
  source_url      TEXT,
  confidence      NUMERIC(3,2)  NOT NULL DEFAULT 1.0,
  tags            TEXT[]        NOT NULL DEFAULT '{}',
  status          VARCHAR(20)   NOT NULL DEFAULT 'ACTIVE',
  version         INTEGER       NOT NULL DEFAULT 1,
  created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  CONSTRAINT ai_knowledge_objects_status_check CHECK (status IN ('ACTIVE','ARCHIVED','SUPERSEDED')),
  CONSTRAINT ai_knowledge_objects_confidence_check CHECK (confidence BETWEEN 0.0 AND 1.0)
);

CREATE INDEX idx_ai_knowledge_objects_type   ON ai_knowledge_objects(object_type);
CREATE INDEX idx_ai_knowledge_objects_tags   ON ai_knowledge_objects USING GIN(tags);
CREATE INDEX idx_ai_knowledge_objects_data   ON ai_knowledge_objects USING GIN(structured_data);
CREATE INDEX idx_ai_knowledge_objects_status ON ai_knowledge_objects(status);
```

---

### zoe_conversations

Conversation threads between users and Zoë.

```sql
CREATE TABLE zoe_conversations (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id      VARCHAR(200)  NOT NULL,
  user_id         VARCHAR(200),
  title           VARCHAR(300),
  status          VARCHAR(20)   NOT NULL DEFAULT 'ACTIVE',  -- ACTIVE | CLOSED | ARCHIVED
  context         JSONB         NOT NULL DEFAULT '{}',      -- session context snapshot
  message_count   INTEGER       NOT NULL DEFAULT 0,
  started_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  last_message_at TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  closed_at       TIMESTAMPTZ
);

CREATE TABLE zoe_messages (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID          NOT NULL REFERENCES zoe_conversations(id),
  role            VARCHAR(20)   NOT NULL,  -- 'user' | 'assistant' | 'tool' | 'system'
  content         TEXT          NOT NULL,
  tool_calls      JSONB,                   -- tool calls made in this turn
  tool_results    JSONB,                   -- results of tool calls
  tokens_used     INTEGER,
  model           VARCHAR(100),
  created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_zoe_conversations_session  ON zoe_conversations(session_id);
CREATE INDEX idx_zoe_conversations_user     ON zoe_conversations(user_id);
CREATE INDEX idx_zoe_messages_conversation  ON zoe_messages(conversation_id);
CREATE INDEX idx_zoe_messages_created_at    ON zoe_messages(created_at);
```

---

### zoe_decisions

Records significant decisions Zoë has made or recommended.

```sql
CREATE TABLE zoe_decisions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  decision_type   VARCHAR(100)  NOT NULL,
  title           VARCHAR(300)  NOT NULL,
  description     TEXT          NOT NULL,
  rationale       TEXT,
  alternatives    JSONB         NOT NULL DEFAULT '[]',
  outcome         VARCHAR(100),            -- 'ACCEPTED','REJECTED','PENDING','IMPLEMENTED'
  related_entities JSONB        NOT NULL DEFAULT '[]',  -- linked properties, assets, etc.
  conversation_id UUID          REFERENCES zoe_conversations(id),
  decided_by      VARCHAR(200),
  decided_at      TIMESTAMPTZ,
  created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_zoe_decisions_type    ON zoe_decisions(decision_type);
CREATE INDEX idx_zoe_decisions_outcome ON zoe_decisions(outcome);
```

---

### zoe_preferences

User and system-level preferences.

```sql
CREATE TABLE zoe_preferences (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scope           VARCHAR(20)   NOT NULL,  -- 'USER' | 'SYSTEM' | 'AGENT'
  scope_id        VARCHAR(200),            -- user_id or agent_id if scope != SYSTEM
  preference_key  VARCHAR(200)  NOT NULL,
  preference_value JSONB        NOT NULL,
  description     TEXT,
  created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  UNIQUE (scope, scope_id, preference_key)
);

CREATE INDEX idx_zoe_preferences_scope ON zoe_preferences(scope, scope_id);
```

---

### audit_log

System-wide audit trail for all significant actions.

```sql
CREATE TABLE audit_log (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  user_id         VARCHAR(200),
  user_label      VARCHAR(200),
  actor           VARCHAR(200)  NOT NULL,  -- 'zoe', 'user:Rene', 'agent:finance'
  action          VARCHAR(50)   NOT NULL,  -- 'CREATE','READ','UPDATE','DELETE','ANALYZE','GENERATE'
  target_table    VARCHAR(200),
  target_record   VARCHAR(200),
  tool_used       VARCHAR(200),
  permission_level VARCHAR(20),            -- 'READ','ANALYZE','WRITE','ADMIN'
  changes         JSONB,                   -- { before: {}, after: {} }
  result          VARCHAR(20)   NOT NULL,  -- 'SUCCESS','FAILURE','DENIED'
  error_message   TEXT,
  session_id      VARCHAR(200),
  conversation_id UUID,
  ip_address      INET,
  metadata        JSONB         NOT NULL DEFAULT '{}'
);

CREATE INDEX idx_audit_log_timestamp  ON audit_log(timestamp);
CREATE INDEX idx_audit_log_user       ON audit_log(user_id);
CREATE INDEX idx_audit_log_actor      ON audit_log(actor);
CREATE INDEX idx_audit_log_action     ON audit_log(action);
CREATE INDEX idx_audit_log_result     ON audit_log(result);
CREATE INDEX idx_audit_log_target     ON audit_log(target_table, target_record);
```

---

## Event / Versioning Strategy

### Memory versioning (never overwrite)

```
Memory record CREATED (event: CREATE, version: 1)
        │
        ▼
Content updated  (event: UPDATE, version: 2 – old content stored in event)
        │
        ▼
Memory archived  (event: ARCHIVE – record marked status='ARCHIVED')
        │
        ▼
Memory restored  (event: RESTORE – new ACTIVE record created from archived)
```

### Identity versioning (explicit version numbers)

```
V1.0 ACTIVE ──── change needed ────▶ V1.1 ACTIVE
                                      V1.0 ARCHIVED (valid_to set)
```

### Knowledge object versioning

```
Object ACTIVE (version: 1)
        │
        ▼ new extract supersedes it
Object SUPERSEDED (version: 1, status: 'SUPERSEDED')
New Object ACTIVE (version: 1)
```

---

## Migration Strategy

All schema changes are managed as numbered migrations in `database/migrations/`.

```
database/migrations/
├── 001_create_zoe_identity.sql
├── 002_create_zoe_memory.sql
├── 003_create_zoe_memory_events.sql
├── 004_create_ai_knowledge_objects.sql
├── 005_create_zoe_conversations.sql
├── 006_create_zoe_decisions.sql
├── 007_create_zoe_preferences.sql
└── 008_create_audit_log.sql
```

Seed data for V1.0 identity is in `database/seeds/001_zoe_identity_v1.sql`.

---

*Zoë AI Platform – Database Design V1.0*  
*Z1 Real Estate Command Center*  
*© 2026*
