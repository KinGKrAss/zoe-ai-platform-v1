# Z1 API

Backend boundary for the Z1 Android client.

## Contract

`Android -> Z1 API -> ZOE Identity / Memory Core / FORTUNA -> providers`

The API owns authentication/session handling and authorization. OpenAI and CoinMarketCap credentials are server-side only.

## Development

```bash
cd services/z1-api
pip install -r requirements.txt
uvicorn app.main:app --reload
```

This scaffold deliberately uses a development token. Production authentication must be connected to the repository's user/role/permission model before deployment.
