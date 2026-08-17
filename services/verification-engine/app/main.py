from __future__ import annotations

import os
from decimal import Decimal

import httpx
from fastapi import FastAPI

from .models import Claim, VerificationResult
from .router import verify_claim

app = FastAPI(title="Z1 Verification Engine", version="1.0.0")


async def verify_rootstock_via_connector(claim: Claim) -> tuple[bool, list[str]]:
    if claim.wallet is None:
        return False, ["rootstock wallet claim is missing"]
    base_url = os.getenv("ROOTSTOCK_CONNECTOR_URL")
    if not base_url:
        return False, ["ROOTSTOCK_CONNECTOR_URL is not configured"]

    url = f"{base_url.rstrip('/')}/v1/wallet/{claim.wallet.address}/balance"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()
            actual = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        return False, [f"rootstock connector unavailable: {type(exc).__name__}"]

    reasons: list[str] = []
    if actual.get("chain_id") != claim.wallet.chain_id:
        reasons.append("Rootstock chain id mismatch")
    if actual.get("block_number", -1) < claim.wallet.reported_block:
        reasons.append("claim block is newer than connector chain tip")
    try:
        actual_balance = Decimal(str(actual["balance_rbtc"]))
    except (KeyError, ValueError):
        return False, ["connector returned invalid balance"]
    if actual_balance != claim.wallet.reported_balance_rbtc:
        reasons.append("reported RBTC balance does not match connector")
    return not reasons, reasons


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/verify", response_model=VerificationResult)
async def verify(claim: Claim) -> VerificationResult:
    trusted_signer = os.getenv("Z1_TRUSTED_SIGNER")
    rootstock_verifier = verify_rootstock_via_connector if claim.source == "rootstock" else None
    return await verify_claim(
        claim,
        rootstock_verifier=rootstock_verifier,
        trusted_signer=trusted_signer,
    )
