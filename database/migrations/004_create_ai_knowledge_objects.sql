-- Migration: 004_create_ai_knowledge_objects.sql
-- Zoë AI Platform V1.0 – Knowledge objects

CREATE TABLE IF NOT EXISTS ai_knowledge_objects (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  object_type     VARCHAR(100)  NOT NULL,
  title           VARCHAR(300)  NOT NULL,
  content         TEXT          NOT NULL,
  structured_data JSONB         NOT NULL DEFAULT '{}',
  source_type     VARCHAR(100),
  source_id       VARCHAR(200),
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

CREATE INDEX IF NOT EXISTS idx_ai_knowledge_objects_type   ON ai_knowledge_objects(object_type);
CREATE INDEX IF NOT EXISTS idx_ai_knowledge_objects_tags   ON ai_knowledge_objects USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_ai_knowledge_objects_data   ON ai_knowledge_objects USING GIN(structured_data);
CREATE INDEX IF NOT EXISTS idx_ai_knowledge_objects_status ON ai_knowledge_objects(status);
