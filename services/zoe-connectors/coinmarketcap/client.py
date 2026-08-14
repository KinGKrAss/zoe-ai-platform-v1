"""Minimal CoinMarketCap Pro API client for FORTUNA CryptoMarketData.

The API key is read only from COINMARKETCAP_API_KEY and is never accepted as
part of a public application request.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = "https://pro-api.coinmarketcap.com"


class CoinMarketCapError(RuntimeError):
    """Raised when CMC cannot satisfy a request."""


@dataclass(frozen=True)
class CMCResponse:
    status_code: int
    data: dict


class CoinMarketCapClient:
    def __init__(self, api_key: str | None = None, base_url: str = BASE_URL, timeout: float = 15.0):
        self.api_key = api_key or os.environ.get("COINMARKETCAP_API_KEY")
        if not self.api_key:
            raise ValueError("COINMARKETCAP_API_KEY is required")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(self, path: str, params: dict[str, str | int | float] | None = None) -> CMCResponse:
        query = ""
        if params:
            from urllib.parse import urlencode
            query = "?" + urlencode(params)
        request = Request(
            f"{self.base_url}/{path.lstrip('/')}{query}",
            headers={
                "Accept": "application/json",
                "X-CMC_PRO_API_KEY": self.api_key,
                "User-Agent": "Z1-FORTUNA-CryptoMarketData/1.0",
            },
            method="GET",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return CMCResponse(response.status, payload)
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise CoinMarketCapError(f"CMC HTTP {exc.code}: {body[:500]}") from exc
        except URLError as exc:
            raise CoinMarketCapError(f"CMC network error: {exc.reason}") from exc

    def quotes_latest(self, symbols: list[str], convert: str = "USD") -> CMCResponse:
        return self.get("v2/cryptocurrency/quotes/latest", {"symbol": ",".join(symbols), "convert": convert})

    def listings_latest(self, limit: int = 100, convert: str = "USD") -> CMCResponse:
        return self.get("v1/cryptocurrency/listings/latest", {"limit": limit, "convert": convert})

    def global_metrics(self, convert: str = "USD") -> CMCResponse:
        return self.get("v1/global-metrics/quotes/latest", {"convert": convert})

    def key_info(self) -> CMCResponse:
        return self.get("v1/key/info")
