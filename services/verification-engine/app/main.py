from __future__ import annotations

import os

from fastapi import FastAPI

from .models import Claim, VerificationResult
from .router import verify_claim

app = FastAPI(title="Z1 Verification Engine", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/verify", response_model=VerificationResult)
async def verify(claim: Claim) -> VerificationResult:
    # Production wiring injects real connector adapters here. Until configured,
    # the engine fails closed rather than treating imported claims as verified.
    trusted_signer = os.getenv("Z1_TRUSTED_SIGNER")
    return await verify_claim(claim, trusted_signer=trusted_signer)
