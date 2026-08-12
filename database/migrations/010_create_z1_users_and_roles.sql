-- Migration: 010_create_z1_users_and_roles.sql
-- Z1 Database V2 foundation: stable user identity and RBAC.

CREATE TABLE IF NOT EXISTS z1_users (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  external_key    VARCHAR(200) UNIQUE,
  display_name    VARCHAR(200) NOT NULL,
  email           VARCHAR(320),
  status          VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
  metadata        JSONB NOT NULL DEFAULT '{}',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT z1_users_status_check CHECK (status IN ('ACTIVE','DISABLED','ARCHIVED'))
);

CREATE TABLE IF NOT EXISTS z1_roles (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role_key        VARCHAR(100) NOT NULL UNIQUE,
  description     TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS z1_permissions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  permission_key  VARCHAR(150) NOT NULL UNIQUE,
  description     TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS z1_user_roles (
  user_id         UUID NOT NULL REFERENCES z1_users(id) ON DELETE CASCADE,
  role_id         UUID NOT NULL REFERENCES z1_roles(id) ON DELETE CASCADE,
  granted_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS z1_role_permissions (
  role_id         UUID NOT NULL REFERENCES z1_roles(id) ON DELETE CASCADE,
  permission_id   UUID NOT NULL REFERENCES z1_permissions(id) ON DELETE CASCADE,
  granted_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (role_id, permission_id)
);

CREATE INDEX IF NOT EXISTS idx_z1_users_status ON z1_users(status);
CREATE INDEX IF NOT EXISTS idx_z1_users_email ON z1_users(email);
CREATE INDEX IF NOT EXISTS idx_z1_user_roles_role ON z1_user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_z1_role_permissions_permission ON z1_role_permissions(permission_id);

INSERT INTO z1_roles (role_key, description) VALUES
  ('USER', 'Standard Z1 user'),
  ('AGENT', 'AI agent/service identity'),
  ('ADMIN', 'System administrator')
ON CONFLICT (role_key) DO NOTHING;

INSERT INTO z1_permissions (permission_key, description) VALUES
  ('memory.read', 'Read memory and candidates'),
  ('memory.write', 'Create or promote memory'),
  ('memory.review', 'Review memory candidates'),
  ('system.audit', 'Read system audit records'),
  ('system.admin', 'Perform administrative operations')
ON CONFLICT (permission_key) DO NOTHING;
