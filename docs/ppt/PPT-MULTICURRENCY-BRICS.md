# PPT Multicurrency / BRICS-Compatible Settlement

PPT is designed as a cross-border payment asset that can support settlement quotes in multiple currencies.

## Principle

PPT does not depend on a single fiat rail. Z1 may accept verified FX evidence for a settlement currency and produce a deterministic quote. The current implementation deliberately separates:

- PPT token accounting
- fiat FX quotation
- reserve evidence
- legal tender / payment acceptance
- external settlement rails

## BRICS-compatible rails

The adapter supports configurable currency rails commonly relevant to BRICS-related cross-border settlement. This is an integration label, not a claim that PPT is an official BRICS currency, legal tender, or an endorsed BRICS payment system.

Supported code configuration includes: AED, BRL, CNY, EGP, ETB, IDR, INR, IRR, RUB and ZAR.

## Verification

A currency rate must carry a source and `verified=true` before it can be used for a settlement quote. Unverified rates are rejected.

## Next production gates

1. Connect an approved FX data provider.
2. Persist rate provenance and timestamp in Z1.
3. Add jurisdiction-specific merchant/payment acceptance rules.
4. Define reserve and redemption controls independently of FX quotes.
5. Perform legal/compliance review before describing PPT as a payment instrument or stable-value asset.
