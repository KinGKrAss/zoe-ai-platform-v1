-- Migration: 008_create_audit_log.sql
-- Zoë AI Platform V1.0 – System-wide audit log

CREATE TABLE IF NOT EXISTS audit_log (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  user_id          VARCHAR(200),
  user_label       VARCHAR(200),
  actor            VARCHAR(200)  NOT NULL,
  action           VARCHAR(50)   NOT NULL,
  target_table     VARCHAR(200),
  target_record    VARCHAR(200),
  tool_used        VARCHAR(200),
  permission_level VARCHAR(20),
  changes          JSONB,
  result           VARCHAR(20)   NOT NULL,
  error_message    TEXT,
  session_id       VARCHAR(200),
  conversation_id  UUID,
  ip_address       INET,
  metadata         JSONB         NOT NULL DEFAULT '{}',
  CONSTRAINT audit_log_action_check CHECK (
    action IN ('CREATE','READ','UPDATE','DELETE','ANALYZE','GENERATE','ARCHIVE','RESTORE','PUBLISH','DEPLOY','TRANSFER')
  ),
  CONSTRAINT audit_log_result_check CHECK (result IN ('SUCCESS','FAILURE','DENIED')),
  CONSTRAINT audit_log_permission_check CHECK (
    permission_level IS NULL OR permission_level IN ('READ','ANALYZE','WRITE','ADMIN')
  )
);

CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp  ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_user       ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_actor      ON audit_log(actor);
CREATE INDEX IF NOT EXISTS idx_audit_log_action     ON audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_log_result     ON audit_log(result);
CREATE INDEX IF NOT EXISTS idx_audit_log_target     ON audit_log(target_table, target_record);
