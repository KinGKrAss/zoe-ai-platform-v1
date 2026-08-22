# PPT ↔ Z1 Interface Contract

## Canonical identity

- Token symbol: `PPT`
- Canonical URI: `z1://ppt/token/PPT`
- Z1 reporting module: `FORTUNA/PPT`

## API surface

- `GET /health` — service health
- `GET /v1/token` — token metadata and configured chain/contract identity
- `GET /v1/reserves` — reserve verification state
- `POST /v1/reserves/preview` — submit a reserve snapshot for review; unverified snapshots are rejected
- `GET /v1/z1/summary` — Z1-facing PPT status summary
- `POST /v1/payments/quote` — calculate a configured reference quote
- `POST /v1/payments/intents` — create a payment intent awaiting signature
- `POST /v1/merchants` / `GET /v1/merchants` — merchant registration and review state

## Safety invariants

1. API reference pricing is not a redemption guarantee.
2. Unverified reserves are never represented as verified backing.
3. Payment intents require an explicit blockchain recipient address.
4. Production contract deployment requires manual authorization.
5. Deployment credentials remain in CI secrets and are never committed.
