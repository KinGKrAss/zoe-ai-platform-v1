from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

ReviewStatus = Literal["draft", "reviewed", "accepted", "rejected"]


@dataclass(frozen=True)
class SourceReference:
    conversation_id: str
    message_id: str
    role: str
    excerpt: str


@dataclass(frozen=True)
class Message:
    conversation_id: str
    message_id: str
    role: str
    content: str


@dataclass(frozen=True)
class MemoryCandidate:
    candidate_id: str
    content: str
    candidate_type: str
    source_references: tuple[SourceReference, ...]
    review_status: ReviewStatus = "draft"
    dedupe_key: str = ""
    extraction_version: str = "2.0"
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CandidateDecision:
    candidate_id: str
    status: str
    reason: str | None = None

    def validate(self) -> None:
        if self.status not in {"draft", "reviewed", "accepted", "rejected"}:
            raise ValueError(f"invalid candidate status: {self.status}")
