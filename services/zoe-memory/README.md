# zoe-memory – ZOE MEMORY

The identity, long-term memory, knowledge, and conversation persistence layer.

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

## Key design principle

Memory is **never overwritten**. Every change creates an event record (CREATE → UPDATE → ARCHIVE → RESTORE → MERGE). This ensures Zoë's knowledge can always be reconstructed or rolled back.

See: [Database Design](../../docs/database/DATABASE-DESIGN-V1.0.md)
