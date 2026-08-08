-- Migration: 006_create_zoe_decisions.sql
-- Zoë AI Platform V1.0 – Decision records

CREATE TABLE IF NOT EXISTS zoe_decisions (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  decision_type    VARCHAR(100)  NOT NULL,
  title            VARCHAR(300)  NOT NULL,
  description      TEXT          NOT NULL,
  rationale        TEXT,
  alternatives     JSONB         NOT NULL DEFAULT '[]',
  outcome          VARCHAR(100),
  related_entities JSONB         NOT NULL DEFAULT '[]',
  conversation_id  UUID          REFERENCES zoe_conversations(id),
  decided_by       VARCHAR(200),
  decided_at       TIMESTAMPTZ,
  created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  CONSTRAINT zoe_decisions_outcome_check CHECK (
    outcome IS NULL OR outcome IN ('ACCEPTED','REJECTED','PENDING','IMPLEMENTED')
  )
);

CREATE INDEX IF NOT EXISTS idx_zoe_decisions_type    ON zoe_decisions(decision_type);
CREATE INDEX IF NOT EXISTS idx_zoe_decisions_outcome ON zoe_decisions(outcome);
