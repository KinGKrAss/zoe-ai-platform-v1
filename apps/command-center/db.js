import pg from 'pg';

const { Pool } = pg;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://zoe:zoe_dev_password@127.0.0.1:5432/zoe',
  max: Number(process.env.PGPOOL_MAX || 10),
  idleTimeoutMillis: 30000,
});

export async function dbHealth() {
  const result = await pool.query('SELECT 1 AS ok');
  return result.rows[0]?.ok === 1;
}

export async function getIdentity() {
  const { rows } = await pool.query(
    `SELECT version, name, designation, system_name, primary_role, functions, values,
            communication_principles, network, status, valid_from
       FROM zoe_identity
      WHERE status = 'ACTIVE'
      ORDER BY valid_from DESC
      LIMIT 1`,
  );
  return rows[0] || null;
}

export async function searchMemory({ ownerUserId, query, limit = 20 }) {
  const values = [ownerUserId || null, `%${query}%`, Math.min(Math.max(limit, 1), 50)];
  const { rows } = await pool.query(
    `SELECT id, memory_key, memory_type, subject, content, metadata, confidence,
            source, status, version, created_at, updated_at
       FROM zoe_memory
      WHERE status = 'ACTIVE'
        AND ($1::uuid IS NULL OR owner_user_id = $1::uuid OR owner_user_id IS NULL)
        AND (content ILIKE $2 OR COALESCE(subject, '') ILIKE $2 OR memory_key ILIKE $2)
      ORDER BY confidence DESC, updated_at DESC
      LIMIT $3`,
    values,
  );
  return rows;
}

export async function writeMemory({ ownerUserId, memoryKey, memoryType, subject, content, confidence = 1, source, metadata = {} }) {
  const { rows } = await pool.query(
    `INSERT INTO zoe_memory
       (memory_key, memory_type, subject, content, metadata, confidence, source, owner_user_id)
     VALUES ($1,$2,$3,$4,$5::jsonb,$6,$7,$8)
     ON CONFLICT (memory_key) WHERE status = 'ACTIVE'
     DO UPDATE SET content = EXCLUDED.content,
                   metadata = EXCLUDED.metadata,
                   confidence = EXCLUDED.confidence,
                   source = EXCLUDED.source,
                   owner_user_id = EXCLUDED.owner_user_id,
                   version = zoe_memory.version + 1,
                   updated_at = NOW()
     RETURNING id, memory_key, memory_type, subject, content, metadata, confidence, source, status, version, created_at, updated_at`,
    [memoryKey, memoryType, subject || null, content, JSON.stringify(metadata), confidence, source || null, ownerUserId || null],
  );
  return rows[0];
}

export async function getUserByEmail(email) {
  const { rows } = await pool.query(
    `SELECT id, display_name, email, password_hash, status
       FROM z1_users WHERE LOWER(email) = LOWER($1) LIMIT 1`,
    [email],
  );
  return rows[0] || null;
}

export async function createUser({ displayName, email, passwordHash }) {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const { rows } = await client.query(
      `INSERT INTO z1_users (display_name, email, password_hash)
       VALUES ($1,$2,$3)
       RETURNING id, display_name, email, status`,
      [displayName, email, passwordHash],
    );
    await client.query(
      `INSERT INTO z1_user_roles (user_id, role_id)
       SELECT $1, id FROM z1_roles WHERE role_key = 'USER'
       ON CONFLICT DO NOTHING`,
      [rows[0].id],
    );
    await client.query('COMMIT');
    return rows[0];
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

export async function getUserPermissions(userId) {
  const { rows } = await pool.query(
    `SELECT DISTINCT p.permission_key
       FROM z1_user_roles ur
       JOIN z1_role_permissions rp ON rp.role_id = ur.role_id
       JOIN z1_permissions p ON p.id = rp.permission_id
      WHERE ur.user_id = $1`,
    [userId],
  );
  return rows.map((row) => row.permission_key);
}

export async function touchLogin(userId) {
  await pool.query('UPDATE z1_users SET last_login_at = NOW(), updated_at = NOW() WHERE id = $1', [userId]);
}

export async function audit({ actorUserId = null, actor = 'system', action, targetTable, targetRecord = null, permissionLevel = null, result = 'SUCCESS', metadata = {} }) {
  await pool.query(
    `INSERT INTO audit_log
       (user_id, user_label, actor, action, target_table, target_record, permission_level, result, metadata, actor_user_id)
     VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9::jsonb,$1)`,
    [actorUserId, actor, actor, action, targetTable, targetRecord, permissionLevel, result, JSON.stringify(metadata)],
  );
}

export async function closeDb() {
  await pool.end();
}
