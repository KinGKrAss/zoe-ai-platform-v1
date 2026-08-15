-- Migration: 016_create_council_of_33.sql
-- Zoë AI Platform V1.0 – Council of 33 registry and orchestration metadata
--
-- Renumbered from the duplicate 009 prefix so migration ordering is deterministic.

CREATE TABLE IF NOT EXISTS council_agents (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_code        VARCHAR(20) NOT NULL UNIQUE,
  name              VARCHAR(100) NOT NULL UNIQUE,
  domain            VARCHAR(100) NOT NULL,
  title             VARCHAR(200) NOT NULL,
  capabilities      JSONB NOT NULL DEFAULT '[]',
  status            VARCHAR(20) NOT NULL DEFAULT 'reconstructed',
  is_active         BOOLEAN NOT NULL DEFAULT TRUE,
  version           VARCHAR(20) NOT NULL DEFAULT '1.0',
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT council_agents_status_check CHECK (status IN ('confirmed','reconstructed','proposed','deprecated'))
);

CREATE INDEX IF NOT EXISTS idx_council_agents_domain ON council_agents(domain);
CREATE INDEX IF NOT EXISTS idx_council_agents_status ON council_agents(status);
CREATE INDEX IF NOT EXISTS idx_council_agents_active ON council_agents(is_active);

CREATE TABLE IF NOT EXISTS council_agent_tools (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id          UUID NOT NULL REFERENCES council_agents(id) ON DELETE CASCADE,
  tool_name         VARCHAR(200) NOT NULL,
  permission_level  VARCHAR(20) NOT NULL,
  confirmation_required BOOLEAN NOT NULL DEFAULT FALSE,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (agent_id, tool_name),
  CONSTRAINT council_agent_tools_permission_check CHECK (permission_level IN ('READ','ANALYZE','WRITE','ADMIN'))
);

CREATE INDEX IF NOT EXISTS idx_council_agent_tools_agent ON council_agent_tools(agent_id);

CREATE TABLE IF NOT EXISTS agent_tasks (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id          UUID NOT NULL REFERENCES council_agents(id),
  requested_by      UUID,
  parent_task_id    UUID REFERENCES agent_tasks(id),
  task              TEXT NOT NULL,
  context           JSONB NOT NULL DEFAULT '{}',
  permissions       JSONB NOT NULL DEFAULT '[]',
  status            VARCHAR(20) NOT NULL DEFAULT 'queued',
  result            JSONB,
  confidence        NUMERIC(5,4),
  sources           JSONB NOT NULL DEFAULT '[]',
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  started_at        TIMESTAMPTZ,
  completed_at      TIMESTAMPTZ,
  CONSTRAINT agent_tasks_status_check CHECK (status IN ('queued','running','completed','failed','cancelled')),
  CONSTRAINT agent_tasks_confidence_check CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1))
);

CREATE INDEX IF NOT EXISTS idx_agent_tasks_agent ON agent_tasks(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_parent ON agent_tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_created ON agent_tasks(created_at);
