# PPT Live Readiness Checklist

## Gate 1 — Backend/API

- [ ] `/health` returns HTTP 200
- [ ] `/v1/token` exposes correct PPT metadata
- [ ] `/v1/reserves` reports verification state
- [ ] unverified reserve submissions are rejected
- [ ] Z1 summary exposes canonical PPT URI

## Gate 2 — CI

- [ ] PPT CI green
- [ ] Z1 CI green
- [ ] no unresolved import/package errors
- [ ] contract compilation green

## Gate 3 — Production configuration

Required GitHub Environment `production` secrets:

- `PPT_ADMIN_ADDRESS`
- `PPT_DEPLOYER_PRIVATE_KEY`
- `PPT_RPC_URL`

The deployment workflow is manually triggered and requires the exact confirmation string `DEPLOY-PPT`.

## Gate 4 — Economic controls

- [ ] tokenomics specification approved
- [ ] reserve policy defined
- [ ] 1-EUR reference/redemption mechanism legally and operationally defined before any value claim
- [ ] issuance authorization and audit trail defined

## Gate 5 — Live smoke test

After deployment, verify contract address, chain ID, token metadata, API health and Z1 summary. Record the deployment transaction and contract address in the release record.
