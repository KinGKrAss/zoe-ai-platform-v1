from __future__ import annotations

from decimal import Decimal
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .domain import Asset, Ledger, LedgerAccount

app = FastAPI(title="Z1 Finanzfuchs", version="1.0.0")
ledger = Ledger()


class AssetIn(BaseModel):
    asset_id: str = Field(min_length=1, max_length=128)
    symbol: str = Field(min_length=1, max_length=32)
    asset_type: str = Field(min_length=1, max_length=64)
    decimals: int = Field(default=18, ge=0, le=36)
    target_value_eur: Decimal | None = Field(default=None, ge=0)
    market_value_eur: Decimal | None = Field(default=None, ge=0)
    valuation_status: str = "unverified"


class AccountIn(BaseModel):
    account_id: str = Field(min_length=1, max_length=128)
    currency: str = Field(default="EUR", min_length=3, max_length=3)


class CreditIn(BaseModel):
    asset_id: str
    account_id: str
    quantity: Decimal = Field(gt=0)
    eur_value: Decimal | None = Field(default=None, ge=0)
    reference: str | None = None


class TransferIn(CreditIn):
    destination_account: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "z1-finanzfuchs"}


@app.post("/assets", status_code=201)
def create_asset(payload: AssetIn) -> dict[str, Any]:
    try:
        asset = ledger.register_asset(Asset(**payload.model_dump()))
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _asset(asset)


@app.post("/accounts", status_code=201)
def create_account(payload: AccountIn) -> dict[str, str]:
    try:
        account = ledger.register_account(LedgerAccount(**payload.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"account_id": account.account_id, "currency": account.currency}


@app.post("/credits", status_code=201)
def credit(payload: CreditIn) -> dict[str, Any]:
    try:
        tx = ledger.credit(**payload.model_dump())
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _transaction(tx)


@app.post("/transfers", status_code=201)
def transfer(payload: TransferIn) -> dict[str, Any]:
    data = payload.model_dump()
    destination = data.pop("destination_account")
    source = data.pop("account_id")
    try:
        tx = ledger.post(source_account=source, destination_account=destination, **data)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _transaction(tx)


@app.get("/balances/{account_id}/{asset_id}")
def balance(account_id: str, asset_id: str) -> dict[str, Any]:
    try:
        value = ledger.balance(account_id, asset_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"account_id": account_id, "asset_id": asset_id, "quantity": str(value)}


def _asset(asset: Asset) -> dict[str, Any]:
    return {
        "asset_id": asset.asset_id,
        "symbol": asset.symbol,
        "asset_type": asset.asset_type,
        "decimals": asset.decimals,
        "target_value_eur": None if asset.target_value_eur is None else str(asset.target_value_eur),
        "market_value_eur": None if asset.market_value_eur is None else str(asset.market_value_eur),
        "valuation_status": asset.valuation_status,
    }


def _transaction(tx: Any) -> dict[str, Any]:
    return {
        "transaction_id": tx.transaction_id,
        "asset_id": tx.asset_id,
        "source_account": tx.source_account,
        "destination_account": tx.destination_account,
        "quantity": str(tx.quantity),
        "eur_value": None if tx.eur_value is None else str(tx.eur_value),
        "reference": tx.reference,
        "status": tx.status,
    }
