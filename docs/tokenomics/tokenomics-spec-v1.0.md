# Tokenomics Spec v1.0 (PPT)

## Status

This specification defines technical policy controls for PPT. It does **not** claim that EUR-fiat is held on-chain. Reserve custody and reconciliation remain off-chain and must be independently verified.

## Core policy

- Token: Preussen Point (PPT), 18 decimals
- Supply starts at 0
- Role-controlled minting and burn
- Pause/emergency controls are mandatory

## Reserve & reconciliation

- Reserve ledger unit: EUR cent (integer)
- Off-chain reconciliation is required between reserve ledger and on-chain supply
- Unverified reserve snapshots must not be presented as collateral backing

## Economic safety

- Minimum collateral ratio must be enforced by policy gates
- Daily mint/redeem limits must be configured in basis points
- Replay and idempotency protection are required for economically effective API writes

## Integrity enforcement

`parameters-v1.0.yaml` is protected by:

1. SHA256 checksum file (`parameters-v1.0.sha256`)
2. Ed25519 detached signature (`parameters-v1.0.sig`)
3. Ed25519 public key file (`parameters-v1.0.pub`)

Signature format:

- `parameters-v1.0.sig`: Base64-encoded detached signature of the **raw YAML bytes**
- `parameters-v1.0.pub`: Base64-encoded 32-byte Ed25519 public key

When integrity enforcement is enabled, startup is fail-closed if validation fails.
