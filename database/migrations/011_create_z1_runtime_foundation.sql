-- Z1 Runtime Foundation
-- P0.2: consolidate the contracts required by Z1 Core + MemoryCore + Wealth Registry.

CREATE TABLE IF NOT EXISTS z1_runtime_state (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  component VARCHAR(100) NOT NULL UNIQUE,
  status VARCHAR(30) NOT NULL DEFAULT 'INITIALIZING',
  version VARCHAR(50) NOT NULL DEFAULT '1.0.0',
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT z1_runtime_state_status_check CHECK (status IN ('INITIALIZING','READY','DEGRADED','STOPPED'))
);

ALTER TABLE zoe_memory ADD COLUMN IF NOT EXISTS owner_user_id UUID REFERENCES z1_users(id) ON DELETE SET NULL;
ALTER TABLE zoe_memory ADD COLUMN IF NOT EXISTS canonical_id VARCHAR(200);
ALTER TABLE zoe_memory ADD COLUMN IF NOT EXISTS promoted_from_candidate_id UUID REFERENCES zoe_memory_candidates(id) ON DELETE SET NULL;
ALTER TABLE zoe_memory ADD COLUMN IF NOT EXISTS embedding JSONB;
ALTER TABLE zoe_memory ADD COLUMN IF NOT EXISTS provenance JSONB NOT NULL DEFAULT '{}';
ALTER TABLE zoe_memory ADD COLUMN IF NOT EXISTS verification_status VARCHAR(30) NOT NULL DEFAULT 'UNVERIFIED';

ALTER TABLE zoe_memory ADD CONSTRAINT zoe_memory_verification_status_check
  CHECK (verification_status IN ('USER_REPORTED','UNVERIFIED','VERIFIED','DERIVED','CONFLICT'));

CREATE INDEX IF NOT EXISTS idx_zoe_memory_owner_user ON zoe_memory(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_canonical_id ON zoe_memory(canonical_id);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_verification_status ON zoe_memory(verification_status);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_promoted_candidate ON zoe_memory(promoted_from_candidate_id);

ALTER TABLE zoe_memory_candidates ADD COLUMN IF NOT EXISTS owner_user_id UUID REFERENCES z1_users(id) ON DELETE SET NULL;
ALTER TABLE zoe_memory_candidates ADD COLUMN IF NOT EXISTS provenance JSONB NOT NULL DEFAULT '{}';

CREATE INDEX IF NOT EXISTS idx_zoe_memory_candidates_owner ON zoe_memory_candidates(owner_user_id);

INSERT INTO z1_runtime_state (component, status, version)
VALUES ('z1-core', 'INITIALIZING', '1.0.0'), ('memory-core', 'INITIALIZING', '1.0.0'), ('wealth-registry', 'INITIALIZING', '1.0.0')
ON CONFLICT (component) DO NOTHING;
