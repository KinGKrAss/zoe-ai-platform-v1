# Zoë AI Platform – Database Design V2.0

**Version:** V2.0  
**System:** Z1 Real Estate Command Center  
**Date:** 2026-08-12  
**Status:** Implementation baseline

---

## 1. Purpose

V2 formalises the database boundary between raw conversation data, extraction evidence, reviewable memory candidates and promoted long-term Memory Core records.

The central rule is:

> **Extraction never writes directly to trusted memory.**

The pipeline is:

```text
ChatGPT / source export
        ↓
conversation / message
        ↓
extraction_run
        ↓
memory_candidate
        ↓
provenance / evidence
        ↓
draft review
        ↓
accepted candidate
        ↓
Memory Core
        ↓
versioned memory + event history + optional embeddings
```

V2 is intentionally conservative. A candidate may be extracted from a conversation without being accepted as a durable fact.

---

## 2. Design Principles

1. **Provenance first** – every extracted candidate can point back to concrete source material.
2. **Draft by default** – candidates enter the system with `review_status = 'draft'`.
3. **No silent promotion** – acceptance is an explicit boundary.
4. **Deterministic deduplication** – candidates carry a stable `dedupe_key`.
5. **Reproducible extraction** – every extraction belongs to an `extraction_run` and records its extraction version/configuration.
6. **User ownership** – durable records can be associated with a stable `z1_users.id` rather than free-form actor strings.
7. **Append-oriented history** – memory changes remain reconstructable through events.
8. **Embedding portability** – V2 stores embeddings in a provider/model-neutral JSONB representation; pgvector can be introduced later without changing the Memory Core contract.
9. **Backward compatibility** – V1 tables remain valid; V2 adds explicit relationships instead of destroying legacy fields.
10. **Auditability** – user, agent, extraction and promotion actions remain attributable.

---

## 3. Layer Model

### Layer A – Source / conversation

- `zoe_conversations`
- `zoe_messages`

These tables represent what actually entered the system. They are not inferred memory.

### Layer B – Extraction

- `zoe_extraction_runs`
- `zoe_memory_candidates`
- `zoe_memory_candidate_decisions`
- `zoe_provenance`

This layer answers: **What did the extraction engine think it found, where did it find it, and what happened during review?**

### Layer C – Memory Core

- `zoe_memory`
- `zoe_memory_events`
- `zoe_memory_embeddings`

This layer contains promoted, durable memory and its history.

### Layer D – Governance / identity

- `z1_users`
- `z1_roles`
- `z1_permissions`
- `z1_user_roles`
- `z1_role_permissions`
- `audit_log`

This layer answers: **Who is allowed to do what, and who actually did it?**

---

## 4. Candidate Contract

A `zoe_memory_candidates` record is not trusted memory.

Required semantics:

| Field | Rule |
|---|---|
| `content` | Candidate statement only; do not imply certainty not present in evidence |
| `candidate_type` | Semantic class such as `FACT`, `PREFERENCE`, `RELATIONSHIP`, `CONTEXT`, `DECISION` |
| `source_references` | Legacy-compatible source list; detailed evidence lives in `zoe_provenance` |
| `review_status` | Starts at `draft` |
| `dedupe_key` | Stable semantic/content fingerprint |
| `extraction_version` | Engine/schema version that produced the candidate |
| `extraction_run_id` | Run that produced the candidate |
| `metadata` | Non-authoritative extraction metadata |

Allowed review states:

```text
draft → reviewed → accepted
                  ↘ rejected
```

A rejected candidate must remain stored as evidence of the extraction decision; it must not be silently deleted.

---

## 5. Provenance Contract

`zoe_provenance` is the authoritative evidence bridge for extraction.

A provenance record may reference:

- an extraction run;
- a candidate;
- a conversation;
- a specific message;
- an external source reference;
- an evidence excerpt;
- a locator describing where the evidence was found.

`relation` is one of:

- `SUPPORTS`
- `CONTRADICTS`
- `CONTEXT`

`strength` is normalised to `0.0–1.0`.

The extraction engine should prefer multiple independent supporting messages over a single weak inference.

---

## 6. Conservative Reconstruction Rules

The database supports the extraction policy defined by Extraction Engine V2:

### Strong evidence

- explicit user statement;
- repeated consistent statements with retained entities/facts;
- explicit correction or confirmation;
- aggregation that compares multiple candidates.

### Weak evidence

Connector words such as `also`, `zusammengefasst`, `daher`, or similar language are not sufficient by themselves to create a durable reconstructed memory.

### Reconstruction boundary

`REKONSTRUKTION` is therefore represented as a candidate with explicit provenance and remains `draft` until reviewed/accepted.

---

## 7. Memory Core Contract

`zoe_memory` is the trusted persistence layer.

V2 adds:

