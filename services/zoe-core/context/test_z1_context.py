import pytest

from .z1_context import MemoryContext, WealthContext, Z1ContextBuilder


class MemoryStub:
    def search(self, query: str, *, owner_user_id: str | None = None):
        return [MemoryContext("m1", query, 0.95, "test")]


class WealthStub:
    def search_assets(self, query: str, *, owner_user_id: str | None = None):
        return [WealthContext("asset-1", "real-estate", "VERIFIED", 1000000, 2)]


def test_context_builder_combines_memory_and_wealth():
    context = Z1ContextBuilder(MemoryStub(), WealthStub()).build("wohnung", owner_user_id="u1")
    assert context.memories[0].key == "m1"
    assert context.wealth_assets[0].verification_status == "VERIFIED"


def test_context_builder_rejects_empty_query():
    with pytest.raises(ValueError):
        Z1ContextBuilder(MemoryStub(), WealthStub()).build(" ")
