import pytest

from app.treasury import TreasuryLedger


def test_verified_reserve_is_aggregated():
    ledger = TreasuryLedger()
    ledger.preview(
        asset="EUR",
        quantity="1000",
        valuation_eur="1000",
        source="authorized-test-source",
        verified=True,
    )
    assert ledger.summary()["verified_reserve_eur"] == "1000"


def test_unverified_reserve_is_rejected():
    ledger = TreasuryLedger()
    with pytest.raises(ValueError, match="not verified"):
        ledger.preview(
            asset="EUR",
            quantity="1000",
            valuation_eur="1000",
            source="unverified-source",
            verified=False,
        )
