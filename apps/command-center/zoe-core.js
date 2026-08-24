import { getIdentity, searchMemory, audit } from './db.js';

const MODULES = [
  { id: 'zoe', name: 'Zoë Core', status: 'online' },
  { id: 'gaia', name: 'GAIA', status: 'standby' },
  { id: 'fortuna', name: 'FORTUNA', status: 'standby' },
  { id: 'electra', name: 'ELECTRA', status: 'standby' },
  { id: 'diplomatie', name: 'DIPLOMATIE', status: 'standby' },
  { id: 'ppt', name: 'PPT', status: 'standby' },
];

function routeIntent(input) {
  const text = String(input || '').toLowerCase();
  if (/immobil|wohnung|grundbuch|miete|objekt/.test(text)) return 'gaia';
  if (/finanz|geld|cash|konto|portfolio|aktie|token/.test(text)) return 'fortuna';
  if (/energie|strom|wind|solar|kraftwerk/.test(text)) return 'electra';
  if (/vertrag|dokument|nachlass|urkunde|recht/.test(text)) return 'diplomatie';
  if (/ppt|preußen point|token/.test(text)) return 'ppt';
  return 'zoe';
}

export async function getSystemState() {
  let identity = null;
  try { identity = await getIdentity(); } catch { /* health endpoint remains available without DB */ }
  return { system: 'Z1 Real Estate Command Center', identity, modules: MODULES };
}

export async function run({ input, principal }) {
  const intent = routeIntent(input);
  const memory = await searchMemory({ ownerUserId: principal.userId, query: input, limit: 8 });
  const identity = await getIdentity();
  const response = {
    zoe: identity?.name || 'Zoë',
    version: identity?.version || 'V1.0',
    intent,
    answer_mode: 'orchestration',
    summary: memory.length
      ? `Zoë routed the request to ${intent.toUpperCase()} and found ${memory.length} relevant memory object(s).`
      : `Zoë routed the request to ${intent.toUpperCase()}. No matching memory objects were found.`,
    memory,
    next: intent === 'zoe' ? 'Handle through Zoë Core' : `Delegate to ${intent.toUpperCase()} module`,
  };
  await audit({
    actorUserId: principal.userId,
    actor: principal.displayName,
    action: 'ANALYZE',
    targetTable: 'zoe_core',
    permissionLevel: 'ANALYZE',
    metadata: { intent, memory_count: memory.length },
  });
  return response;
}
