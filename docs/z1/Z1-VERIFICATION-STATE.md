# Z1 Verification State

## Purpose

The Z1 Control Plane owns verification truth. Command Center renders the state but cannot assign it.

## Status contract

| State | UI | Meaning |
|---|---|---|
| VERIFIED | 🟢 | Every required verification check passed |
| PENDING | 🟡 | Evidence is incomplete or still being checked |
| FAILED | 🔴 | At least one required check failed |
| BLOCKED | ⛔ | Entity is explicitly blocked by policy |

## Green-state rule

`VERIFIED` is derived only when **all required checks are PASS**. A balance, explorer label, user assertion, or UI action alone can never create a green state.

## Blockchain checks

The initial required checks are:

1. address format
2. supported chain
3. address type (EOA/contract)
4. RPC readability
5. transaction history
6. token state
7. ownership evidence when ownership is asserted
8. audit record

PPT/Z1 attribution is a separate evidence claim. It must never be inferred merely because an address exists or holds tokens.

## Address lifecycle

`UNVERIFIED_EXTERNAL_ADDRESS` is represented operationally as `PENDING` until the verification engine has produced evidence. A successful run persists check evidence, source, timestamp and audit information; the derived view then exposes `VERIFIED`.

## UI contract

The Command Center must read `derived_status` from `z1_verification_state`. It must not maintain a second status truth in frontend state.
