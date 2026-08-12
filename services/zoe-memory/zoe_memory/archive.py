from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class CursorLike(Protocol):
    def execute(self, operation: str, params: tuple[Any, ...] = ...) -> Any: ...
    def fetchone(self) -> Any: ...
    def fetchall(self) -> list[Any]: ...


class ConnectionLike(Protocol):
    def cursor(self) -> CursorLike: ...
    def commit(self) -> Any: ...
    def rollback(self) -> Any: ...


@dataclass(frozen=True)
class ArchiveItem:
    id: str
    source_id: str
    conversation_ref: str | None
    message_ref: str | None
    role: str | None
    content: str
    source_locator: dict[str, Any]
    created_at_source: str | None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_chatgpt_archive(path: str | Path) -> tuple[str, list[dict[str, Any]]]:
    """Parse a ChatGPT conversations.json export without discarding source identity."""
    source_path = Path(path)
    raw = source_path.read_bytes()
    payload = json.loads(raw.decode("utf-8"))
    conversations = payload if isinstance(payload, list) else payload.get("conversations", [])
    items: list[dict[str, Any]] = []

    for conversation in conversations:
        conversation_ref = str(
            conversation.get("conversation_id")
            or conversation.get("id")
            or "unknown"
        )
        mapping = conversation.get("mapping", {})
        for message_ref, node in mapping.items():
            message = node.get("message") or {}
            content = message.get("content") or {}
            parts = content.get("parts", []) if isinstance(content, dict) else []
            text = "\n".join(str(part) for part in parts if isinstance(part, str)).strip()
            if not text:
                continue
            author = message.get("author") or {}
            items.append(
                {
                    "conversation_ref": conversation_ref,
                    "message_ref": str(message_ref),
                    "role": str(author.get("role") or "unknown"),
                    "content": text,
                    "created_at_source": message.get("create_time"),
                    "source_locator": {
                        "conversation_id": conversation_ref,
                        "message_id": str(message_ref),
                    },
                }
            )
    return sha256_bytes(raw), items


class ArchiveStore:
    """Persistence boundary for immutable source archives.

    The store deliberately exposes import/search only. It never updates or deletes
    archived source text. A DB-API-compatible PostgreSQL connection is sufficient.
    """

    def __init__(self, connection: ConnectionLike) -> None:
        self.connection = connection

    def import_chatgpt_export(self, path: str | Path) -> dict[str, int | str]:
        source_path = Path(path)
        source_hash, items = load_chatgpt_archive(source_path)
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO z1_archive_sources
                    (source_type, source_name, source_hash, source_version, metadata)
                VALUES ('CHATGPT_EXPORT', %s, %s, %s, %s::jsonb)
                ON CONFLICT (source_type, source_hash) DO NOTHING
                """,
                (
                    source_path.name,
                    source_hash,
                    "chatgpt-conversations-json",
                    json.dumps({"item_count": len(items)}),
                ),
            )
            cursor.execute(
                """
                SELECT id FROM z1_archive_sources
                WHERE source_type = 'CHATGPT_EXPORT' AND source_hash = %s
                """,
                (source_hash,),
            )
            source_id = str(cursor.fetchone()[0])

            inserted = 0
            for item in items:
                content_hash = hashlib.sha256(item["content"].encode("utf-8")).hexdigest()
                cursor.execute(
                    """
                    INSERT INTO z1_archive_items
                        (source_id, external_id, conversation_ref, message_ref, role,
                         content, content_hash, source_locator, created_at_source, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb,
                            CASE WHEN %s IS NULL THEN NULL ELSE to_timestamp(%s::double precision) END,
                            '{}'::jsonb)
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        source_id,
                        item["message_ref"],
                        item["conversation_ref"],
                        item["message_ref"],
                        item["role"],
                        item["content"],
                        content_hash,
                        json.dumps(item["source_locator"]),
                        item["created_at_source"],
                        item["created_at_source"],
                    ),
                )
                inserted += int(getattr(cursor, "rowcount", 0) == 1)

            self.connection.commit()
            return {
                "source_id": source_id,
                "source_hash": source_hash,
                "items_seen": len(items),
                "items_inserted": inserted,
            }
        except Exception:
            self.connection.rollback()
            raise

    def search(self, query: str, limit: int = 20) -> list[ArchiveItem]:
        """Search archived source text; results are evidence, never trusted memory."""
        if not query.strip():
            return []
        limit = max(1, min(limit, 100))
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT id, source_id, conversation_ref, message_ref, role, content,
                   source_locator, created_at_source
            FROM z1_archive_items
            WHERE search_document @@ plainto_tsquery('simple', %s)
            ORDER BY ts_rank(search_document, plainto_tsquery('simple', %s)) DESC,
                     created_at_source DESC NULLS LAST
            LIMIT %s
            """,
            (query, query, limit),
        )
        return [
            ArchiveItem(
                id=str(row[0]),
                source_id=str(row[1]),
                conversation_ref=row[2],
                message_ref=row[3],
                role=row[4],
                content=row[5],
                source_locator=row[6] or {},
                created_at_source=row[7].isoformat() if row[7] else None,
            )
            for row in cursor.fetchall()
        ]
