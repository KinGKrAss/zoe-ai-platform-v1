from __future__ import annotations

from memory_gateway import MemoryGateway


def test_memory_gateway_requires_database_and_owner() -> None:
    gateway = MemoryGateway(database_url=None, owner_user_id=None)
    assert gateway.configured is False


def test_memory_gateway_is_configured_only_with_both_values() -> None:
    gateway = MemoryGateway(database_url="postgresql://example", owner_user_id="owner")
    assert gateway.configured is True
