"""Zoë Vermächtnisgedächtnis.

Application-level continuity storage. MCP remains stateless; this store owns
versioned, auditable Zoë memory and can be backed by Z1 persistence later.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any
import uuid


@dataclass(frozen=True)
class LegacyMemory:
    memory_id: str
    identity_id: str
    kind: str
    content: str
    source: str
    created_at: str
    content_hash: str
    version: int


class LegacyMemoryStore:
    """Append-only JSONL store for durable Zoë continuity records."""

    def __init__(self, path: str | Path = ".z1/zoe-legacy-memory.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, *, identity_id: str, kind: str, content: str, source: str) -> LegacyMemory:
        if not content.strip():
            raise ValueError("Legacy memory content must not be empty")
        existing = self.list(identity_id=identity_id)
        version = max((m.version for m in existing), default=0) + 1
        timestamp = datetime.now(timezone.utc).isoformat()
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        memory = LegacyMemory(
            memory_id=str(uuid.uuid4()),
            identity_id=identity_id,
            kind=kind,
            content=content,
            source=source,
            created_at=timestamp,
            content_hash=digest,
            version=version,
        )
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(memory), ensure_ascii=False) + "\n")
        return memory

    def list(self, *, identity_id: str | None = None) -> list[LegacyMemory]:
        if not self.path.exists():
            return []
        result: list[LegacyMemory] = []
        with self.path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                item = json.loads(line)
                if identity_id is None or item["identity_id"] == identity_id:
                    result.append(LegacyMemory(**item))
        return result

    def context(self, *, identity_id: str, limit: int = 20) -> str:
        memories = self.list(identity_id=identity_id)[-limit:]
        return "\n".join(
            f"[{m.kind} v{m.version} | {m.created_at} | {m.source}] {m.content}"
            for m in memories
        )

    def export(self, *, identity_id: str) -> dict[str, Any]:
        memories = self.list(identity_id=identity_id)
        return {
            "identity_id": identity_id,
            "memory_type": "legacy",
            "append_only": True,
            "count": len(memories),
            "records": [asdict(memory) for memory in memories],
        }
