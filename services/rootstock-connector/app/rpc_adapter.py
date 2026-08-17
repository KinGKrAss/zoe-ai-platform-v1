from __future__ import annotations

from decimal import Decimal

from .client import RootstockClient
from .models import WalletBalance

WEI_PER_RBTC = Decimal(10**18)


async def get_wallet_balance(client: RootstockClient, address: str) -> WalletBalance:
    chain_id = await client.chain_id()
    block_number = await client.block_number()
    balance_wei = await client.balance_wei(address)
    return WalletBalance(
        address=address,
        balance_wei=balance_wei,
        balance_rbtc=Decimal(balance_wei) / WEI_PER_RBTC,
        block_number=block_number,
        chain_id=chain_id,
    )
