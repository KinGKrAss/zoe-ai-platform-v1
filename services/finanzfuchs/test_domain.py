from decimal import Decimal

import pytest

from finanzfuchs.domain import Asset, Ledger, LedgerAccount, money


def setup_ledger() -> Ledger:
    ledger = Ledger()
    ledger.register_asset(Asset("ppt", "PPT", "erc20", decimals=18, target_value_eur=Decimal("1.00")))
    ledger.register_account(LedgerAccount("treasury"))
    ledger.register_account(LedgerAccount("merchant"))
    return ledger


def test_money_is_decimal_and_cent_quantized() -> None:
    assert money("1.005") == Decimal("1.01")
    with pytest.raises(ValueError):
        money("-1")


def test_credit_and_transfer_preserve_double_sided_balance() -> None:
    ledger = setup_ledger()
    ledger.credit(asset_id="ppt", account_id="treasury", quantity="100", eur_value="100")
    tx = ledger.post(asset_id="ppt", source_account="treasury", destination_account="merchant", quantity="25", eur_value="25")
    assert tx.status == "posted"
    assert ledger.balance("treasury", "ppt") == Decimal("75")
    assert ledger.balance("merchant", "ppt") == Decimal("25")
    assert len(ledger.transactions()) == 2


def test_transfer_rejects_insufficient_balance_without_mutation() -> None:
    ledger = setup_ledger()
    ledger.credit(asset_id="ppt", account_id="treasury", quantity="10")
    with pytest.raises(ValueError, match="insufficient balance"):
        ledger.post(asset_id="ppt", source_account="treasury", destination_account="merchant", quantity="11")
    assert ledger.balance("treasury", "ppt") == Decimal("10")
    assert ledger.balance("merchant", "ppt") == Decimal("0")
    assert len(ledger.transactions()) == 1


def test_target_value_is_not_market_value() -> None:
    asset = Asset("ppt", "PPT", "erc20", target_value_eur=Decimal("1.00"), valuation_status="unverified")
    assert asset.target_value_eur == Decimal("1.00")
    assert asset.market_value_eur is None
    assert asset.valuation_status == "unverified"
