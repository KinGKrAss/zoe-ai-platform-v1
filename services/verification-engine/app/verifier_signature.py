from __future__ import annotations

import json

from eth_account import Account
from eth_account.messages import encode_defunct

from .models import Claim


def _canonical_payload(claim: Claim) -> str:
    payload = claim.model_dump(mode="json", exclude={"signature"})
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def verify_signature(claim: Claim, trusted_signer: str | None) -> tuple[bool, list[str]]:
    if not trusted_signer:
        return False, ["no trusted signer configured"]
    if not claim.signature:
        return False, ["cryptographic signature is missing"]
    try:
        recovered = Account.recover_message(
            encode_defunct(text=_canonical_payload(claim)),
            signature=claim.signature,
        )
    except Exception as exc:
        return False, [f"signature verification failed: {type(exc).__name__}"]
    if recovered.lower() != trusted_signer.lower():
        return False, ["recovered signer does not match trusted signer"]
    if claim.signer_address and recovered.lower() != claim.signer_address.lower():
        return False, ["recovered signer does not match claim signer_address"]
    return True, []
