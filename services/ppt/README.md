# Preussen Point (PPT)

Preussen Point is the digital-point token subsystem for Z1/FORTUNA.

## Canonical flow

`Z1 → Finanzfuchs → PPT Contract → MetaMask → PPT Portal → controlled distribution → liquidity → trading`

The repository restores the original PPT foundation from commit `74f1d80` and extends it with a merchant-payment layer and Serum Regalis partner registry.

## Monetary model

`1 PPT = 1 EUR` is a target/reference only until reserve ownership, custody, valuation, supply, redemption rights and independent attestations are verified. The token contract does not create EUR backing by itself.

## Safety

- role-controlled minting
- pausing
- explicit chain configuration
- no private keys or seed phrases in source
- no automatic minting from market prices
- reserve accounting is separate from token accounting
- merchant acceptance is opt-in and jurisdiction-aware
