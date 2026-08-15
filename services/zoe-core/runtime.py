"""Executable Zoë orchestration boundary for Z1.

This first runtime is intentionally provider-agnostic. It establishes the
stable request lifecycle without coupling Z1 to a specific LLM vendor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ZoeIntent:
    text: str
    kind: str = "general"


@dataclass(frozen=True)
class ZoePlan:
    steps: tuple[str, ...]


@dataclass(frozen=True)
class ZoeResult:
    intent: ZoeIntent
    plan: ZoePlan
    response: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


class ZoeCoreRuntime:
    """Deterministic orchestration shell around future model/tool adapters."""

    def understand(self, text: str) -> ZoeIntent:
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("Zoë input must not be empty")
        lowered = cleaned.lower()
        if any(word in lowered for word in ("prüf", "beleg", "nachweis", "dokument")):
            kind = "document_analysis"
        elif any(word in lowered for word in ("vermögen", "immobil", "wohnung", "asset")):
            kind = "wealth"
        else:
            kind = "general"
        return ZoeIntent(text=cleaned, kind=kind)

    def plan(self, intent: ZoeIntent) -> ZoePlan:
        return ZoePlan(
            steps=(
                "load_context",
                f"route:{intent.kind}",
                "authorize_tools",
                "execute_or_delegate",
                "produce_auditable_response",
            )
        )

    def run(self, text: str, *, session_id: str | None = None) -> ZoeResult:
        intent = self.understand(text)
        plan = self.plan(intent)
        response = "Zoë Core accepted the request and produced an execution plan."
        return ZoeResult(
            intent=intent,
            plan=plan,
            response=response,
            metadata={"session_id": session_id, "runtime": "z1-zoe-core-v1"},
        )
