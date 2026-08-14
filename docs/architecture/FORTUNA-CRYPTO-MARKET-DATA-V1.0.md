# FORTUNA CryptoMarketData

CryptoMarketData is the FORTUNA integration boundary for CoinMarketCap market data.

## Configuration

Set the API key only in the server environment:

`COINMARKETCAP_API_KEY=<secret>`

Never ship this value to Android, browser JavaScript, or the Git repository.

## Initial contract

- latest cryptocurrency quotes
- latest listings
- global market metrics
- API key / usage information
- normalized persistence in FORTUNA tables
- request telemetry for rate-limit and cost monitoring

The client uses the CoinMarketCap Pro API header `X-CMC_PRO_API_KEY` and keeps the provider-specific transport outside Zoë's reasoning layer.

## Memory Core relationship

Zoë receives normalized market observations through Z1/FORTUNA. Crypto provider credentials and HTTP transport remain outside the Memory Core. Durable memories can store approved analytical observations with owner and embedding metadata.
