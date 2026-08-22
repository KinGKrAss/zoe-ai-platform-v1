# Preussen Point (PPT) — Technical Tokenomics v1.0

## Status

Technical specification only. This document does **not** constitute a promise of value, reserve backing, redemption, investment return, or a public offer.

## Core parameters

- Name: Preussen Point
- Symbol: PPT
- Standard: ERC-20
- Decimals: 18
- Supply model: role-controlled minting; no implicit fixed maximum in the current contract
- Burn: holder-initiated burn
- Transfer control: pausable
- Mint authority: `MINTER_ROLE`
- Administrative authority: `DEFAULT_ADMIN_ROLE`

## Reference value

The Z1/PPT system may use a configurable EUR reference price for application calculations. A reference price is **not** a guaranteed exchange rate.

A 1 PPT = 1 EUR target may only be represented as a target/reference value until a legally and operationally valid reserve, redemption and verification mechanism exists.

## Reserve model

Reserve snapshots must contain:

- asset identifier
- quantity
- EUR valuation
- source
- verification state

Unverified reserves must not be presented as backing. The API therefore exposes the current reserve state as `unverified` until verified evidence is available.

## Minting policy

Minting should be limited to documented issuance events and recorded with:

1. authorization
2. amount
3. recipient
4. issuance reason
5. reserve/economic evidence where applicable
6. audit timestamp

No automatic minting against unverified assets is permitted by this specification.

## Z1 utility

PPT is intended to function as a payment/accounting unit inside Z1 modules, including merchant payment quotes, payment intents, reserve reporting and FORTUNA/PPT reporting.

## Controls

- Pause transfers during incidents.
- Keep deployment keys outside source control.
- Require explicit production deployment approval.
- Monitor contract address, chain ID, API health and reserve verification state.

## Future 1-EUR mechanism

If a 1-EUR redemption mechanism is implemented, it must specify eligibility, reserve assets, redemption process, fees, settlement timing, insolvency treatment, verification frequency and responsible operator before being described as a stable value mechanism.
