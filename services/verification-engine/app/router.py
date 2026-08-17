from __future__ import annotations

from .models import Claim, VerificationResult, VerificationStatus
from .verifier_schema import verify_schema
from .verifier_signature import verify_signature


async def verify_claim(
    claim: Claim,
    *,
    rootstock_verifier=None,
    revolut_verifier=None,
    trusted_signer: str | None = None,
    require_signature: bool = True,
) -> VerificationResult:
    schema_valid, reasons = verify_schema(claim)
    if not schema_valid:
        return VerificationResult(
            schema_valid=False,
            rootstock_valid=None,
            revolut_valid=None,
            signature_valid=None,
            status=VerificationStatus.REJECTED,
            reasons=reasons,
        )

    rootstock_valid = None
    revolut_valid = None
    signature_valid = None

    if claim.source == "rootstock":
        if rootstock_verifier is None:
            rootstock_valid = False
            reasons.append("Rootstock verifier is not configured")
        else:
            rootstock_valid, rootstock_reasons = await rootstock_verifier(claim)
            reasons.extend(rootstock_reasons)
    elif claim.source == "revolut":
        if revolut_verifier is None:
            revolut_valid = False
            reasons.append("Revolut verifier is not configured")
        else:
            revolut_valid, revolut_reasons = await revolut_verifier(claim)
            reasons.extend(revolut_reasons)

    if require_signature:
        signature_valid, signature_reasons = verify_signature(claim, trusted_signer)
        reasons.extend(signature_reasons)
    else:
        signature_valid = None

    source_valid = (
        rootstock_valid if claim.source == "rootstock" else revolut_valid if claim.source == "revolut" else True
    )
    verified = schema_valid and bool(source_valid) and (signature_valid is True if require_signature else True)
    return VerificationResult(
        schema_valid=schema_valid,
        rootstock_valid=rootstock_valid,
        revolut_valid=revolut_valid,
        signature_valid=signature_valid,
        status=VerificationStatus.VERIFIED if verified else VerificationStatus.PENDING_ON_CHAIN_PROOF,
        reasons=reasons,
    )
