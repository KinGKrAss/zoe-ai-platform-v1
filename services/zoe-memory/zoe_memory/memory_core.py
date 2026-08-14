from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from typing import Any, Protocol, Sequence


class CursorLike(Protocol):
    def execute(self, operation: str, params: Sequence[Any] = ...) -> Any: ...
    def fetchone(self) -> Any: ...
    def fetchall(self) -> list[Any]: ...


class ConnectionLike(Protocol):
    def cursor(self) -> CursorLike: ...
    def commit(self) -> Any: ...
    def rollback(self) -> Any: ...


@dataclass(frozen=True)
class MemoryEntry:
    id: str
    memory_key: str
    memory_type: str
    subject: str | None
    content: str
    metadata: dict[str, Any]
    confidence: float
    source: str | None
    status: str
    version: int
    owner_user_id: str | None
    canonical_id: str | None
    promoted_from_candidate_id: str | None
    dedupe_key: str | None
    review_status: str


class MemoryCore:
    """Persistence boundary between reviewed candidates and trusted memory.

    Candidates are evidence. Only an explicitly accepted candidate may be
    promoted. Every lifecycle transition writes an append-only memory event.
    """

    def __init__(self, connection: ConnectionLike) -> None:
        self.connection = connection

    @staticmethod
    def dedupe_key(content: str) -> str:
        normalized = " ".join(content.strip().casefold().split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def promote_candidate(
        self,
        candidate_id: str,
        *,
        memory_key: str,
        memory_type: str = "episodic",
        subject: str | None = None,
        owner_user_id: str | None = None,
        actor: str = "zoe-memory-core",
        session_id: str | None = None,
        source: str | None = "extraction-engine-v2",
    ) -> MemoryEntry:
        """Promote one accepted candidate into active Memory Core state."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                SELECT id, content, candidate_type, source_references, metadata,
                       review_status, dedupe_key
                FROM zoe_memory_candidates
                WHERE id = %s
                FOR UPDATE
                """,
                (candidate_id,),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"memory candidate not found: {candidate_id}")
            if row[5] != "accepted":
                raise ValueError(
                    f"candidate {candidate_id} is not accepted; current status={row[5]}"
                )

            content = str(row[1])
            dedupe_key = str(row[6] or self.dedupe_key(content))
            memory_id = str(uuid.uuid4())
            canonical_id = memory_id
            metadata = row[4] if isinstance(row[4], dict) else {}

            cursor.execute(
                """
                SELECT id FROM zoe_memory
                WHERE memory_key = %s AND status = 'ACTIVE'
                LIMIT 1
                """,
                (memory_key,),
            )
            existing = cursor.fetchone()
            if existing is not None:
                raise ValueError(f"active memory_key already exists: {memory_key}")

            cursor.execute(
                """
                INSERT INTO zoe_memory
                    (id, memory_key, memory_type, subject, content, metadata,
                     confidence, source, status, version, owner_user_id,
                     canonical_id, promoted_from_candidate_id, dedupe_key, review_status)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, 1.0, %s, 'ACTIVE', 1,
                        %s, %s, %s, %s, 'accepted')
                """,
                (
                    memory_id,
                    memory_key,
                    memory_type,
                    subject,
                    content,
                    json.dumps(metadata),
                    source,
                    owner_user_id,
                    canonical_id,
                    candidate_id,
                    dedupe_key,
                ),
            )
            cursor.execute(
                """
                INSERT INTO zoe_memory_events
                    (memory_id, event_type, previous_content, new_content,
                     previous_metadata, new_metadata, reason, actor, session_id,
                     actor_user_id, candidate_id)
                VALUES (%s, 'CREATE', NULL, %s, NULL, %s::jsonb,
                        'promote accepted memory candidate', %s, %s, %s, %s)
                """,
                (
                    memory_id,
                    content,
                    json.dumps(metadata),
                    actor,
                    session_id,
                    owner_user_id,
                    candidate_id,
                ),
            )
            self.connection.commit()
            return self.get(memory_id)
        except Exception:
            self.connection.rollback()
            raise

    def archive(
        self,
        memory_id: str,
        *,
        reason: str,
        actor: str = "zoe-memory-core",
        session_id: str | None = None,
        actor_user_id: str | None = None,
    ) -> MemoryEntry:
        """Archive memory without deleting its historical event trail."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                SELECT content, metadata, status FROM zoe_memory
                WHERE id = %s FOR UPDATE
                """,
                (memory_id,),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"memory not found: {memory_id}")
            if row[2] == "ARCHIVED":
                return self.get(memory_id)

            cursor.execute(
                """
                UPDATE zoe_memory
                SET status = 'ARCHIVED', review_status = 'archived',
                    archived_at = NOW(), updated_at = NOW(), version = version + 1
                WHERE id = %s
                """,
                (memory_id,),
            )
            cursor.execute(
                """
                INSERT INTO zoe_memory_events
                    (memory_id, event_type, previous_content, new_content,
                     previous_metadata, new_metadata, reason, actor, session_id,
                     actor_user_id)
                VALUES (%s, 'ARCHIVE', %s, %s, %s::jsonb, %s::jsonb,
                        %s, %s, %s, %s)
                """,
                (
                    memory_id,
                    row[0],
                    row[0],
                    json.dumps(row[1] or {}),
                    json.dumps(row[1] or {}),
                    reason,
                    actor,
                    session_id,
                    actor_user_id,
                ),
            )
            self.connection.commit()
            return self.get(memory_id)
        except Exception:
            self.connection.rollback()
            raise

    def restore(
        self,
        memory_id: str,
        *,
        reason: str,
        actor: str = "zoe-memory-core",
        session_id: str | None = None,
        actor_user_id: str | None = None,
    ) -> MemoryEntry:
        """Restore archived memory while retaining the complete event history."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                SELECT content, metadata, status FROM zoe_memory
                WHERE id = %s FOR UPDATE
                """,
                (memory_id,),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"memory not found: {memory_id}")
            if row[2] == "ACTIVE":
                return self.get(memory_id)

            cursor.execute(
                """
                UPDATE zoe_memory
                SET status = 'ACTIVE', review_status = 'accepted',
                    archived_at = NULL, updated_at = NOW(), version = version + 1
                WHERE id = %s
                """,
                (memory_id,),
            )
            cursor.execute(
                """
                INSERT INTO zoe_memory_events
                    (memory_id, event_type, previous_content, new_content,
                     previous_metadata, new_metadata, reason, actor, session_id,
                     actor_user_id)
                VALUES (%s, 'RESTORE', %s, %s, %s::jsonb, %s::jsonb,
                        %s, %s, %s, %s)
                """,
                (
                    memory_id,
                    row[0],
                    row[0],
                    json.dumps(row[1] or {}),
                    json.dumps(row[1] or {}),
                    reason,
                    actor,
                    session_id,
                    actor_user_id,
                ),
            )
            self.connection.commit()
            return self.get(memory_id)
        except Exception:
            self.connection.rollback()
            raise

    def attach_embedding(
        self,
        memory_id: str,
        *,
        embedding_model: str,
        embedding: Sequence[float],
        content_hash: str,
    ) -> None:
        """Store an embedding without coupling Memory Core to a vector provider."""
        vector = [float(value) for value in embedding]
        if not vector:
            raise ValueError("embedding must not be empty")
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO zoe_memory_embeddings
                    (memory_id, embedding_model, dimensions, embedding, content_hash)
                VALUES (%s, %s, %s, %s::jsonb, %s)
                ON CONFLICT (memory_id, embedding_model, content_hash) DO NOTHING
                """,
                (
                    memory_id,
                    embedding_model,
                    len(vector),
                    json.dumps(vector),
                    content_hash,
                ),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def get(self, memory_id: str) -> MemoryEntry:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT id, memory_key, memory_type, subject, content, metadata,
                   confidence, source, status, version, owner_user_id,
                   canonical_id, promoted_from_candidate_id, dedupe_key, review_status
            FROM zoe_memory WHERE id = %s
            """,
            (memory_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise ValueError(f"memory not found: {memory_id}")
        return MemoryEntry(
            id=str(row[0]),
            memory_key=str(row[1]),
            memory_type=str(row[2]),
            subject=row[3],
            content=str(row[4]),
            metadata=row[5] or {},
            confidence=float(row[6]),
            source=row[7],
            status=str(row[8]),
            version=int(row[9]),
            owner_user_id=str(row[10]) if row[10] else None,
            canonical_id=str(row[11]) if row[11] else None,
            promoted_from_candidate_id=str(row[12]) if row[12] else None,
            dedupe_key=row[13],
            review_status=str(row[14]),
        )
