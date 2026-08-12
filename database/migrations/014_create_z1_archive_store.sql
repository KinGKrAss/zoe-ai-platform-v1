-- Migration: 014_create_z1_archive_store.sql
-- Z1 Archive Store: immutable source archive for long-term retrieval and re-processing.
--
-- The archive is NOT trusted memory. It preserves source text so later extraction,
-- contradiction checks, and memory reconstruction can revisit the original evidence.

CREATE TABLE IF NOT EXISTS z1_archive_sources (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_type       VARCHAR(50) NOT NULL, -- CHATGPT_EXPORT | DOCUMENT | API | OTHER
  source_name       VARCHAR(500) NOT NULL,
  source_hash       VARCHAR(64) NOT NULL,
  source_version    VARCHAR(50),
  imported_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  metadata          JSONB NOT NULL DEFAULT '{}',
  UNIQUE (source_type, source_hash)
);

CREATE TABLE IF NOT EXISTS z1_archive_items (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id         UUID NOT NULL REFERENCES z1_archive_sources(id) ON DELETE RESTRICT,
  external_id       VARCHAR(500),
  conversation_ref  VARCHAR(500),
  message_ref       VARCHAR(500),
  role              VARCHAR(50),
  content           TEXT NOT NULL,
  content_hash      VARCHAR(64) NOT NULL,
  source_locator    JSONB NOT NULL DEFAULT '{}',
  created_at_source TIMESTAMPTZ,
  archived_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  metadata          JSONB NOT NULL DEFAULT '{}',
  search_document   TSVECTOR GENERATED ALWAYS AS (
    to_tsvector('simple', coalesce(content, ''))
  ) STORED
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_z1_archive_items_identity
  ON z1_archive_items(source_id, content_hash, coalesce(message_ref, ''));

CREATE INDEX IF NOT EXISTS idx_z1_archive_items_source
  ON z1_archive_items(source_id);
CREATE INDEX IF NOT EXISTS idx_z1_archive_items_conversation
  ON z1_archive_items(conversation_ref);
CREATE INDEX IF NOT EXISTS idx_z1_archive_items_message
  ON z1_archive_items(message_ref);
CREATE INDEX IF NOT EXISTS idx_z1_archive_items_content_hash
  ON z1_archive_items(content_hash);
CREATE INDEX IF NOT EXISTS idx_z1_archive_items_search
  ON z1_archive_items USING GIN(search_document);
CREATE INDEX IF NOT EXISTS idx_z1_archive_items_created
  ON z1_archive_items(created_at_source);

COMMENT ON TABLE z1_archive_sources IS
  'Immutable registry of imported source archives. Not trusted memory.';
COMMENT ON TABLE z1_archive_items IS
  'Immutable source text retained for retrieval, evidence, re-extraction and reconstruction.';
