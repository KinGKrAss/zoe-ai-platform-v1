import express from 'express';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { dbHealth, writeMemory } from './db.js';
import { register, login, requirePermission } from './auth.js';
import { getSystemState, run } from './zoe-core.js';
import { handleMcp } from './mcp.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const port = Number(process.env.PORT || 3000);

app.disable('x-powered-by');
app.use(express.json({ limit: '256kb' }));
app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/health', async (_req, res) => {
  let database = false;
  try { database = await dbHealth(); } catch { /* report degraded, don't crash */ }
  res.status(database ? 200 : 503).json({
    status: database ? 'ok' : 'degraded',
    system: 'Z1 Command Center',
    service: 'z1-command-center',
    version: '0.2.0',
    database,
  });
});

app.get('/api/modules', async (_req, res) => {
  const state = await getSystemState();
  res.json(state.modules);
});

app.get('/api/zoe/identity', async (_req, res) => {
  const state = await getSystemState();
  if (!state.identity) return res.status(503).json({ error: 'identity_unavailable' });
  res.json(state.identity);
});

app.post('/api/auth/register', async (req, res) => {
  try {
    res.status(201).json(await register(req.body));
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Registration failed';
    res.status(message === 'Account already exists' ? 409 : 400).json({ error: message });
  }
});

app.post('/api/auth/login', async (req, res) => {
  try {
    res.json(await login(req.body));
  } catch {
    res.status(401).json({ error: 'invalid_credentials' });
  }
});

app.post('/api/zoe/run', requirePermission('memory.read'), async (req, res) => {
  try {
    if (!String(req.body?.input || '').trim()) return res.status(400).json({ error: 'input_required' });
    res.json(await run({ input: req.body.input, principal: req.principal }));
  } catch (error) {
    res.status(500).json({ error: error instanceof Error ? error.message : 'Zoë Core failure' });
  }
});

app.get('/api/memory/search', requirePermission('memory.read'), async (req, res) => {
  try {
    const { searchMemory } = await import('./db.js');
    const rows = await searchMemory({ ownerUserId: req.principal.userId, query: String(req.query.q || ''), limit: Number(req.query.limit || 20) });
    res.json({ items: rows });
  } catch (error) {
    res.status(500).json({ error: error instanceof Error ? error.message : 'memory_search_failed' });
  }
});

app.post('/api/memory', requirePermission('memory.write'), async (req, res) => {
  try {
    const row = await writeMemory({ ...req.body, ownerUserId: req.principal.userId });
    res.status(201).json(row);
  } catch (error) {
    res.status(500).json({ error: error instanceof Error ? error.message : 'memory_write_failed' });
  }
});

app.post('/mcp', handleMcp);

app.get('/api/system/status', async (_req, res) => {
  res.json(await getSystemState());
});

app.get('*', (_req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(port, () => {
  console.log(`Z1 Command Center listening on http://localhost:${port}`);
});
