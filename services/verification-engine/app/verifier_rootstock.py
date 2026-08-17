from __future__ import annotations

from decimal import Decimal
from typing import Protocol

from .models import Claim


class RootstockReader(Protocol):
    async def chain_id(self) -> int: ...
    async def block_number(self) -> int: ...
    async def balance_wei(self, address: str) -> int: ...


async def verify_rootstock(claim: Claim, client: RootstockReader) -> tuple[bool, list[str]]:
    if claim.wallet is None:
        return False, ["rootstock wallet claim is missing"]
    wallet = claim.wallet
    try:
        chain_id = await client.chain_id()
        block = await client.block_number()
        balance_wei = await client.balance_wei(wallet.address)
    except Exception as exc:
        return False, [f"rootstock verification unavailable: {type(exc).__name__}"]

    actual_balance = Decimal(balance_wei) / Decimal(10**18)
    reasons: list[str] = []
    if chain_id != wallet.chain_id:
        reasons.append(f"chain id mismatch: expected {wallet.chain_id}, got {chain_id}")
    if block < wallet.reported_block:
        reasons.append("reported block is newer than current chain tip")
    if actual_balance != wallet.reported_balance_rbtc:
        reasons.append("reported RBTC balance does not match current on-chain balance")
    return not reasons, reasons
