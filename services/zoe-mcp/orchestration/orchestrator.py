from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any

from .models import TaskEnvelope, TaskResult
from .providers import Provider, ProviderError

AuditFn = Callable[[dict[str, Any]], Awaitable[None]]


class Orchestrator:
    def __init__(self, providers: dict[str, Provider], audit: AuditFn | None = None) -> None:
        self.providers = providers
        self.audit = audit

    async def dispatch(self, envelope: TaskEnvelope) -> TaskResult:
        provider_id = envelope.provider_id or self._select_provider(envelope)
        provider = self.providers.get(provider_id)
        if provider is None:
            raise ProviderError(f"No configured provider: {provider_id}")
        started = time.monotonic()
        await self._audit("task.started", envelope, provider_id)
        try:
            result = await provider.run(envelope)
        except Exception as exc:
            await self._audit("task.failed", envelope, provider_id, error=str(exc))
            raise
        result.metadata["latency_ms"] = round((time.monotonic() - started) * 1000, 2)
        await self._audit("task.completed", envelope, provider_id, result=result.text)
        return result

    def _select_provider(self, envelope: TaskEnvelope) -> str:
        preferred = envelope.metadata.get("preferred_providers", [])
        for provider_id in preferred:
            if provider_id in self.providers:
                return provider_id
        if envelope.model_id:
            for provider in self.providers.values():
                if getattr(provider, "model", None) == envelope.model_id:
                    return provider.provider_id
        if "openai" in self.providers:
            return "openai"
        if "gemini" in self.providers:
            return "gemini"
        if self.providers:
            return next(iter(self.providers))
        raise ProviderError("No AI providers are configured")

    async def _audit(self, event: str, envelope: TaskEnvelope, provider_id: str, **extra: Any) -> None:
        if self.audit:
            await self.audit({"event": event, "task_id": envelope.task_id, "agent_id": envelope.agent_id, "tenant_id": envelope.tenant_id, "provider_id": provider_id, **extra})