- `owner_user_id` – stable ownership;
- `canonical_id` – grouping of equivalent/merged memory representations;
- `promoted_from_candidate_id` – promotion provenance;
- `dedupe_key` – semantic deduplication support;
- `review_status` – explicit trust boundary.

A promoted memory should normally retain the candidate ID that caused its promotion.

`zoe_memory_events` remains append-oriented and records state transitions. V2 additionally allows events to identify the responsible stable user and originating candidate.

---

## 8. Embedding Contract

`zoe_memory_embeddings` stores one or more representations of a memory for semantic retrieval.

Each embedding records:

- memory ID;
- embedding model;
- dimensions;
- vector payload;
- content hash;
- creation timestamp.

The JSONB payload is deliberately portable. A later migration may add a `vector(n)` column through PostgreSQL `pgvector` while retaining model/hash metadata.

Embeddings are derived artifacts. They are never the source of truth for memory content.

---

## 9. User / RBAC Contract

V1 used free-form `user_id` and `actor` strings in several tables. V2 introduces stable UUID-based identity through `z1_users`.

Roles:

- `USER`
- `AGENT`
- `ADMIN`

Initial permissions:

- `memory.read`
- `memory.write`
- `memory.review`
- `system.audit`
- `system.admin`

Legacy string actor fields remain for compatibility. New application code should prefer the UUID relationships.

---

## 10. Table Overview

| Table | V2 role |
|---|---|
| `z1_users` | Stable user/service identity |
| `z1_roles` | RBAC roles |
| `z1_permissions` | Atomic permissions |
| `z1_user_roles` | User → role assignment |
| `z1_role_permissions` | Role → permission assignment |
| `zoe_conversations` | Conversation container |
| `zoe_messages` | Immutable-ish source messages |
| `zoe_extraction_runs` | Reproducible extraction execution |
| `zoe_memory_candidates` | Untrusted extracted candidates |
| `zoe_memory_candidate_decisions` | Candidate review history |
| `zoe_provenance` | Evidence/source links |
| `zoe_memory` | Trusted long-term memory |
| `zoe_memory_events` | Memory state history |
| `zoe_memory_embeddings` | Retrieval representations |
| `zoe_knowledge_objects` / `ai_knowledge_objects` | Structured factual knowledge; naming harmonisation remains a follow-up |
| `zoe_decisions` | Significant decisions |
| `zoe_preferences` | Scoped preferences |
| `audit_log` | System-wide audit trail |

---

## 11. Migration Sequence

V1 remains migrations `001–008`.

Extraction Engine V2 introduced migration `009` and the database V2 hardening continues with:

```text
database/migrations/
├── 001_create_zoe_identity.sql
├── 002_create_zoe_memory.sql
├── 003_create_zoe_memory_events.sql
├── 004_create_ai_knowledge_objects.sql
├── 005_create_zoe_conversations.sql
├── 006_create_zoe_decisions.sql
├── 007_create_zoe_preferences.sql
├── 008_create_audit_log.sql
├── 009_create_zoe_memory_candidates.sql
├── 010_create_z1_users_and_roles.sql
├── 011_create_extraction_runs_and_provenance.sql
├── 012_create_memory_core_v2.sql
└── 013_harden_v2_relationships.sql
```

The migrations are additive. Existing V1 data can remain in place while application services progressively adopt V2 relationships.

---

## 12. Promotion Transaction

Promotion from candidate to trusted memory should be performed atomically by the Memory Core service:

```text
BEGIN
  lock candidate
  verify review_status = 'accepted'
  verify provenance exists
  verify dedupe policy
  create/update memory
  create MEMORY event
  link promoted_from_candidate_id
  optionally generate embedding
  write audit record
COMMIT
```

If any mandatory step fails, no trusted memory record should be committed.

---

## 13. Non-Goals

V2 does not yet define:

- application authentication tokens;
- OAuth/session storage;
- a specific embedding provider;
- pgvector as a mandatory dependency;
- Z1 real-estate domain tables;
- automated candidate acceptance without review policy;
- legal conclusions from extracted text.

Those concerns belong to subsequent service/domain migrations.

---

## 14. Acceptance Criteria

The V2 database foundation is considered complete when:

- every extraction run is reproducible and identifiable;
- candidates default to `draft`;
- candidate evidence can be traced to source messages;
- deduplication is deterministic;
- accepted candidates can be linked to trusted memory;
- memory history remains reconstructable;
- durable memory can be user-scoped;
- semantic embeddings are stored as derived artifacts;
- RBAC has stable UUID relationships;
- audit records can identify a stable actor;
- V1 records remain readable;
- the application can implement the pipeline without inventing additional persistence semantics.

---

*Zoë AI Platform – Database Design V2.0*  
*Z1 Real Estate Command Center*  
*© 2026*
