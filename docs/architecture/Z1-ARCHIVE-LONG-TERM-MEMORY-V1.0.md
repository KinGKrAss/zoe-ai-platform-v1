# Z1 Archive + Long-Term Memory Access V1.0

**Status:** Implementation baseline  
**Date:** 2026-08-12

## Purpose

Z1 must be able to revisit archived source conversations instead of depending only on already-promoted Memory Core entries.

The archive is therefore a persistent evidence layer between source exports and extraction.

```text
ChatGPT export / external source
        ↓
Z1 Archive Store
        ↓
retrieval / search
        ↓
Extraction Engine V2
        ↓
Candidate + provenance
        ↓
review
        ↓
Memory Core
```

## Core rule

**Archive is evidence, not truth.**

An archived sentence may be retrieved and cited as source material, but it does not become a trusted memory merely because it exists in the archive.

## Implemented components

- `database/migrations/014_create_z1_archive_store.sql`
  - `z1_archive_sources`: immutable source registry
  - `z1_archive_items`: immutable source text and source locators
  - SHA-256 hashes for source and message content
  - PostgreSQL full-text search index
- `services/zoe-memory/zoe_memory/archive.py`
  - ChatGPT `conversations.json` import
  - source identity preservation
  - idempotent import
  - archive search
- `services/zoe-memory/tests/test_archive.py`
  - hash stability
  - ChatGPT source/conversation/message identity preservation

## Why this is different from `zoe_memory`

`zoe_memory` is trusted, promoted long-term memory. `z1_archive_items` is the retained source record from which extraction can be rerun, contradictions can be checked, and older context can be recovered.

This distinction prevents historical text from being silently converted into fact.

## Retrieval contract

A retrieval result contains:

- archive item ID;
- source ID;
- conversation reference;
- message reference;
- role;
- original content;
- source locator;
- original source timestamp when available.

The result can then be passed to Extraction Engine V2 as provenance-bearing evidence.

## Deduplication

- Source archives are deduplicated by `(source_type, source_hash)`.
- Archive items are deduplicated by source, content hash and message reference.
- Re-importing the same export therefore does not create a second copy of the same source evidence.

## Integrity

The archive is append-oriented. The application API exposes import and search, not update/delete operations for archived source text. Any correction or interpretation belongs in the candidate/review/memory layers and retains provenance back to the archive.

## Required next integration

The Memory/Extraction orchestrator should accept archive search results as source input and create `zoe_extraction_runs` plus `zoe_provenance` records before candidate creation.
