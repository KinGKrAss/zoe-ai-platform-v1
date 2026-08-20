"""CoinMarketCap API v3/v2 connector for ZOE-CORE.

The connector deliberately keeps CMC market data separate from Z1/PPT accounting.
PPT can be represented as an internal asset until a verified CMC listing exists.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping

import requests


DEFAULT_BASE_URL = "https://pro-api.coinmarketcap.com"


class CoinMarketCapError(RuntimeError):
    """Raised when the CoinMarketCap request fails or returns an API error."""


@dataclass(frozen=True)
class CoinMarketCapClient:
    api_key: str | None = None
    base_url: str = DEFAULT_BASE_URL
    timeout: float = 10.0

    def __post_init__(self) -> None:
        key = self.api_key or os.getenv("COINMARKETCAP_API_KEY")
        if not key:
            raise CoinMarketCapError(
                "COINMARKETCAP_API_KEY is not configured."
            )
        object.__setattr__(self, "api_key", key)

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": self.api_key or "",
        }

    def _get(self, path: str, params: Mapping[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}{path}"
        try:
            response = requests.get(
                url, headers=self._headers, params=dict(params), timeout=self.timeout
            )
        except requests.RequestException as exc:
            raise CoinMarketCapError(f"CoinMarketCap request failed: {exc}") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise CoinMarketCapError(
                f"CoinMarketCap returned non-JSON response ({response.status_code})."
            ) from exc

        if not response.ok:
            status = payload.get("status", {})
            message = status.get("error_message") or response.text
            raise CoinMarketCapError(
                f"CoinMarketCap HTTP {response.status_code}: {message}"
            )

        status = payload.get("status", {})
        if status.get("error_code", 0):
            raise CoinMarketCapError(
                f"CoinMarketCap API error {status['error_code']}: "
                f"{status.get('error_message', 'unknown error')}"
            )
        return payload

    def latest_quotes(
        self,
        symbols: list[str] | tuple[str, ...],
        convert: str = "USD",
    ) -> list[dict[str, Any]]:
        """Return latest CMC quotes for symbols such as BTC and ETH."""
        if not symbols:
            return []
        payload = self._get(
            "/v3/cryptocurrency/quotes/latest",
            {"symbol": ",".join(symbols), "convert": convert},
        )
        data = payload.get("data", {})
        return list(data.values()) if isinstance(data, dict) else list(data)

    def historical_quotes(
        self,
        symbol: str,
        time_start: date | str,
        time_end: date | str | None = None,
        convert: str = "USD",
    ) -> list[dict[str, Any]]:
        """Return historical CMC quote observations."""
        params: dict[str, Any] = {
            "symbol": symbol,
            "time_start": str(time_start),
            "convert": convert,
        }
        if time_end is not None:
            params["time_end"] = str(time_end)
        payload = self._get("/v3/cryptocurrency/quotes/historical", params)
        return payload.get("data", {}).get("quotes", [])

    def historical_ohlcv(
        self,
        symbol: str,
        time_start: date | str,
        time_end: date | str | None = None,
        convert: str = "USD",
    ) -> list[dict[str, Any]]:
        """Return historical OHLCV observations."""
        params: dict[str, Any] = {
            "symbol": symbol,
            "time_start": str(time_start),
            "convert": convert,
        }
        if time_end is not None:
            params["time_end"] = str(time_end)
        payload = self._get("/v2/cryptocurrency/ohlcv/historical", params)
        return payload.get("data", {}).get("quotes", [])


DEFAULT_MARKET_ASSETS = ("BTC", "ETH")


def market_assets(client: CoinMarketCapClient) -> list[dict[str, Any]]:
    """Z1-safe default market feed; internal PPT is intentionally not queried."""
    return client.latest_quotes(list(DEFAULT_MARKET_ASSETS))
