# Z1 Green Status Engine

## Purpose

The Z1 Control Plane owns verification state. The Command Center only renders that state.
The UI MUST NOT manufacture a green status.

## Status model

- `VERIFIED` -> 🟢 green
- `PENDING` -> 🟡 yellow
- `INVALID` -> 🔴 red
- `BLOCKED` -> 🔴 red

## Verification contract

An entity becomes `VERIFIED` only when every required check for its entity type passes.
A failed or missing required check keeps the entity `PENDING`, unless the verifier explicitly classifies it as `INVALID` or `BLOCKED`.

For EVM addresses the initial required checks are:

1. `ADDRESS_FORMAT`
2. `CHAIN_SUPPORTED`
3. `ADDRESS_TYPE`
4. `RPC_READ`
5. `BALANCE_READ`
6. `TRANSACTION_READ`
7. `TOKEN_STATE_READ`

Additional checks are conditional:

- `CONTRACT_CODE` for contracts
- `CONTRACT_CREATOR` for contracts when attribution is requested
- `OWNERSHIP_EVIDENCE` only when ownership is claimed
- `PPT_INTERACTION` only when PPT attribution is claimed

## State transition

```text
PENDING -> VERIFIED   all required checks pass
PENDING -> INVALID    verifier proves invalidity
PENDING -> BLOCKED    policy/audit block
VERIFIED -> PENDING   required evidence becomes stale or unavailable
VERIFIED -> INVALID   later verification proves invalidity
```

Every transition must be accompanied by timestamped evidence and an audit event.

## Example

`0x3c3b473565482292f024371f3ce1b021d6877545` must initially be registered as
`UNVERIFIED_EXTERNAL_ADDRESS` / `PENDING`. It may become `VERIFIED` only after the
configured EVM checks have actually succeeded. No balance or ownership is inferred merely
from the presence of an address string.

## Security invariant

A green UI indicator is a projection of authoritative Control Plane state, never an input to it.
