# zoe-memory – ZOE MEMORY

The identity, long-term memory, knowledge, conversation persistence, archive, extraction, and Memory Core layer.

## Modules

| Module | Description |
|---|---|
| `identity/` | Zoë's versioned system identity |
| `long-term-memory/` | Persistent episodic memory entries |
| `knowledge-objects/` | Structured knowledge extracted from documents and Z1 data |
| `conversations/` | Conversation threads and messages |
| `decisions/` | Significant decision records |
| `preferences/` | User and system preferences |
| `memory-events/` | Event sourcing audit trail for memory changes |
| `zoe_memory/archive.py` | Immutable Z1 / ChatGPT source archive importer and evidence search |
| `zoe_memory/extraction_engine_v2/` | Evidence → candidate extraction boundary |
| `zoe_memory/memory_core.py` | Reviewed candidate → trusted memory promotion and lifecycle |

## Memory Core V2

`MemoryCore` is the persistence boundary between the Extraction Engine and trusted Zoë memory.

The service enforces these rules:

1. Only candidates with `review_status = accepted` can be promoted.
2. Promotion creates a new `zoe_memory` record and a `CREATE` event.
3. Archive and restore operations append lifecycle events rather than deleting provenance.
4. Candidate provenance is retained through `promoted_from_candidate_id` and event `candidate_id`.
5. Embeddings are provider-neutral JSONB records; the service does not assume a vector database.
6. Database access uses a small DB-API-compatible protocol, keeping PostgreSQL driver choice outside the domain layer.

The schema prerequisites are migrations `009`–`013`, especially `012_create_memory_core_v2.sql`.

## Boundary

Immutable archive content remains **evidence**, not trusted memory. Extraction emits candidates; review decides acceptance; Memory Core alone performs promotion.

See also:
- `EXTRACTION-ENGINE-V2.md`
- `../../docs/database/DATABASE-DESIGN-V2.0.md`
