from decimal import Decimal

import pytest
from eth_account import Account
from eth_account.messages import encode_defunct

from app.models import Claim, VerificationStatus
from app.router import verify_claim
from app.verifier_signature import _canonical_payload


class FakeRootstock:
    async def __call__(self, claim):
        return True, []


def signed_claim() -> tuple[Claim, str]:
    account = Account.create()
    unsigned = Claim(
        source="rootstock",
        source_reference="rpc://rootstock/latest",
        wallet={
            "address": "0x" + "a" * 40,
            "reported_balance_rbtc": Decimal("15.5871304328784058"),
            "reported_block": 5_524_300,
            "chain_id": 30,
        },
        signer_address=account.address,
    )
    signed = account.sign_message(encode_defunct(text=_canonical_payload(unsigned)))
    return unsigned.model_copy(update={"signature": signed.signature.hex()}), account.address


@pytest.mark.asyncio
async def test_claim_requires_real_signature_and_source_verification() -> None:
    claim, signer = signed_claim()
    result = await verify_claim(
        claim,
        rootstock_verifier=FakeRootstock(),
        trusted_signer=signer,
    )
    assert result.status == VerificationStatus.VERIFIED
    assert result.rootstock_valid is True
    assert result.signature_valid is True


@pytest.mark.asyncio
async def test_missing_signature_fails_closed() -> None:
    claim = Claim(
        source="rootstock",
        wallet={
            "address": "0x" + "a" * 40,
            "reported_balance_rbtc": Decimal("1"),
            "reported_block": 1,
            "chain_id": 30,
        },
    )
    result = await verify_claim(
        claim,
        rootstock_verifier=FakeRootstock(),
        trusted_signer="0x" + "b" * 40,
    )
    assert result.status != VerificationStatus.VERIFIED
    assert result.signature_valid is False
