from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field


class VerificationStatus(StrEnum):
    PENDING_ON_CHAIN_PROOF = "PENDING_ON_CHAIN_PROOF"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    UNAVAILABLE = "UNAVAILABLE"


class WalletClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    address: str
    reported_balance_rbtc: Decimal = Field(ge=0)
    reported_block: int = Field(ge=0)
    chain_id: int = Field(default=30, ge=1)


class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    source_reference: str | None = None
    wallet: WalletClaim | None = None
    signature: str | None = None
    signer_address: str | None = None


class VerificationResult(BaseModel):
    schema_valid: bool
    rootstock_valid: bool | None
    revolut_valid: bool | None
    signature_valid: bool | None
    status: VerificationStatus
    reasons: list[str] = Field(default_factory=list)
