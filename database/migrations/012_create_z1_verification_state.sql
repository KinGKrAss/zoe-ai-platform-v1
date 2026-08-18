-- Z1 Control Plane: authoritative verification state for assets and blockchain addresses.
-- Green is derived from completed required checks; UI must never write status directly.

CREATE TABLE IF NOT EXISTS z1_verification_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_key TEXT NOT NULL,
    chain_id BIGINT,
    address TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING',
    reason TEXT,
    verified_at TIMESTAMPTZ,
    last_checked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT z1_verification_entities_status_ck
      CHECK (status IN ('VERIFIED','PENDING','INVALID','BLOCKED')),
    CONSTRAINT z1_verification_entities_unique_key
      UNIQUE (entity_type, entity_key)
);

CREATE TABLE IF NOT EXISTS z1_verification_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES z1_verification_entities(id) ON DELETE CASCADE,
    check_code TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (entity_id, check_code)
);

CREATE INDEX IF NOT EXISTS idx_z1_verification_entities_status
  ON z1_verification_entities(status);
CREATE INDEX IF NOT EXISTS idx_z1_verification_entities_address
  ON z1_verification_entities(address);
CREATE INDEX IF NOT EXISTS idx_z1_verification_checks_entity
  ON z1_verification_checks(entity_id);

COMMENT ON TABLE z1_verification_entities IS
  'Authoritative Z1 verification state. VERIFIED is the source of truth for green UI state.';
COMMENT ON TABLE z1_verification_checks IS
  'Evidence-bearing verification checks used to derive entity status.';
