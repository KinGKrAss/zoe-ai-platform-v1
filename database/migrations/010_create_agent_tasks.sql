-- Migration: 010_create_agent_tasks.sql
-- Zoë AI Platform V1.0 – Goddess task dispatch log

DO $$ BEGIN
  CREATE TYPE agent_task_status AS ENUM ('PENDING','RUNNING','COMPLETE','FAILED');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS agent_tasks (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  goddess_id    UUID          NOT NULL REFERENCES goddesses(id),
  requested_by  VARCHAR(200)  NOT NULL,
  task          TEXT          NOT NULL,
  context       JSONB         NOT NULL DEFAULT '{}',
  parameters    JSONB         NOT NULL DEFAULT '{}',
  status        agent_task_status NOT NULL DEFAULT 'PENDING',
  result        JSONB,
  confidence    NUMERIC(3,2),
  sources       TEXT[]        NOT NULL DEFAULT '{}',
  session_id    VARCHAR(200),
  conversation_id UUID        REFERENCES zoe_conversations(id),
  created_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  completed_at  TIMESTAMPTZ,
  CONSTRAINT agent_tasks_confidence_check CHECK (
    confidence IS NULL OR confidence BETWEEN 0.0 AND 1.0
  )
);

CREATE INDEX IF NOT EXISTS idx_agent_tasks_goddess_id ON agent_tasks(goddess_id);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_status     ON agent_tasks(status);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_created_at ON agent_tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_session_id ON agent_tasks(session_id);
