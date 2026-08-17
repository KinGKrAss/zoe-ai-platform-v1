from __future__ import annotations

from typing import Any

import httpx


class RootstockRpcError(RuntimeError):
    """Raised when a Rootstock JSON-RPC request fails."""


class RootstockClient:
    def __init__(self, rpc_url: str, *, timeout: float = 10.0) -> None:
        if not rpc_url:
            raise ValueError("ROOTSTOCK_RPC_URL is required")
        self.rpc_url = rpc_url
        self.timeout = timeout

    async def call(self, method: str, params: list[Any]) -> Any:
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.rpc_url, json=payload)
            response.raise_for_status()
            body = response.json()
        if body.get("error"):
            error = body["error"]
            raise RootstockRpcError(f"RPC {error.get('code')}: {error.get('message')}")
        if "result" not in body:
            raise RootstockRpcError("RPC response did not contain result")
        return body["result"]

    async def chain_id(self) -> int:
        return int(await self.call("eth_chainId", []), 16)

    async def block_number(self) -> int:
        return int(await self.call("eth_blockNumber", []), 16)

    async def balance_wei(self, address: str) -> int:
        return int(await self.call("eth_getBalance", [address, "latest"]), 16)

    async def transaction_count(self, address: str) -> int:
        return int(await self.call("eth_getTransactionCount", [address, "latest"]), 16)
