from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import httpx


DEFAULT_BASE_URL = "https://b2b.revolut.com/api/1.0"


@dataclass(frozen=True)
class RevolutAccount:
    id: str
    name: str
    balance: Decimal
    currency: str
    state: str
    updated_at: str | None


class RevolutBusinessClient:
    """READ-only Revolut Business connector for Z1 Treasury/FORTUNA.

    Credentials are read only from runtime environment variables. This client
    never creates payments, transfers, exchanges, or token issuance events.
    """

    def __init__(self, access_token: str | None = None, base_url: str | None = None) -> None:
        self.access_token = access_token or os.getenv("REVOLUT_BUSINESS_ACCESS_TOKEN")
        self.base_url = (base_url or os.getenv("REVOLUT_BUSINESS_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")

    def _headers(self) -> dict[str, str]:
        if not self.access_token:
            raise RuntimeError("REVOLUT_BUSINESS_ACCESS_TOKEN is not configured")
        return {"Authorization": f"Bearer {self.access_token}", "Accept": "application/json"}

    async def list_accounts(self) -> list[RevolutAccount]:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(f"{self.base_url}/accounts", headers=self._headers())
            response.raise_for_status()
            payload: Any = response.json()

        return [
            RevolutAccount(
                id=str(item["id"]),
                name=str(item.get("name", "")),
                balance=Decimal(str(item["balance"])),
                currency=str(item["currency"]),
                state=str(item["state"]),
                updated_at=item.get("updated_at"),
            )
            for item in payload
        ]

    async def eur_balance(self) -> Decimal:
        accounts = await self.list_accounts()
        return sum((a.balance for a in accounts if a.currency == "EUR" and a.state == "active"), Decimal("0"))
