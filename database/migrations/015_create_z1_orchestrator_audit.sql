-- Z1 Orchestrator, TaskRegistry and Audit Log
CREATE TABLE IF NOT EXISTS zoe_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  goal TEXT NOT NULL,
  context JSONB NOT NULL DEFAULT '{}'::jsonb,
  tools_allowed JSONB NOT NULL DEFAULT '[]'::jsonb,
  status VARCHAR(16) NOT NULL DEFAULT 'PENDING',
  actor_type VARCHAR(16) NOT NULL,
  actor_id UUID,
  request_id VARCHAR(128),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  error TEXT,
  result JSONB
);

CREATE INDEX IF NOT EXISTS idx_zoe_tasks_status ON zoe_tasks(status);
CREATE INDEX IF NOT EXISTS idx_zoe_tasks_request_id ON zoe_tasks(request_id);

CREATE TABLE IF NOT EXISTS audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  request_id VARCHAR(128),
  actor_type VARCHAR(16) NOT NULL,
  actor_id UUID,
  action VARCHAR(128) NOT NULL,
  resource VARCHAR(255) NOT NULL,
  result VARCHAR(32) NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_request_id ON audit_log(request_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_actor ON audit_log(actor_type, actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at DESC);
