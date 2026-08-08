-- Migration: 002_create_zoe_memory.sql
-- Zoë AI Platform V1.0 – Long-term memory

CREATE TABLE IF NOT EXISTS zoe_memory (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  memory_key    VARCHAR(200)  NOT NULL,
  memory_type   VARCHAR(100)  NOT NULL,
  subject       VARCHAR(200),
  content       TEXT          NOT NULL,
  metadata      JSONB         NOT NULL DEFAULT '{}',
  confidence    NUMERIC(3,2)  NOT NULL DEFAULT 1.0,
  source        VARCHAR(200),
  status        VARCHAR(20)   NOT NULL DEFAULT 'ACTIVE',
  version       INTEGER       NOT NULL DEFAULT 1,
  created_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  archived_at   TIMESTAMPTZ,
  CONSTRAINT zoe_memory_status_check CHECK (status IN ('ACTIVE','ARCHIVED','MERGED')),
  CONSTRAINT zoe_memory_confidence_check CHECK (confidence BETWEEN 0.0 AND 1.0)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_zoe_memory_key_active ON zoe_memory(memory_key) WHERE status = 'ACTIVE';
CREATE INDEX IF NOT EXISTS idx_zoe_memory_type    ON zoe_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_subject ON zoe_memory(subject);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_status  ON zoe_memory(status);
