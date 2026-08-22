# Revolut Business → PPT Treasury Setup

The connector uses the Revolut Business API in **read-only** mode. Revolut's Business API exposes account balances through `GET /accounts`; authentication uses a bearer access token. citeturn0search0turn0search2

## Required runtime secret

`REVOLUT_BUSINESS_ACCESS_TOKEN`

Store this only in the deployment environment/secret manager. Never commit it to Git.

## Optional configuration

`REVOLUT_BUSINESS_BASE_URL`

Defaults to the official Business API base URL.

## Authorization

For production, create/authorize the Business API application in Revolut Business, generate the required certificate/client assertion flow, and obtain the access token. Revolut documents this setup and warns that access and refresh tokens provide access to banking data and must not be shared. citeturn0search1turn0search0

Use the minimum required permission: `READ` for account balance retrieval. Do not grant `WRITE` or `PAY` to this connector. citeturn0search0

## Data flow

`Revolut Business /accounts → RevolutBusinessClient → verified treasury process → TreasuryLedger → Z1/FORTUNA`

The connector does **not** mint PPT and does not initiate payments, transfers or currency exchanges.

## Production verification gate

1. Configure the secret in the production environment.
2. Authenticate the Revolut Business application.
3. Retrieve accounts through `/accounts`.
4. Confirm active EUR accounts and balances.
5. Record source, timestamp and verification evidence in the Treasury Ledger.
6. Only then expose the verified reserve to Z1/FORTUNA.

A Revolut balance is evidence of an account balance; it is not by itself a legal promise that 1 PPT is redeemable for EUR 1.
