import pytest

from app.client import RootstockClient, RootstockRpcError


class FakeResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {"jsonrpc": "2.0", "id": 1, "result": "0x1e"}


class FakeClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, *args, **kwargs):
        return FakeResponse()


@pytest.mark.asyncio
async def test_chain_id(monkeypatch) -> None:
    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
    client = RootstockClient("https://example.invalid")
    assert await client.chain_id() == 30


@pytest.mark.asyncio
async def test_rpc_error_is_rejected(monkeypatch) -> None:
    import httpx

    class ErrorResponse(FakeResponse):
        def json(self) -> dict:
            return {"jsonrpc": "2.0", "id": 1, "error": {"code": -32000, "message": "boom"}}

    class ErrorClient(FakeClient):
        async def post(self, *args, **kwargs):
            return ErrorResponse()

    monkeypatch.setattr(httpx, "AsyncClient", ErrorClient)
    with pytest.raises(RootstockRpcError):
        await RootstockClient("https://example.invalid").chain_id()
