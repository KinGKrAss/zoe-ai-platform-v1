-- Z1 authentication boundary. Passwords are stored only as scrypt hashes; plaintext credentials never enter the database.
ALTER TABLE z1_users
  ADD COLUMN IF NOT EXISTS password_hash TEXT,
  ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ;

CREATE UNIQUE INDEX IF NOT EXISTS idx_z1_users_email_unique
  ON z1_users (LOWER(email))
  WHERE email IS NOT NULL;

-- Default least-privilege role mappings. ADMIN is intentionally not assigned to any user automatically.
INSERT INTO z1_role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM z1_roles r
CROSS JOIN z1_permissions p
WHERE r.role_key = 'USER'
  AND p.permission_key IN ('memory.read')
ON CONFLICT DO NOTHING;

INSERT INTO z1_role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM z1_roles r
CROSS JOIN z1_permissions p
WHERE r.role_key = 'AGENT'
  AND p.permission_key IN ('memory.read','memory.write')
ON CONFLICT DO NOTHING;

INSERT INTO z1_role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM z1_roles r
CROSS JOIN z1_permissions p
WHERE r.role_key = 'ADMIN'
  AND p.permission_key IN ('memory.read','memory.write','memory.review','system.audit','system.admin')
ON CONFLICT DO NOTHING;
