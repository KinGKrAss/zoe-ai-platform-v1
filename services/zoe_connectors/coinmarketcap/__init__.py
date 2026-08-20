"""CoinMarketCap connector for ZOE-CORE."""

from .client import CoinMarketCapClient, CoinMarketCapError, market_assets

__all__ = ["CoinMarketCapClient", "CoinMarketCapError", "market_assets"]
