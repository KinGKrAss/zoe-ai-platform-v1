from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN


@dataclass(frozen=True)
class CurrencyRate:
    code: str
    units_per_eur: Decimal
    source: str
    verified: bool = False


class CurrencyRegistry:
    """Deterministic FX registry for payment quotes.

    Rates are configuration/evidence, not a claim that PPT is a legal tender
    or that a currency is officially part of a BRICS settlement system.
    """

    def __init__(self) -> None:
        self._rates: dict[str, CurrencyRate] = {}

    def register(self, rate: CurrencyRate) -> None:
        if not rate.code or rate.units_per_eur <= 0:
            raise ValueError("invalid currency rate")
        self._rates[rate.code.upper()] = rate

    def quote_from_eur(self, amount_eur: Decimal, currency: str) -> Decimal:
        if amount_eur <= 0:
            raise ValueError("amount_eur must be positive")
        code = currency.upper()
        rate = self._rates.get(code)
        if rate is None or not rate.verified:
            raise ValueError("currency rate is unavailable or unverified")
        return (amount_eur * rate.units_per_eur).quantize(Decimal("0.000001"), rounding=ROUND_DOWN)

    def supported(self) -> list[str]:
        return sorted(code for code, rate in self._rates.items() if rate.verified)


# BRICS-compatible settlement rails are represented as configurable currencies,
# not as a hard-coded claim of official BRICS membership or legal tender.
BRICS_CURRENCY_CODES = ("AED", "BRL", "CNY", "EGP", "ETB", "IDR", "INR", "IRR", "RUB", "ZAR")
