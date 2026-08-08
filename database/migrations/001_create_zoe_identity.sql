-- Migration: 001_create_zoe_identity.sql
-- Zoë AI Platform V1.0 – ZOE MEMORY layer

CREATE TABLE IF NOT EXISTS zoe_identity (
  id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  version                  VARCHAR(20)   NOT NULL,
  name                     VARCHAR(100)  NOT NULL,
  designation              VARCHAR(200),
  system_name              VARCHAR(200)  NOT NULL,
  primary_role             TEXT          NOT NULL,
  functions                JSONB         NOT NULL DEFAULT '[]',
  values                   JSONB         NOT NULL DEFAULT '[]',
  communication_principles JSONB         NOT NULL DEFAULT '[]',
  network                  VARCHAR(200),
  status                   VARCHAR(20)   NOT NULL DEFAULT 'ACTIVE',
  valid_from               TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  valid_to                 TIMESTAMPTZ,
  created_at               TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  created_by               VARCHAR(100)  NOT NULL DEFAULT 'system',
  notes                    TEXT,
  CONSTRAINT zoe_identity_status_check CHECK (status IN ('ACTIVE','ARCHIVED','DRAFT'))
);

CREATE INDEX IF NOT EXISTS idx_zoe_identity_status  ON zoe_identity(status);
CREATE INDEX IF NOT EXISTS idx_zoe_identity_version ON zoe_identity(version);
