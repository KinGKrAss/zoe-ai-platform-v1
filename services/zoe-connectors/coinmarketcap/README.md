# CoinMarketCap Connector

ZOE-CORE connector for CoinMarketCap market data.

## Endpoints

- `GET /v3/cryptocurrency/quotes/latest` — live cryptocurrency quotes
- `GET /v3/cryptocurrency/quotes/historical` — historical quote observations
- `GET /v2/cryptocurrency/ohlcv/historical` — historical OHLCV data

## Configuration

Set the API key outside source control:

```bash
export COINMARKETCAP_API_KEY="<your-key>"
```

The connector never stores or logs the key. Production deployments should inject it through the platform's secret manager.

## Z1/PPT boundary

BTC and ETH are the default external market feed. PPT is **not** assumed to be a CoinMarketCap-listed token. Until a verified CMC listing/identifier is configured, PPT remains an internal Z1 asset and its internal accounting/reference value must not be replaced by CMC market data.

## Example

```python
from services.zoe-connectors.coinmarketcap import CoinMarketCapClient

client = CoinMarketCapClient()
quotes = client.latest_quotes(["BTC", "ETH"], convert="USD")
```

For EUR dashboard presentation, request `convert="EUR"` or perform a controlled internal FX conversion rather than mixing currencies implicitly.
