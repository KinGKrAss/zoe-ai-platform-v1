from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


@dataclass
class GatewayRequest:
    request_id: str
    actor_type: str
    actor_id: str | None
    role: str
    scopes: set[str]


@dataclass
class ZoeTask:
    goal: str
    context: dict[str, Any] = field(default_factory=dict)
    tools_allowed: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING


class PolicyEngine:
    def authorize_tool(self, request: GatewayRequest, tool: str, allowed_tools: list[str]) -> None:
        if tool not in allowed_tools:
            raise PermissionError(f"tool not allowed by task: {tool}")
        required_scope = f"ZOEUSETOOL_{tool.upper()}"
        if required_scope not in request.scopes and "ADMIN" not in request.scopes:
            raise PermissionError(f"missing scope: {required_scope}")


class TaskRegistry:
    def __init__(self):
        self.tasks: dict[str, ZoeTask] = {}

    def create(self, task_id: str, task: ZoeTask) -> None:
        if task_id in self.tasks:
            raise ValueError("task already exists")
        self.tasks[task_id] = task

    def set_status(self, task_id: str, status: TaskStatus) -> None:
        self.tasks[task_id].status = status


class RequestRouter:
    def __init__(self, handlers: dict[str, Callable[..., Any]]):
        self.handlers = handlers

    def dispatch(self, service: str, *args: Any, **kwargs: Any) -> Any:
        if service not in self.handlers:
            raise KeyError(f"unknown service: {service}")
        return self.handlers[service](*args, **kwargs)


class Z1Orchestrator:
    def __init__(self, router: RequestRouter, policies: PolicyEngine, tasks: TaskRegistry):
        self.router = router
        self.policies = policies
        self.tasks = tasks

    def create_task(self, request: GatewayRequest, task_id: str, task: ZoeTask) -> ZoeTask:
        if "ZOEANALYZE" not in request.scopes and "ADMIN" not in request.scopes:
            raise PermissionError("missing scope: ZOEANALYZE")
        self.tasks.create(task_id, task)
        return task
