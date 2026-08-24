import crypto from 'node:crypto';
import { SignJWT, jwtVerify } from 'jose';
import { createUser, getUserByEmail, getUserPermissions, touchLogin } from './db.js';

const secret = process.env.Z1_JWT_SECRET;
if (!secret && process.env.NODE_ENV === 'production') {
  throw new Error('Z1_JWT_SECRET must be configured in production');
}
const jwtSecret = new TextEncoder().encode(secret || 'development-only-z1-secret-change-me');

function normalizeEmail(email) {
  return String(email || '').trim().toLowerCase();
}

function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync(password, salt, 64).toString('hex');
  return `scrypt$${salt}$${hash}`;
}

function verifyPassword(password, encoded) {
  const [scheme, salt, expected] = String(encoded || '').split('$');
  if (scheme !== 'scrypt' || !salt || !expected) return false;
  const actual = crypto.scryptSync(password, salt, 64).toString('hex');
  return crypto.timingSafeEqual(Buffer.from(actual, 'hex'), Buffer.from(expected, 'hex'));
}

async function issueToken(user, permissions) {
  return new SignJWT({
    sub: user.id,
    name: user.display_name,
    permissions,
  })
    .setProtectedHeader({ alg: 'HS256', typ: 'JWT' })
    .setIssuedAt()
    .setExpirationTime(process.env.Z1_JWT_TTL || '8h')
    .sign(jwtSecret);
}

export async function register({ displayName, email, password }) {
  if (!displayName || !normalizeEmail(email) || typeof password !== 'string' || password.length < 12) {
    throw new Error('displayName, email and a password of at least 12 characters are required');
  }
  const normalized = normalizeEmail(email);
  if (await getUserByEmail(normalized)) throw new Error('Account already exists');
  const user = await createUser({ displayName: displayName.trim(), email: normalized, passwordHash: hashPassword(password) });
  const permissions = await getUserPermissions(user.id);
  return { user, token: await issueToken(user, permissions) };
}

export async function login({ email, password }) {
  const user = await getUserByEmail(normalizeEmail(email));
  if (!user || user.status !== 'ACTIVE' || !verifyPassword(password, user.password_hash)) {
    throw new Error('Invalid credentials');
  }
  await touchLogin(user.id);
  const permissions = await getUserPermissions(user.id);
  return {
    user: { id: user.id, display_name: user.display_name, email: user.email, status: user.status },
    token: await issueToken(user, permissions),
  };
}

export async function authenticate(req) {
  const header = req.headers.authorization || '';
  if (!header.startsWith('Bearer ')) return null;
  try {
    const { payload } = await jwtVerify(header.slice(7), jwtSecret, { algorithms: ['HS256'] });
    return {
      userId: String(payload.sub),
      displayName: String(payload.name || 'Z1 user'),
      permissions: Array.isArray(payload.permissions) ? payload.permissions.map(String) : [],
    };
  } catch {
    return null;
  }
}

export function requirePermission(permission) {
  return async (req, res, next) => {
    const principal = await authenticate(req);
    if (!principal) return res.status(401).json({ error: 'authentication_required' });
    if (!principal.permissions.includes(permission) && !principal.permissions.includes('system.admin')) {
      return res.status(403).json({ error: 'permission_denied', required: permission });
    }
    req.principal = principal;
    next();
  };
}

export { hashPassword };
