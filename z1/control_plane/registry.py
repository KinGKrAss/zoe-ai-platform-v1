"""File-backed Z1 coordination registry.

The registry is deliberately deterministic and dependency-free. It is a
coordination contract, not a distributed lock service. Production deployments
should back the same contract with transactional storage/leases.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
import json
from threading import RLock
from typing import Any


class Status(StrEnum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    MERGED = "MERGED"
    CLOSED = "CLOSED"


@dataclass
class Task:
    task_id: str
    title: str
    owner: str
    module: str
    branch: str
    status: Status = Status.PLANNED
    dependencies: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    notes: str = ""
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Agent:
    agent_id: str
    name: str
    role: str
    capabilities: list[str] = field(default_factory=list)
    active_task: str | None = None


class CoordinationRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._lock = RLock()
        self.data: dict[str, Any] = {"agents": {}, "tasks": {}, "locks": {}, "decisions": []}
        self.load()

    def load(self) -> None:
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.path)

    def register_agent(self, agent: Agent) -> None:
        with self._lock:
            self.data["agents"][agent.agent_id] = asdict(agent)
            self.save()

    def register_task(self, task: Task) -> None:
        with self._lock:
            if task.task_id in self.data["tasks"]:
                raise ValueError(f"Task already exists: {task.task_id}")
            self.data["tasks"][task.task_id] = asdict(task)
            self.save()

    def acquire_lock(self, module: str, agent_id: str, task_id: str) -> None:
        with self._lock:
            current = self.data["locks"].get(module)
            if current and current["agent_id"] != agent_id:
                raise RuntimeError(
                    f"Module '{module}' is locked by {current['agent_id']} for {current['task_id']}"
                )
            self.data["locks"][module] = {
                "agent_id": agent_id,
                "task_id": task_id,
                "acquired_at": datetime.now(timezone.utc).isoformat(),
            }
            self.data["tasks"][task_id]["status"] = Status.IN_PROGRESS
            self.data["tasks"][task_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
            self.data["agents"][agent_id]["active_task"] = task_id
            self.save()

    def release_lock(self, module: str, agent_id: str) -> None:
        with self._lock:
            current = self.data["locks"].get(module)
            if current and current["agent_id"] != agent_id:
                raise PermissionError("Only the lock owner can release a module lock")
            self.data["locks"].pop(module, None)
            self.save()

    def record_decision(self, decision_id: str, decision: str, by: str) -> None:
        with self._lock:
            self.data["decisions"].append({
                "decision_id": decision_id,
                "decision": decision,
                "by": by,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            self.save()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return json.loads(json.dumps(self.data))


class TaskRegistry(CoordinationRegistry):
    pass


class AgentRegistry(CoordinationRegistry):
    pass
