"""Read-only live gateway from Zoë MCP to the Z1 Memory Core database.

The database remains the source of truth. Authentication is deliberately
required before memory can be queried; no memory writes are exposed here.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator

import psycopg
from psycopg.rows import dict_row


class MemoryGatewayError(RuntimeError):
    pass


def _database_url() -> str:
    value = os.getenv("Z1_DATABASE_URL")
    if not value:
        raise MemoryGatewayError("Z1_DATABASE_URL is not configured")
    return value


def _owner_user_id() -> str | None:
    # In production this must be injected by the authenticated Z1 gateway,
    # never supplied by the model or an untrusted client.
    return os.getenv("Z1_MEMORY_OWNER_USER_ID") or None


@contextmanager
def connection() -> Iterator[psycopg.Connection[Any]]:
    conn = psycopg.connect(_database_url(), row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()


def search_memory(query: str, *, limit: int = 10) -> list[dict[str, Any]]:
    """Search active trusted memory by normalized textual content.

    The first live implementation uses PostgreSQL ILIKE so it works without
    requiring pgvector. Embeddings remain available for a later semantic index.
    """
    query = query.strip()
    if not query:
        raise MemoryGatewayError("query must not be empty")
    limit = max(1, min(limit, 50))
    owner = _owner_user_id()
    pattern = f"%{query}%"

    with connection() as conn:
        with conn.cursor() as cur:
            if owner:
                cur.execute(
                    """
                    SELECT id, memory_key, memory_type, subject, content,
                           metadata, confidence, source, status, version,
                           owner_user_id, canonical_id, review_status,
                           created_at, updated_at
                    FROM zoe_memory
                    WHERE status = 'ACTIVE'
                      AND review_status = 'accepted'
                      AND (owner_user_id = %s OR owner_user_id IS NULL)
                      AND (memory_key ILIKE %s OR subject ILIKE %s OR content ILIKE %s)
                    ORDER BY updated_at DESC
                    LIMIT %s
                    """,
                    (owner, pattern, pattern, pattern, limit),
                )
            else:
                cur.execute(
                    """
                    SELECT id, memory_key, memory_type, subject, content,
                           metadata, confidence, source, status, version,
                           owner_user_id, canonical_id, review_status,
                           created_at, updated_at
                    FROM zoe_memory
                    WHERE status = 'ACTIVE'
                      AND review_status = 'accepted'
                      AND (memory_key ILIKE %s OR subject ILIKE %s OR content ILIKE %s)
                    ORDER BY updated_at DESC
                    LIMIT %s
                    """,
                    (pattern, pattern, pattern, limit),
                )
            return [dict(row) for row in cur.fetchall()]


def get_memory(memory_id: str) -> dict[str, Any]:
    owner = _owner_user_id()
    with connection() as conn:
        with conn.cursor() as cur:
            if owner:
                cur.execute(
                    """
                    SELECT id, memory_key, memory_type, subject, content,
                           metadata, confidence, source, status, version,
                           owner_user_id, canonical_id, review_status,
                           created_at, updated_at
                    FROM zoe_memory
                    WHERE id = %s AND status = 'ACTIVE'
                      AND review_status = 'accepted'
                      AND (owner_user_id = %s OR owner_user_id IS NULL)
                    """,
                    (memory_id, owner),
                )
            else:
                cur.execute(
                    """
                    SELECT id, memory_key, memory_type, subject, content,
                           metadata, confidence, source, status, version,
                           owner_user_id, canonical_id, review_status,
                           created_at, updated_at
                    FROM zoe_memory
                    WHERE id = %s AND status = 'ACTIVE'
                      AND review_status = 'accepted'
                    """,
                    (memory_id,),
                )
            row = cur.fetchone()
            if row is None:
                raise MemoryGatewayError("memory not found")
            return dict(row)
