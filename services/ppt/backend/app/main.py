from __future__ import annotations

import os
from decimal import Decimal
from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .multicurrency import CurrencyRate, CurrencyRegistry, BRICS_CURRENCY_CODES

app = FastAPI(title="Preussen Point API", version="2.0.0")
TOKEN_NAME = "Preussen Point"
TOKEN_SYMBOL = "PPT"
TOKEN_DECIMALS = 18

class ReserveSnapshot(BaseModel):
    asset: str
    quantity: Decimal = Field(ge=0)
    valuation_eur: Decimal = Field(ge=0)
    source: str
    verified: bool = False

class PaymentQuote(BaseModel):
    merchant_id: str = Field(min_length=1)
    amount_eur: Decimal = Field(gt=0)
    ppt_per_eur: Decimal = Field(gt=0)

class MultiCurrencyQuote(BaseModel):
    merchant_id: str = Field(min_length=1)
    amount_eur: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    units_per_eur: Decimal = Field(gt=0)
    rate_source: str = Field(min_length=1)
    rate_verified: bool = False

class PaymentIntent(BaseModel):
    merchant_id: str
    amount_ppt: Decimal = Field(gt=0)
    chain_id: int
    token_contract: str
    recipient: str
    status: Literal["created", "awaiting_signature", "submitted", "confirmed", "rejected"] = "created"

class Merchant(BaseModel):
    merchant_id: str
    name: str
    country: str
    accepts_ppt: bool = False
    product_scope: list[str] = []
    jurisdiction_review: Literal["pending", "approved", "rejected"] = "pending"

_currency_registry = CurrencyRegistry()

@app.get("/health")
def health():
    return {"status": "ok", "service": "ppt", "version": "2.0.0"}

@app.get("/v1/token")
def token():
    return {"name": TOKEN_NAME, "symbol": TOKEN_SYMBOL, "decimals": TOKEN_DECIMALS,
            "chain_id": os.getenv("PPT_CHAIN_ID"), "contract_address": os.getenv("PPT_CONTRACT_ADDRESS")}

@app.get("/v1/reserves")
def reserves():
    return {"status": "unverified", "snapshots": []}

@app.post("/v1/reserves/preview")
def reserve_preview(snapshot: ReserveSnapshot):
    if not snapshot.verified:
        raise HTTPException(status_code=409, detail="Reserve snapshot is not verified")
    return {"status": "accepted-for-review", "snapshot": snapshot.model_dump()}

@app.get("/v1/z1/summary")
def z1_summary():
    return {"module": "FORTUNA/PPT", "token": TOKEN_SYMBOL,
            "canonical_uri": "z1://ppt/token/PPT", "minting": "manual-role-controlled",
            "reserve_status": "unverified"}

@app.post("/v1/payments/quote")
def quote(request: PaymentQuote):
    return {"merchant_id": request.merchant_id, "amount_eur": str(request.amount_eur),
            "amount_ppt": str(request.amount_eur * request.ppt_per_eur),
            "price_basis": "configured_reference"}

@app.post("/v1/payments/quote/multicurrency")
def multicurrency_quote(request: MultiCurrencyQuote):
    rate = CurrencyRate(code=request.currency.upper(), units_per_eur=request.units_per_eur,
                        source=request.rate_source, verified=request.rate_verified)
    _currency_registry.register(rate)
    try:
        amount = _currency_registry.quote_from_eur(request.amount_eur, request.currency)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"merchant_id": request.merchant_id, "currency": request.currency.upper(),
            "amount_eur": str(request.amount_eur), "settlement_amount": str(amount),
            "rate_source": request.rate_source, "rate_verified": True,
            "rail_group": "brics-compatible" if request.currency.upper() in BRICS_CURRENCY_CODES else "standard"}

@app.get("/v1/payments/currencies")
def currencies():
    return {"verified_currencies": _currency_registry.supported(),
            "configured_brics_compatible_codes": list(BRICS_CURRENCY_CODES)}

@app.post("/v1/payments/intents")
def payment_intent(intent: PaymentIntent):
    if not intent.recipient.startswith("0x"):
        raise HTTPException(status_code=400, detail="Recipient must be a configured blockchain address")
    return {"status": "awaiting_signature", "intent": intent.model_copy(update={"status": "awaiting_signature"}).model_dump()}

_MERCHANTS: dict[str, Merchant] = {}

@app.post("/v1/merchants")
def register_merchant(merchant: Merchant):
    _MERCHANTS[merchant.merchant_id] = merchant
    return {"status": "registered-for-review", "merchant": merchant.model_dump()}

@app.get("/v1/merchants")
def merchants():
    return {"merchants": list(_MERCHANTS.values())}
