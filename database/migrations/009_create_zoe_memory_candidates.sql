-- Migration: 009_create_zoe_memory_candidates.sql
-- Extraction Engine V2: evidence -> candidate -> review -> promotion boundary.

CREATE TABLE IF NOT EXISTS zoe_memory_candidates (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content             TEXT NOT NULL,
  candidate_type      VARCHAR(50) NOT NULL,
  source_references   JSONB NOT NULL DEFAULT '[]',
  review_status       VARCHAR(20) NOT NULL DEFAULT 'draft',
  dedupe_key          VARCHAR(64) NOT NULL,
  extraction_version  VARCHAR(20) NOT NULL,
  metadata            JSONB NOT NULL DEFAULT '{}',
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT zoe_memory_candidates_review_status_check
    CHECK (review_status IN ('draft','reviewed','accepted','rejected'))
);

CREATE INDEX IF NOT EXISTS idx_zoe_memory_candidates_status
  ON zoe_memory_candidates(review_status);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_candidates_dedupe
  ON zoe_memory_candidates(dedupe_key);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_candidates_version
  ON zoe_memory_candidates(extraction_version);

CREATE TABLE IF NOT EXISTS zoe_memory_candidate_decisions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id    UUID NOT NULL REFERENCES zoe_memory_candidates(id) ON DELETE CASCADE,
  status          VARCHAR(20) NOT NULL,
  reason          TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT zoe_memory_candidate_decision_status_check
    CHECK (status IN ('draft','reviewed','accepted','rejected'))
);

CREATE INDEX IF NOT EXISTS idx_zoe_memory_candidate_decisions_candidate
  ON zoe_memory_candidate_decisions(candidate_id);
