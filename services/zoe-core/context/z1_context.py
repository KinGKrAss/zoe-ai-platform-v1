"""Unified Zoë context adapters for Memory Core and the Z1 Wealth Registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence


@dataclass(frozen=True)
class MemoryContext:
    key: str
    content: str
    confidence: float
    source: str | None = None


@dataclass(frozen=True)
class WealthContext:
    asset_id: str
    asset_type: str
    verification_status: str
    value: Any = None
    evidence_count: int = 0


class MemoryProvider(Protocol):
    def search(self, query: str, *, owner_user_id: str | None = None) -> Sequence[MemoryContext]: ...


class WealthProvider(Protocol):
    def search_assets(
        self, query: str, *, owner_user_id: str | None = None
    ) -> Sequence[WealthContext]: ...


@dataclass(frozen=True)
class Z1KnowledgeContext:
    memories: tuple[MemoryContext, ...]
    wealth_assets: tuple[WealthContext, ...]


class Z1ContextBuilder:
    """Compose reviewed memory and wealth evidence without leaking persistence details."""

    def __init__(self, memory: MemoryProvider, wealth: WealthProvider) -> None:
        self.memory = memory
        self.wealth = wealth

    def build(self, query: str, *, owner_user_id: str | None = None) -> Z1KnowledgeContext:
        cleaned = query.strip()
        if not cleaned:
            raise ValueError("context query must not be empty")
        memories = tuple(self.memory.search(cleaned, owner_user_id=owner_user_id))
        assets = tuple(self.wealth.search_assets(cleaned, owner_user_id=owner_user_id))
        return Z1KnowledgeContext(memories=memories, wealth_assets=assets)
