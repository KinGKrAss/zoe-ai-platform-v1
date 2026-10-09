import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from orchestration.models import TaskEnvelope, TaskResult
from orchestration.orchestrator import Orchestrator
from orchestration.providers import Provider


class FakeProvider(Provider):
    provider_id = "fake"
    model = "fake-1"

    async def run(self, envelope):
        return TaskResult(envelope.task_id, self.provider_id, self.model, f"ok:{envelope.task}")


def test_routing_and_identity():
    import asyncio
    async def run():
        events = []
        async def audit(event): events.append(event)
        result = await Orchestrator({"fake": FakeProvider()}, audit).dispatch(TaskEnvelope.create("hello", provider_id="fake", tenant_id="t1"))
        assert result.text == "ok:hello"
        assert result.task_id
        assert [e["event"] for e in events] == ["task.started", "task.completed"]
        assert events[0]["tenant_id"] == "t1"
    asyncio.run(run())
