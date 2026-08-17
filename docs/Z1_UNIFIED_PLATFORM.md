# Z1 Unified Platform — PPT System Consolidation

## Purpose
Consolidate the agreed components under one Z1 platform instead of separate apps:

`Z1 → Finanzfuchs → PPT Contract → MetaMask → PPT Portal → controlled distribution → liquidity → trading`

## Platform modules
1. **Z1 Core** — orchestration, registry, evidence and audit.
2. **FORTUNA / Finanzfuchs** — financial intelligence, reserve/supply coverage, risk and monitoring.
3. **PPT** — existing Preussen Point contract and token services; do not create a second PPT contract until the historical contract identity has been verified.
4. **Wallet** — MetaMask-compatible DApp connection; signing remains in the user's wallet.
5. **PPT Portal** — unified UI for balances, payment requests, merchant flow and evidence.
6. **Merchant layer** — QR/payment intents and settlement records.
7. **Serum Regalis** — separate regulated product/partner module; Nobody's Place (Venlo) remains a candidate partner, not a confirmed relationship.
8. **Market layer** — controlled distribution, price discovery, liquidity and trading after gates pass.

## Security boundaries
- Z1, Finanzfuchs and the portal never accept or store seed phrases/private keys.
- Mainnet minting requires verified contract identity, owner/role review and supply controls.
- Reserve-backed value claims require evidence for ownership, custody, quantity, valuation, supply reconciliation and applicable redemption terms.
- `1 PPT = 1 EUR` is a target/reference until independently supported; it is not asserted as a guaranteed market value.

## Live platform target
The portal is designed as the single user-facing surface. Backend APIs remain modular behind it so the platform can evolve without fragmenting the user experience.
