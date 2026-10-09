from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any

import httpx

from .models import TaskEnvelope, TaskResult


class ProviderError(RuntimeError):
    pass


class Provider(ABC):
    provider_id: str

    @abstractmethod
    async def run(self, envelope: TaskEnvelope) -> TaskResult:
        raise NotImplementedError


class OpenAIResponsesProvider(Provider):
    provider_id = "openai"

    def __init__(self, api_key: str, model: str, base_url: str = "https://api.openai.com/v1") -> None:
        self.api_key, self.model, self.base_url = api_key, model, base_url.rstrip("/")

    async def run(self, envelope: TaskEnvelope) -> TaskResult:
        payload = {"model": self.model, "input": envelope.task}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f"{self.base_url}/responses", json=payload, headers=headers)
        if response.is_error:
            raise ProviderError(f"OpenAI returned HTTP {response.status_code}: {response.text[:500]}")
        data = response.json()
        text = data.get("output_text")
        if not text:
            parts: list[str] = []
            for item in data.get("output", []):
                for content in item.get("content", []):
                    if content.get("type") in {"output_text", "text"} and content.get("text"):
                        parts.append(content["text"])
            text = "\n".join(parts).strip()
        if not text:
            raise ProviderError("OpenAI response contained no text output")
        return TaskResult(envelope.task_id, self.provider_id, self.model, text, metadata={"response_id": data.get("id")})


class GeminiGenerateContentProvider(Provider):
    provider_id = "gemini"

    def __init__(self, api_key: str, model: str, base_url: str = "https://generativelanguage.googleapis.com/v1beta") -> None:
        self.api_key, self.model, self.base_url = api_key, model, base_url.rstrip("/")

    async def run(self, envelope: TaskEnvelope) -> TaskResult:
        payload = {"contents": [{"role": "user", "parts": [{"text": envelope.task}]}]}
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.base_url}/models/{self.model}:generateContent",
                params={"key": self.api_key}, json=payload,
            )
        if response.is_error:
            raise ProviderError(f"Gemini returned HTTP {response.status_code}: {response.text[:500]}")
        data = response.json()
        parts = []
        for candidate in data.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                if part.get("text"):
                    parts.append(part["text"])
        text = "\n".join(parts).strip()
        if not text:
            raise ProviderError("Gemini response contained no text output")
        return TaskResult(envelope.task_id, self.provider_id, self.model, text, metadata={"finish_reason": (data.get("candidates") or [{}])[0].get("finishReason")})


class HttpJsonProvider(Provider):
    """Explicit adapter for a configured external provider endpoint.

    It is intentionally disabled unless an endpoint and API key are supplied.
    This avoids pretending that GitHub Copilot has a public generic inference API.
    """

    def __init__(self, provider_id: str, endpoint: str, api_key: str, model: str) -> None:
        self.provider_id, self.endpoint, self.api_key, self.model = provider_id, endpoint, api_key, model

    async def run(self, envelope: TaskEnvelope) -> TaskResult:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"task_id": envelope.task_id, "model": self.model, "input": envelope.task}
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(self.endpoint, json=payload, headers=headers)
        if response.is_error:
            raise ProviderError(f"{self.provider_id} returned HTTP {response.status_code}: {response.text[:500]}")
        data: dict[str, Any] = response.json()
        text = data.get("text") or data.get("output_text") or data.get("output")
        if not isinstance(text, str) or not text.strip():
            raise ProviderError(f"{self.provider_id} response contained no text output")
        return TaskResult(envelope.task_id, self.provider_id, self.model, text.strip(), metadata=data.get("metadata", {}))


def build_provider_registry(env: dict[str, str] | None = None) -> dict[str, Provider]:
    env = env or os.environ
    registry: dict[str, Provider] = {}
    if env.get("OPENAI_API_KEY") and env.get("OPENAI_MODEL"):
        registry["openai"] = OpenAIResponsesProvider(env["OPENAI_API_KEY"], env["OPENAI_MODEL"], env.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    if env.get("GEMINI_API_KEY") and env.get("GEMINI_MODEL"):
        registry["gemini"] = GeminiGenerateContentProvider(env["GEMINI_API_KEY"], env["GEMINI_MODEL"], env.get("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"))
    if env.get("COPILOT_ENDPOINT") and env.get("COPILOT_API_KEY") and env.get("COPILOT_MODEL"):
        registry["copilot"] = HttpJsonProvider("copilot", env["COPILOT_ENDPOINT"], env["COPILOT_API_KEY"], env["COPILOT_MODEL"])
    return registry
