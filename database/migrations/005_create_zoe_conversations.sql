-- Migration: 005_create_zoe_conversations.sql
-- Zoë AI Platform V1.0 – Conversations and messages

CREATE TABLE IF NOT EXISTS zoe_conversations (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id      VARCHAR(200)  NOT NULL,
  user_id         VARCHAR(200),
  title           VARCHAR(300),
  status          VARCHAR(20)   NOT NULL DEFAULT 'ACTIVE',
  context         JSONB         NOT NULL DEFAULT '{}',
  message_count   INTEGER       NOT NULL DEFAULT 0,
  started_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  last_message_at TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  closed_at       TIMESTAMPTZ,
  CONSTRAINT zoe_conversations_status_check CHECK (status IN ('ACTIVE','CLOSED','ARCHIVED'))
);

CREATE TABLE IF NOT EXISTS zoe_messages (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID          NOT NULL REFERENCES zoe_conversations(id),
  role            VARCHAR(20)   NOT NULL,
  content         TEXT          NOT NULL,
  tool_calls      JSONB,
  tool_results    JSONB,
  tokens_used     INTEGER,
  model           VARCHAR(100),
  created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  CONSTRAINT zoe_messages_role_check CHECK (role IN ('user','assistant','tool','system'))
);

CREATE INDEX IF NOT EXISTS idx_zoe_conversations_session  ON zoe_conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_zoe_conversations_user     ON zoe_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_zoe_messages_conversation  ON zoe_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_zoe_messages_created_at    ON zoe_messages(created_at);
