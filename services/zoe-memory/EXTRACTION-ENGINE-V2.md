# Extraction Engine V2

The V2 boundary is deliberately one-way:

`ChatGPT Export -> Importer -> Conversation/Message -> Extraction Engine -> JSONL Candidate Store -> Memory Core review/promotion`

## Guarantees

- Every emitted `MemoryCandidate` starts as `review_status="draft"`.
- The engine never creates or promotes `zoe_memory` / `MemoryEntry` records.
- Exact deduplication uses SHA-256 over normalized content.
- Near-duplicate suppression is thread-local and deterministic; embeddings are intentionally outside extraction.
- `reconstruction` requires explicit synthesis language **and** at least two related source messages.
- Reconstruction retains all underlying `SourceReference` objects, including the synthesis message.
- Extraction is versioned with `extraction_version`.

## Layout

- `services/zoe-memory/zoe_memory/extraction_engine_v2/models.py` — candidate and provenance types
- `.../engine.py` — conservative extraction and reconstruction
- `.../importer.py` — ChatGPT `conversations.json` adapter
- `.../store.py` — append-only JSONL candidate/decision store
- `tests/extraction_engine_v2/` — regression tests for the safety boundary
- `database/migrations/009_create_zoe_memory_candidates.sql` — persistence schema

The Memory Core remains the authority for review, accept/reject, promotion, and final provenance linking.
