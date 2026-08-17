from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException

from .client import RootstockClient, RootstockRpcError
from .models import WalletBalance
from .rpc_adapter import get_wallet_balance

app = FastAPI(title="Z1 Rootstock Connector", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/wallet/{address}/balance", response_model=WalletBalance)
async def wallet_balance(address: str) -> WalletBalance:
    rpc_url = os.getenv("ROOTSTOCK_RPC_URL")
    if not rpc_url:
        raise HTTPException(status_code=503, detail="ROOTSTOCK_RPC_URL is not configured")
    try:
        return await get_wallet_balance(RootstockClient(rpc_url), address)
    except (ValueError, RootstockRpcError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
