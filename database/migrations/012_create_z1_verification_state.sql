-- Z1 Control Plane verification state registry
-- Green is a derived state: it is valid only when all required checks pass.

CREATE TABLE IF NOT EXISTS z1_verification_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_key TEXT NOT NULL,
    display_name TEXT,
    chain_id BIGINT,
    address TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('VERIFIED', 'PENDING', 'FAILED', 'BLOCKED')),
    verification_score INTEGER NOT NULL DEFAULT 0
        CHECK (verification_score BETWEEN 0 AND 100),
    last_verified_at TIMESTAMPTZ,
    next_verification_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (entity_type, entity_key)
);

CREATE TABLE IF NOT EXISTS z1_verification_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES z1_verification_entities(id) ON DELETE CASCADE,
    check_code TEXT NOT NULL,
    required BOOLEAN NOT NULL DEFAULT TRUE,
    status TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PASS', 'PENDING', 'FAIL', 'SKIPPED')),
    source TEXT,
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    checked_at TIMESTAMPTZ,
    error_code TEXT,
    error_message TEXT,
    UNIQUE (entity_id, check_code)
);

CREATE INDEX IF NOT EXISTS idx_z1_verification_status
    ON z1_verification_entities(status);
CREATE INDEX IF NOT EXISTS idx_z1_verification_address
    ON z1_verification_entities(address);
CREATE INDEX IF NOT EXISTS idx_z1_verification_checks_entity
    ON z1_verification_checks(entity_id);

CREATE OR REPLACE VIEW z1_verification_state AS
SELECT
    e.id,
    e.entity_type,
    e.entity_key,
    e.display_name,
    e.chain_id,
    e.address,
    CASE
        WHEN COUNT(c.id) FILTER (WHERE c.required) = 0 THEN 'PENDING'
        WHEN COUNT(c.id) FILTER (WHERE c.required AND c.status = 'FAIL') > 0 THEN 'FAILED'
        WHEN COUNT(c.id) FILTER (WHERE c.required AND c.status IN ('PENDING', 'SKIPPED')) > 0 THEN 'PENDING'
        WHEN COUNT(c.id) FILTER (WHERE c.required AND c.status = 'PASS')
             = COUNT(c.id) FILTER (WHERE c.required) THEN 'VERIFIED'
        ELSE 'PENDING'
    END AS derived_status,
    e.verification_score,
    e.last_verified_at,
    e.updated_at
FROM z1_verification_entities e
LEFT JOIN z1_verification_checks c ON c.entity_id = e.id
GROUP BY e.id;
