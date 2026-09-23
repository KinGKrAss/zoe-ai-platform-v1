from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass(slots=True)
class TaskEnvelope:
    task_id: str
    task: str
    agent_id: str = "zoe-core"
    model_id: str | None = None
    provider_id: str | None = None
    conversation_id: str | None = None
    parent_task_id: str | None = None
    tenant_id: str = "default"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, task: str, **kwargs: Any) -> "TaskEnvelope":
        return cls(task_id=str(uuid.uuid4()), task=task, **kwargs)


@dataclass(slots=True)
class TaskResult:
    task_id: str
    provider_id: str
    model_id: str
    text: str
    status: str = "completed"
    metadata: dict[str, Any] = field(default_factory=dict)
