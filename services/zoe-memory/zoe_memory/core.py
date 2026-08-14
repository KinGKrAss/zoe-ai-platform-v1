"""Memory Core V2 service primitives.

This module defines the stable application contract for ownership, canonical
memories, embeddings and review state. Database-specific persistence remains
behind an adapter so the service can later use pgvector without changing Zoë's
Memory Core API.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Protocol


class MemoryStore(Protocol):
    def save(self, record: "MemoryRecord") -> None: ...
    def search(self, text: str, owner_user_id: str | None, limit: int) -> list["MemoryRecord"]: ...
    def archive(self, memory_id: str) -> None: ...


@dataclass
class MemoryRecord:
    id: str
    content: str
    memory_type: str
    owner_user_id: str | None = None
    review_status: str = "accepted"
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None
    embedding_model: str | None = None

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.content.strip().encode("utf-8")).hexdigest()


class MemoryCore:
    def __init__(self, store: MemoryStore):
        self.store = store

    def put(self, record: MemoryRecord) -> MemoryRecord:
        if record.review_status not in {"accepted", "archived"}:
            raise ValueError("review_status must be accepted or archived")
        if record.embedding is not None and not record.embedding_model:
            raise ValueError("embedding_model is required when embedding is supplied")
        self.store.save(record)
        return record

    def recall(self, text: str, owner_user_id: str | None = None, limit: int = 20) -> list[MemoryRecord]:
        if not text.strip():
            return []
        return self.store.search(text.strip(), owner_user_id, max(1, min(limit, 100)))

    def archive(self, memory_id: str) -> None:
        self.store.archive(memory_id)
