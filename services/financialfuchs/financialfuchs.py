from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

class Risk(str, Enum):
    GREEN = 'green'
    AMBER = 'amber'
    RED = 'red'
    UNKNOWN = 'unknown'

@dataclass(frozen=True)
class Reserve:
    valuation_eur: Decimal
    verified: bool

@dataclass(frozen=True)
class Supply:
    token_amount: Decimal

@dataclass(frozen=True)
class Coverage:
    reserve_eur: Decimal
    supply_ppt: Decimal
    reference_eur_per_ppt: Decimal
    coverage_ratio: Decimal | None
    risk: Risk


def assess(reserve: Reserve, supply: Supply, reference_eur_per_ppt: Decimal = Decimal('1')) -> Coverage:
    if not reserve.verified or supply.token_amount <= 0:
        return Coverage(reserve.valuation_eur, supply.token_amount, reference_eur_per_ppt, None, Risk.UNKNOWN)
    required = supply.token_amount * reference_eur_per_ppt
    ratio = reserve.valuation_eur / required if required else None
    if ratio is None:
        risk = Risk.UNKNOWN
    elif ratio >= Decimal('1'):
        risk = Risk.GREEN
    elif ratio >= Decimal('0.8'):
        risk = Risk.AMBER
    else:
        risk = Risk.RED
    return Coverage(reserve.valuation_eur, supply.token_amount, reference_eur_per_ppt, ratio, risk)
