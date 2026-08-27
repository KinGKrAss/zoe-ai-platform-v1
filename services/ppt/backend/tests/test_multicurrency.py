from decimal import Decimal

import pytest

from app.multicurrency import CurrencyRate, CurrencyRegistry, BRICS_CURRENCY_CODES


def test_verified_currency_can_be_quoted():
    registry = CurrencyRegistry()
    registry.register(CurrencyRate("INR", Decimal("90"), "test", True))
    assert registry.quote_from_eur(Decimal("2"), "INR") == Decimal("180.000000")


def test_unverified_currency_is_rejected():
    registry = CurrencyRegistry()
    registry.register(CurrencyRate("BRL", Decimal("6"), "test", False))
    with pytest.raises(ValueError):
        registry.quote_from_eur(Decimal("1"), "BRL")


def test_currency_codes_are_normalized():
    registry = CurrencyRegistry()
    registry.register(CurrencyRate("cny", Decimal("8"), "test", True))
    assert registry.supported() == ["CNY"]


def test_brics_compatible_configuration_contains_core_rails():
    for code in ("BRL", "CNY", "INR", "RUB", "ZAR"):
        assert code in BRICS_CURRENCY_CODES
