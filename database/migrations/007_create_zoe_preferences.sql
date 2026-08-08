-- Migration: 007_create_zoe_preferences.sql
-- Zoë AI Platform V1.0 – User and system preferences

CREATE TABLE IF NOT EXISTS zoe_preferences (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scope            VARCHAR(20)   NOT NULL,
  scope_id         VARCHAR(200),
  preference_key   VARCHAR(200)  NOT NULL,
  preference_value JSONB         NOT NULL,
  description      TEXT,
  created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  CONSTRAINT zoe_preferences_scope_check CHECK (scope IN ('USER','SYSTEM','AGENT')),
  UNIQUE (scope, scope_id, preference_key)
);

CREATE INDEX IF NOT EXISTS idx_zoe_preferences_scope ON zoe_preferences(scope, scope_id);
