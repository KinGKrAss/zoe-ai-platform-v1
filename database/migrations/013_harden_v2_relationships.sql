-- Migration: 013_harden_v2_relationships.sql
-- Connect V1 conversation/audit records to stable Z1 users without breaking legacy references.

ALTER TABLE zoe_conversations
  ADD COLUMN IF NOT EXISTS owner_user_id UUID REFERENCES z1_users(id) ON DELETE SET NULL;

ALTER TABLE zoe_preferences
  ADD COLUMN IF NOT EXISTS owner_user_id UUID REFERENCES z1_users(id) ON DELETE CASCADE;

ALTER TABLE zoe_decisions
  ADD COLUMN IF NOT EXISTS owner_user_id UUID REFERENCES z1_users(id) ON DELETE SET NULL;

ALTER TABLE audit_log
  ADD COLUMN IF NOT EXISTS actor_user_id UUID REFERENCES z1_users(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_zoe_conversations_owner ON zoe_conversations(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_zoe_preferences_owner ON zoe_preferences(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_zoe_decisions_owner ON zoe_decisions(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_actor_user ON audit_log(actor_user_id);

-- Candidate deduplication is scoped to extraction semantics rather than content alone.
CREATE UNIQUE INDEX IF NOT EXISTS uq_zoe_memory_candidates_dedupe_active
  ON zoe_memory_candidates(dedupe_key, extraction_version)
  WHERE review_status IN ('draft','reviewed','accepted');

-- Every provenance record must identify a usable source locator.
ALTER TABLE zoe_provenance
  ADD CONSTRAINT zoe_provenance_source_locator_nonempty
  CHECK (jsonb_typeof(source_locator) = 'object');
