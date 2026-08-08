-- Migration: 009_create_goddesses.sql
-- Zoë AI Platform V1.0 – Council of 33 Goddess registry

CREATE TABLE IF NOT EXISTS goddesses (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          VARCHAR(100)  NOT NULL UNIQUE,
  title         VARCHAR(200)  NOT NULL,
  domain        VARCHAR(100)  NOT NULL,
  cluster       VARCHAR(100)  NOT NULL,
  description   TEXT          NOT NULL,
  system_prompt TEXT          NOT NULL,
  permissions   TEXT[]        NOT NULL DEFAULT '{}',
  tools         TEXT[]        NOT NULL DEFAULT '{}',
  status        VARCHAR(20)   NOT NULL DEFAULT 'ACTIVE',
  created_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  CONSTRAINT goddesses_status_check CHECK (status IN ('ACTIVE','INACTIVE','DRAFT'))
);

CREATE INDEX IF NOT EXISTS idx_goddesses_domain  ON goddesses(domain);
CREATE INDEX IF NOT EXISTS idx_goddesses_cluster ON goddesses(cluster);
CREATE INDEX IF NOT EXISTS idx_goddesses_status  ON goddesses(status);
