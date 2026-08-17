from decimal import Decimal

import pytest

from app.rpc_adapter import get_wallet_balance


class FakeRootstock:
    async def chain_id(self) -> int:
        return 30

    async def block_number(self) -> int:
        return 5_524_300

    async def balance_wei(self, address: str) -> int:
        assert address.startswith("0x")
        return 15_587_130_432_878_405_800


@pytest.mark.asyncio
async def test_wallet_balance_uses_exact_wei_conversion() -> None:
    result = await get_wallet_balance(FakeRootstock(), "0x" + "a" * 40)
    assert result.chain_id == 30
    assert result.block_number == 5_524_300
    assert result.balance_wei == 15_587_130_432_878_405_800
    assert result.balance_rbtc == Decimal("15.5871304328784058")
