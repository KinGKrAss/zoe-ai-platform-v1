from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from threading import RLock
from uuid import uuid4


def money(value: Decimal | str | int | float) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("invalid monetary amount") from exc
    if not amount.is_finite() or amount < 0:
        raise ValueError("amount must be finite and non-negative")
    return amount.quantize(Decimal("0.01"))


@dataclass(frozen=True)
class Asset:
    asset_id: str
    symbol: str
    asset_type: str
    decimals: int = 18
    target_value_eur: Decimal | None = None
    market_value_eur: Decimal | None = None
    valuation_status: str = "unverified"

    def __post_init__(self) -> None:
        if not self.asset_id or not self.symbol:
            raise ValueError("asset_id and symbol are required")
        if self.decimals < 0 or self.decimals > 36:
            raise ValueError("decimals must be between 0 and 36")
        if self.valuation_status not in {"unverified", "verified", "market"}:
            raise ValueError("invalid valuation_status")


@dataclass(frozen=True)
class LedgerAccount:
    account_id: str
    currency: str = "EUR"


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    asset_id: str
    source_account: str
    destination_account: str
    quantity: Decimal
    eur_value: Decimal | None
    reference: str | None = None
    status: str = "posted"


class Ledger:
    """Thread-safe double-entry-style asset movement ledger.

    The ledger records both sides of every movement and never assumes a market
    price for an asset. EUR valuation is optional and must be supplied explicitly.
    """

    def __init__(self) -> None:
        self._accounts: dict[str, LedgerAccount] = {}
        self._balances: dict[tuple[str, str], Decimal] = {}
        self._assets: dict[str, Asset] = {}
        self._transactions: list[Transaction] = []
        self._lock = RLock()

    def register_asset(self, asset: Asset) -> Asset:
        with self._lock:
            if asset.asset_id in self._assets:
                raise ValueError("asset already exists")
            self._assets[asset.asset_id] = asset
            return asset

    def register_account(self, account: LedgerAccount) -> LedgerAccount:
        with self._lock:
            if account.account_id in self._accounts:
                raise ValueError("account already exists")
            self._accounts[account.account_id] = account
            return account

    def post(self, *, asset_id: str, source_account: str, destination_account: str,
             quantity: Decimal | str | int | float, eur_value: Decimal | str | int | float | None = None,
             reference: str | None = None) -> Transaction:
        qty = Decimal(str(quantity))
        if not qty.is_finite() or qty <= 0:
            raise ValueError("quantity must be finite and positive")
        with self._lock:
            if asset_id not in self._assets:
                raise KeyError("unknown asset")
            if source_account not in self._accounts or destination_account not in self._accounts:
                raise KeyError("unknown account")
            source_key = (source_account, asset_id)
            destination_key = (destination_account, asset_id)
            source_balance = self._balances.get(source_key, Decimal("0"))
            if source_balance < qty:
                raise ValueError("insufficient balance")
            value = None if eur_value is None else money(eur_value)
            self._balances[source_key] = source_balance - qty
            self._balances[destination_key] = self._balances.get(destination_key, Decimal("0")) + qty
            tx = Transaction(str(uuid4()), asset_id, source_account, destination_account, qty, value, reference)
            self._transactions.append(tx)
            return tx

    def credit(self, *, asset_id: str, account_id: str, quantity: Decimal | str | int | float,
               eur_value: Decimal | str | int | float | None = None, reference: str | None = None) -> Transaction:
        qty = Decimal(str(quantity))
        if not qty.is_finite() or qty <= 0:
            raise ValueError("quantity must be finite and positive")
        with self._lock:
            if asset_id not in self._assets or account_id not in self._accounts:
                raise KeyError("unknown asset or account")
            key = (account_id, asset_id)
            self._balances[key] = self._balances.get(key, Decimal("0")) + qty
            tx = Transaction(str(uuid4()), asset_id, "external", account_id, qty,
                             None if eur_value is None else money(eur_value), reference)
            self._transactions.append(tx)
            return tx

    def balance(self, account_id: str, asset_id: str) -> Decimal:
        with self._lock:
            if account_id not in self._accounts:
                raise KeyError("unknown account")
            if asset_id not in self._assets:
                raise KeyError("unknown asset")
            return self._balances.get((account_id, asset_id), Decimal("0"))

    def transactions(self) -> tuple[Transaction, ...]:
        with self._lock:
            return tuple(self._transactions)
