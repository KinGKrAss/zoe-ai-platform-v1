-- Migration: 011_create_extraction_runs_and_provenance.sql
-- Extraction Engine V2: reproducible runs and conservative provenance.

CREATE TABLE IF NOT EXISTS zoe_extraction_runs (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  extraction_version  VARCHAR(30) NOT NULL,
  source_type         VARCHAR(50) NOT NULL,
  source_ref          VARCHAR(500),
  status              VARCHAR(20) NOT NULL DEFAULT 'RUNNING',
  configuration       JSONB NOT NULL DEFAULT '{}',
  statistics          JSONB NOT NULL DEFAULT '{}',
  error_message       TEXT,
  started_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at        TIMESTAMPTZ,
  CONSTRAINT zoe_extraction_runs_status_check
    CHECK (status IN ('RUNNING','COMPLETED','FAILED','CANCELLED'))
);

CREATE TABLE IF NOT EXISTS zoe_provenance (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  extraction_run_id   UUID REFERENCES zoe_extraction_runs(id) ON DELETE SET NULL,
  candidate_id        UUID REFERENCES zoe_memory_candidates(id) ON DELETE CASCADE,
  conversation_id     UUID REFERENCES zoe_conversations(id) ON DELETE SET NULL,
  message_id          UUID REFERENCES zoe_messages(id) ON DELETE SET NULL,
  source_type         VARCHAR(50) NOT NULL,
  source_ref          VARCHAR(500),
  source_locator      JSONB NOT NULL DEFAULT '{}',
  evidence_text       TEXT,
  evidence_hash       VARCHAR(64),
  relation            VARCHAR(50) NOT NULL DEFAULT 'SUPPORTS',
  strength             NUMERIC(3,2) NOT NULL DEFAULT 1.0,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT zoe_provenance_relation_check
    CHECK (relation IN ('SUPPORTS','CONTRADICTS','CONTEXT')),
  CONSTRAINT zoe_provenance_strength_check
    CHECK (strength BETWEEN 0.0 AND 1.0)
);

CREATE INDEX IF NOT EXISTS idx_zoe_extraction_runs_status
  ON zoe_extraction_runs(status);
CREATE INDEX IF NOT EXISTS idx_zoe_extraction_runs_source
  ON zoe_extraction_runs(source_type, source_ref);
CREATE INDEX IF NOT EXISTS idx_zoe_provenance_candidate
  ON zoe_provenance(candidate_id);
CREATE INDEX IF NOT EXISTS idx_zoe_provenance_message
  ON zoe_provenance(message_id);
CREATE INDEX IF NOT EXISTS idx_zoe_provenance_run
  ON zoe_provenance(extraction_run_id);
CREATE INDEX IF NOT EXISTS idx_zoe_provenance_evidence_hash
  ON zoe_provenance(evidence_hash);

ALTER TABLE zoe_memory_candidates
  ADD COLUMN IF NOT EXISTS extraction_run_id UUID REFERENCES zoe_extraction_runs(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_zoe_memory_candidates_extraction_run
  ON zoe_memory_candidates(extraction_run_id);
