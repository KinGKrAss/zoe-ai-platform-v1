BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS zoe_identity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identity_version TEXT NOT NULL UNIQUE,
    codename TEXT NOT NULL,
    display_name TEXT NOT NULL,
    system_name TEXT NOT NULL,
    role_description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS zoe_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    importance SMALLINT NOT NULL DEFAULT 50 CHECK (importance BETWEEN 0 AND 100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    actor TEXT NOT NULL DEFAULT 'system',
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_zoe_memory_type ON zoe_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_created_at ON zoe_memory(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at DESC);

INSERT INTO zoe_identity (
    identity_version,
    codename,
    display_name,
    system_name,
    role_description
)
VALUES (
    'V1.0',
    'ZOE-CORE',
    'Zoë',
    'Z1 Real Estate Command Center',
    'Central AI, knowledge, analysis and coordination platform'
)
ON CONFLICT (identity_version) DO NOTHING;

COMMIT;
