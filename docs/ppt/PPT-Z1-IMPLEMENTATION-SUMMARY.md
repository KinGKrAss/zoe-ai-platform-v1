# Preussen Point / Z1 — implementation summary

## Agreed system concept

The last three hours converged on one operating chain:

`Z1 → Finanzfuchs → PPT Contract → MetaMask → PPT Portal → controlled distribution → liquidity → trading`

### Z1
System core and canonical registry. PPT identity is exposed as:

`z1://ppt/token/PPT`

Z1 stores the configured chain, contract address, evidence state, audit state and merchant/payment references.

### Finanzfuchs / FORTUNA
Financial-intelligence layer. It monitors supply, reserve evidence, wallets, cashflow, liquidity and risk. It never receives seed phrases/private keys and never mints directly.

### PPT Contract
Restored from the historical Preussen Point foundation commit `74f1d80`. The contract is ERC-20, role-controlled for minting, pausable and burnable. No reserve or EUR value is encoded as a false on-chain guarantee.

### MetaMask
Wallet/DApp signing layer. The portal requests a wallet connection and submits ERC-20 transfers through the user's wallet. Private keys remain in the wallet.

### PPT Portal
Merchant/user surface for wallet connection, configured token address, transfers, payment intents and future buy/distribution flows.

### Controlled distribution
Minting is role-controlled. Production distribution must use explicit governance, reserve/redemption controls and audited parameters. No automatic minting from market prices.

### Liquidity / trading
A future public market can be connected after the token, reserve model, legal classification and distribution controls are verified. A DEX/launchpad is an execution venue, not proof of reserve value.

## Serum Regalis

Serum Regalis is modeled as a separate regulated health-products domain under Z1. Product, batch, supplier, pharmacy/specialist-retail and jurisdiction-review records belong here.

`Nobody's Place — Venlo, NL` is stored only as a candidate partner. The repository does not assert an existing partnership, ownership relationship, product authorization or PPT acceptance.

## Value policy

The historical target/reference `1 PPT = 1 EUR` is preserved as a design target, not as a factual guarantee. A fixed or stable value requires independently verifiable reserve assets, ownership, custody, valuation, supply reconciliation, redemption rights and governance.

## Safety policy

Never place private keys, seed phrases or wallet JSON files in the repository or application logs. Real mainnet minting is intentionally blocked until deployment identity, chain, contract address, reserve evidence and governance are verified.
