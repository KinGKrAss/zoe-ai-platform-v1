"""FORTUNA schemas for international property and PPT/MIDAS reporting."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


CustodyType = Literal["bank", "custodian", "onchain_wallet", "other"]
AssetClass = Literal["fiat_pool", "crypto_asset", "token", "yield_accrual", "other"]


class InternationalPropertyCreate(BaseModel):
    """Submitted property and valuation information; not an ownership verification."""

    model_config = ConfigDict(extra="forbid")

    property_name: str = Field(min_length=1, max_length=255)
    country_code: str = Field(pattern=r"^[A-Za-z]{2}$")
    legal_entity: str = Field(min_length=1, max_length=255)
    local_tax_id: str | None = Field(default=None, max_length=100)
    valuation_local_currency: Decimal = Field(ge=0, max_digits=28, decimal_places=8)
    currency_code: str = Field(pattern=r"^[A-Za-z]{3}$")
    valuation_eur: Decimal | None = Field(default=None, ge=0, max_digits=28, decimal_places=8)
    fx_rate_to_eur: Decimal | None = Field(default=None, gt=0, max_digits=28, decimal_places=12)
    fx_source: str | None = Field(default=None, max_length=255)
    ownership_share_percent: Decimal = Field(
        default=Decimal("100"), ge=0, le=100, max_digits=7, decimal_places=4
    )
    reporting_date: date
    evidence_reference: str | None = Field(default=None, max_length=2000)
    document_hash: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    storage_key: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{1,128}$")

    @field_validator("country_code", "currency_code", mode="before")
    @classmethod
    def normalize_codes(cls, value: str) -> str:
        return value.upper()

    @model_validator(mode="after")
    def validate_fx_fields(self) -> "InternationalPropertyCreate":
        if self.valuation_eur is None:
            if self.fx_rate_to_eur is not None or self.fx_source is not None:
                raise ValueError("FX rate and source require valuation_eur")
        elif self.currency_code == "EUR":
            if self.valuation_eur != self.valuation_local_currency:
                raise ValueError("EUR valuation must equal the local-currency valuation")
            if self.fx_rate_to_eur is not None or self.fx_source is not None:
                raise ValueError("FX fields are not used for EUR valuations")
        elif self.fx_rate_to_eur is None or not self.fx_source:
            raise ValueError("Non-EUR valuation_eur requires an FX rate and source")
        return self


class InternationalPropertyResponse(InternationalPropertyCreate):
    id: UUID
    record_status: Literal["SUBMITTED"] = "SUBMITTED"
    created_by: str
    created_at: datetime


class PPTMidasEntryCreate(BaseModel):
    """Submitted pool/custody balance; no verification state is client writable."""

    model_config = ConfigDict(extra="forbid")

    custody_type: CustodyType
    custody_reference: str = Field(
        min_length=1,
        max_length=255,
        description="Opaque internal reference; do not enter full IBANs, credentials, or API keys.",
    )
    public_wallet_address: str | None = Field(default=None, max_length=255)
    asset_class: AssetClass
    chain_id: str | None = Field(default=None, max_length=120)
    reporting_date: date
    balance_nominal: Decimal = Field(ge=0, max_digits=32, decimal_places=12)
    currency_code: str = Field(pattern=r"^[A-Za-z]{3}$")
    q1_return_nominal: Decimal | None = Field(default=None, max_digits=32, decimal_places=12)
    q1_period_start: date | None = None
    q1_period_end: date | None = None
    evidence_reference: str | None = Field(default=None, max_length=2000)
    document_hash: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    storage_key: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{1,128}$")
    transaction_reference: str | None = Field(default=None, max_length=255)
    audit_notes: str | None = Field(default=None, max_length=2000)

    @field_validator("currency_code", mode="before")
    @classmethod
    def normalize_currency_code(cls, value: str) -> str:
        return value.upper()

    @model_validator(mode="after")
    def validate_custody_and_period(self) -> "PPTMidasEntryCreate":
        if self.custody_type == "onchain_wallet" and not (self.chain_id and self.public_wallet_address):
            raise ValueError("On-chain entries require chain_id and public_wallet_address")
        q1_values = (self.q1_return_nominal, self.q1_period_start, self.q1_period_end)
        if any(value is not None for value in q1_values) and not all(
            value is not None for value in q1_values
        ):
            raise ValueError("Q1 return requires amount, period start, and period end")
        if self.q1_period_start and self.q1_period_end and self.q1_period_end < self.q1_period_start:
            raise ValueError("Q1 period end must be on or after its start")
        return self


class PPTMidasEntryResponse(PPTMidasEntryCreate):
    id: UUID
    verification_status: Literal["SUBMITTED"] = "SUBMITTED"
    created_by: str
    created_at: datetime
