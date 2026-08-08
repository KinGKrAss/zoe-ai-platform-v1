-- Migration: 003_create_zoe_memory_events.sql
-- Zoë AI Platform V1.0 – Memory event sourcing

DO $$ BEGIN
  CREATE TYPE memory_event_type AS ENUM ('CREATE','UPDATE','ARCHIVE','RESTORE','MERGE','DELETE');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS zoe_memory_events (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  memory_id         UUID          NOT NULL REFERENCES zoe_memory(id),
  event_type        memory_event_type NOT NULL,
  previous_content  TEXT,
  new_content       TEXT,
  previous_metadata JSONB,
  new_metadata      JSONB,
  reason            TEXT,
  actor             VARCHAR(200)  NOT NULL,
  session_id        VARCHAR(200),
  created_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_zoe_memory_events_memory_id  ON zoe_memory_events(memory_id);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_events_event_type ON zoe_memory_events(event_type);
CREATE INDEX IF NOT EXISTS idx_zoe_memory_events_created_at ON zoe_memory_events(created_at);
