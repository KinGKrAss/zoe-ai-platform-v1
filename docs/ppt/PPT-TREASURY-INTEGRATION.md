# PPT Treasury ↔ Z1 FORTUNA Integration

## Architecture

`Authorized financial connector → TreasuryLedger → verified reserve snapshot → Z1/FORTUNA → PPT reporting`

The ledger is an accounting/integration layer. It is not a bank connection and it does not mint PPT.

## Reserve states

- `unverified`: external evidence has not been validated; cannot be treated as backing.
- `verified`: authorized source and verification process have accepted the snapshot.

## Required connector contract

An external finance connector should provide:

- source identifier
- asset/currency
- quantity
- valuation currency (EUR for PPT reporting)
- valuation timestamp
- evidence/reference ID
- verification status

Credentials must remain in GitHub Environment/Secret storage or the external connector; never commit credentials to source control.

## PPT issuance control

The treasury ledger is intentionally decoupled from minting. A verified reserve does not automatically create or mint PPT. Any issuance must pass the project's explicit authorization, tokenomics and compliance gates.

## Z1/FORTUNA use

Z1 may consume the verified reserve summary for dashboards, reconciliation and reporting. It must preserve source, timestamp and verification status so that reserve figures remain auditable.

## 1-EUR target

A reserve balance can support a future redemption model, but the presence of a balance in this ledger is not itself a guarantee that 1 PPT can be redeemed for EUR 1. Such a mechanism requires separate operational, legal and liquidity controls.
