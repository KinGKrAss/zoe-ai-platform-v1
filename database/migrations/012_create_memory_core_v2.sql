-- Migration: 012_create_memory_core_v2.sql
-- Memory Core V2: ownership, promotion links, deterministic versioning and embeddings.

ALTER TABLE zoe_memory
  ADD COLUMN IF NOT EXISTS owner_user_id UUID REFERENCES z1_users(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS canonical_id UUID,
  ADD COLUMN IF NOT EXISTS promoted_from_candidate_id UUID REFERENCES zoe_memory_candidates(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS dedupe_key VARCHAR(64),
  ADD COLUMN IF NOT EXISTS review_status VARCHAR(20) NOT NULL DEFAULT 'accepted';

ALTER TABLE zoe_memory
  ADD CONSTRAINT zoe_memory_review_status_check
  CHECK (review_status IN ('accepted','archived'));

CREATE TABLE IF NOT EXISTS zoe_memory_embeddings (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  memory_id           UUID NOT NULL REFERENCES zoe_memory(id) ON DELETE CASCADE,
  embedding_model     VARCHAR(200) NOT NULL,
  dimensions          INTEGER NOT NULL,
  embedding           JSONB NOT NULL,
  content_hash        VARCHAR(64) NOT NULL,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (memory_id, embedding_model, content_hash),
  CONSTRAINT zoe_memory_embeddings_dimensions_check CHECK (dimensions > 0)
);

CREATE INDEX IF NOT EXISTS idx_zoe_memory_owner ON zoe_memory(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_canonical ON zoe_memory(canonical_id);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_candidate ON zoe_memory(promoted_from_candidate_id);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_dedupe ON zoe_memory(dedupe_key);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_review_status ON zoe_memory(review_status);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_embeddings_memory ON zoe_memory_embeddings(memory_id);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_embeddings_hash ON zoe_memory_embeddings(content_hash);

-- Portable JSONB storage is intentional for V2. A future pgvector migration can
-- materialize the same vectors without changing the Memory Core contract.

ALTER TABLE zoe_memory_events
  ADD COLUMN IF NOT EXISTS actor_user_id UUID REFERENCES z1_users(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS candidate_id UUID REFERENCES zoe_memory_candidates(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_zoe_memory_events_actor_user ON zoe_memory_events(actor_user_id);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_events_candidate ON zoe_memory_events(candidate_id);
