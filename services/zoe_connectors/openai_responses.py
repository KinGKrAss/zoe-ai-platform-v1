"""Server-side OpenAI Responses API connector for Z1.

The connector never reads credentials from client requests and never logs prompts,
responses, or API keys. Configure OPENAI_API_KEY in the backend environment.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from openai import AsyncOpenAI, OpenAIError


class OpenAIConnectorError(RuntimeError):
    """Raised when the OpenAI connector is not configured or a call fails."""


@dataclass(frozen=True, slots=True)
class OpenAISettings:
    api_key: str = field(repr=False)
    model: str = "gpt-4o"
    timeout_seconds: float = 60.0
    max_retries: int = 2

    @classmethod
    def from_env(cls) -> "OpenAISettings":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise OpenAIConnectorError(
                "OPENAI_API_KEY is missing from the server environment."
            )

        return cls(
            api_key=api_key,
            model=os.getenv("OPENAI_MODEL", "gpt-4o").strip() or "gpt-4o",
            timeout_seconds=float(os.getenv("OPENAI_TIMEOUT_SECONDS", "60")),
            max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "2")),
        )


class OpenAIResponsesConnector:
    """Calls an OpenAI model through the Responses API from a trusted backend."""

    def __init__(
        self,
        settings: OpenAISettings | None = None,
        *,
        client: AsyncOpenAI | None = None,
    ) -> None:
        self.settings = settings or OpenAISettings.from_env()
        self._client = client or AsyncOpenAI(
            api_key=self.settings.api_key,
            timeout=self.settings.timeout_seconds,
            max_retries=self.settings.max_retries,
        )

    async def generate(
        self,
        prompt: str,
        *,
        instructions: str | None = None,
    ) -> str:
        """Generate a text response. Tool execution remains with Z1's tool router."""
        if not prompt.strip():
            raise ValueError("prompt must not be empty")

        try:
            response: Any = await self._client.responses.create(
                model=self.settings.model,
                input=prompt,
                instructions=instructions,
            )
        except OpenAIError as exc:
            # Do not include request content or credentials in the raised message.
            raise OpenAIConnectorError(
                f"OpenAI request failed ({type(exc).__name__})."
            ) from exc

        text = getattr(response, "output_text", "")
        if not isinstance(text, str) or not text.strip():
            raise OpenAIConnectorError("OpenAI returned no text output.")
        return text

    async def close(self) -> None:
        """Close the underlying HTTP client during application shutdown."""
        await self._client.close()
