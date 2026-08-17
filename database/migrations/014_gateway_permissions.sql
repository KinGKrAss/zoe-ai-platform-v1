-- Migration: 014_gateway_permissions.sql
-- Permissions required by the authenticated Zoë Core Gateway.

INSERT INTO z1_permissions (permission_key, description) VALUES
  ('mcp.execute', 'Execute registered MCP tools'),
  ('stream.read', 'Open the authenticated realtime WebSocket stream')
ON CONFLICT (permission_key) DO NOTHING;

-- Default USER role gets read-only realtime access and MCP is deliberately
-- restricted to ADMIN/explicit grants. No implicit administrative access.
INSERT INTO z1_role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM z1_roles r
JOIN z1_permissions p ON p.permission_key = 'stream.read'
WHERE r.role_key = 'USER'
ON CONFLICT DO NOTHING;

INSERT INTO z1_role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM z1_roles r
JOIN z1_permissions p ON p.permission_key = 'mcp.execute'
WHERE r.role_key IN ('AGENT', 'ADMIN')
ON CONFLICT DO NOTHING;
