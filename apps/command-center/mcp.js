import { authenticate } from './auth.js';
import { getIdentity, searchMemory, writeMemory, audit } from './db.js';

const SERVER_INFO = {
  name: 'z1-command-center',
  version: '0.2.0',
};

const TOOLS = [
  {
    name: 'z1_system_status',
    description: 'Return Z1 and Zoë identity/module status.',
    inputSchema: { type: 'object', properties: {} },
  },
  {
    name: 'z1_memory_search',
    description: 'Search the authenticated user-scoped Zoë memory.',
    inputSchema: { type: 'object', properties: { query: { type: 'string' }, limit: { type: 'integer', minimum: 1, maximum: 50 } }, required: ['query'] },
  },
  {
    name: 'z1_memory_write',
    description: 'Create or update a Zoë memory object. Requires memory.write.',
    inputSchema: {
      type: 'object',
      properties: {
        memoryKey: { type: 'string' }, memoryType: { type: 'string' }, subject: { type: 'string' },
        content: { type: 'string' }, confidence: { type: 'number', minimum: 0, maximum: 1 },
        source: { type: 'string' }, metadata: { type: 'object' },
      },
      required: ['memoryKey', 'memoryType', 'content'],
    },
  },
];

function jsonRpc(id, result) {
  return { jsonrpc: '2.0', id, result };
}
function jsonRpcError(id, code, message) {
  return { jsonrpc: '2.0', id, error: { code, message } };
}

export async function handleMcp(req, res) {
  const principal = await authenticate(req);
  if (!principal) return res.status(401).json({ error: 'authentication_required' });

  const body = req.body || {};
  const id = body.id ?? null;
  if (body.jsonrpc !== '2.0' || typeof body.method !== 'string') {
    return res.status(400).json(jsonRpcError(id, -32600, 'Invalid JSON-RPC request'));
  }

  try {
    if (body.method === 'initialize') {
      return res.json(jsonRpc(id, {
        protocolVersion: body.params?.protocolVersion || '2025-06-18',
        capabilities: { tools: {} },
        serverInfo: SERVER_INFO,
      }));
    }
    if (body.method === 'tools/list') return res.json(jsonRpc(id, { tools: TOOLS }));
    if (body.method !== 'tools/call') return res.json(jsonRpcError(id, -32601, 'Method not found'));

    const name = body.params?.name;
    const args = body.params?.arguments || {};
    if (name === 'z1_system_status') {
      const identity = await getIdentity();
      return res.json(jsonRpc(id, { content: [{ type: 'text', text: JSON.stringify({ identity, server: SERVER_INFO }) }] }));
    }
    if (name === 'z1_memory_search') {
      if (!principal.permissions.includes('memory.read') && !principal.permissions.includes('system.admin')) {
        return res.json(jsonRpcError(id, -32003, 'Permission denied: memory.read'));
      }
      const rows = await searchMemory({ ownerUserId: principal.userId, query: String(args.query || ''), limit: Number(args.limit || 20) });
      return res.json(jsonRpc(id, { content: [{ type: 'text', text: JSON.stringify(rows) }] }));
    }
    if (name === 'z1_memory_write') {
      if (!principal.permissions.includes('memory.write') && !principal.permissions.includes('system.admin')) {
        return res.json(jsonRpcError(id, -32003, 'Permission denied: memory.write'));
      }
      const row = await writeMemory({
        ownerUserId: principal.userId,
        memoryKey: args.memoryKey,
        memoryType: args.memoryType,
        subject: args.subject,
        content: args.content,
        confidence: args.confidence ?? 1,
        source: args.source,
        metadata: args.metadata || {},
      });
      await audit({ actorUserId: principal.userId, actor: principal.displayName, action: 'CREATE', targetTable: 'zoe_memory', targetRecord: row.id, permissionLevel: 'WRITE' });
      return res.json(jsonRpc(id, { content: [{ type: 'text', text: JSON.stringify(row) }] }));
    }
    return res.json(jsonRpcError(id, -32602, `Unknown tool: ${name}`));
  } catch (error) {
    return res.status(500).json(jsonRpcError(id, -32603, error instanceof Error ? error.message : 'Internal error'));
  }
}
