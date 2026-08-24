"""Read-only live access to the Z1/Zoë Memory Core PostgreSQL store."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator

import psycopg
from psycopg.rows import dict_row


class MemoryGateway:
    """Small, owner-scoped read boundary for trusted active memory."""

    def __init__(self, database_url: str | None = None, owner_user_id: str | None = None) -> None:
        self.database_url = database_url or os.getenv("Z1_MEMORY_DATABASE_URL")
        self.owner_user_id = owner_user_id or os.getenv("Z1_MEMORY_OWNER_USER_ID")

    @property
    def configured(self) -> bool:
        return bool(self.database_url and self.owner_user_id)

    @contextmanager
    def connection(self) -> Iterator[Any]:
        if not self.configured:
            raise RuntimeError("Z1 live memory is not configured")
        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            yield connection

    @staticmethod
    def _entry(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(row["id"]),
            "memory_key": row["memory_key"],
            "memory_type": row["memory_type"],
            "subject": row["subject"],
            "content": row["content"],
            "metadata": row["metadata"] or {},
            "confidence": float(row["confidence"]),
            "source": row["source"],
            "status": row["status"],
            "version": int(row["version"]),
            "owner_user_id": str(row["owner_user_id"]) if row["owner_user_id"] else None,
            "canonical_id": str(row["canonical_id"]) if row["canonical_id"] else None,
            "review_status": row["review_status"],
        }

    def search(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        query = query.strip()
        if not query:
            raise ValueError("query must not be empty")
        limit = max(1, min(int(limit), 50))
        pattern = f"%{query}%"
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, memory_key, memory_type, subject, content, metadata,
                           confidence, source, status, version, owner_user_id,
                           canonical_id, review_status
                    FROM zoe_memory
                    WHERE status = 'ACTIVE'
                      AND review_status = 'accepted'
                      AND owner_user_id = %s
                      AND (memory_key ILIKE %s OR subject ILIKE %s OR content ILIKE %s)
                    ORDER BY updated_at DESC
                    LIMIT %s
                    """,
                    (self.owner_user_id, pattern, pattern, pattern, limit),
                )
                return [self._entry(row) for row in cursor.fetchall()]

    def get(self, memory_id: str) -> dict[str, Any]:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, memory_key, memory_type, subject, content, metadata,
                           confidence, source, status, version, owner_user_id,
                           canonical_id, review_status
                    FROM zoe_memory
                    WHERE id = %s AND owner_user_id = %s
                    """,
                    (memory_id, self.owner_user_id),
                )
                row = cursor.fetchone()
                if row is None:
                    raise KeyError(f"memory not found: {memory_id}")
                return self._entry(row)
