---
name: ppt-android-appfunctions
description: Z1/PPT Android AppFunctions policy and implementation guidance layered on Google's official Android Skills.
license: Project-local
metadata:
  upstream: https://github.com/android/skills/tree/main/device-ai/appfunctions
---

# PPT Android AppFunctions

Use Google's official `appfunctions` skill as the technical source of truth, then apply these Z1/PPT constraints.

## Safe functions

Prefer read-only or preview operations:

- `getPptTokenInfo`
- `getPptBalance`
- `getPptReserveStatus`
- `getPptTransactionHistory`
- `previewPptOperation`
- `openPptDashboard`

## Financial security

Never expose private keys, seed phrases, wallet signing material, reserve credentials, or administrative secrets through AppFunctions or agent-visible metadata.

Do not implement autonomous minting, burning, reserve movement, or transaction signing. Such actions must cross the authenticated Z1/FORTUNA backend boundary and require explicit user confirmation.

## Android target

When implementing AppFunctions, follow the current upstream Android guidance rather than hard-coding stale dependency versions. The upstream skill currently specifies Android 16-era AppFunctions requirements and recommends the Jetpack compatibility layer.

## Validation

After implementation:

1. Build the Android client.
2. Register AppFunctions.
3. Inspect registration on a test device/emulator.
4. Invoke read-only functions with ADB tooling.
5. Confirm that privileged PPT operations cannot be invoked without backend authorization.
