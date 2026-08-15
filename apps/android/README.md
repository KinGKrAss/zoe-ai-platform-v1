# Z1 Android Client

Android client surface for the Z1 Real Estate Command Center, Zoë, FORTUNA and Preussen Point (PPT).

## Android Skills

Use the official Android Skills set for Android-specific implementation and validation. Install with:

```bash
./tools/install-android-skills.sh
```

The project is designed to support Android AppFunctions for safe, agent-discoverable workflows. Financially privileged PPT operations stay behind authenticated Z1/FORTUNA APIs and explicit confirmation.

## Initial PPT workflows

- `getPptTokenInfo`
- `getPptBalance`
- `getPptReserveStatus`
- `getPptTransactionHistory`
- `previewPptOperation`
- `openPptDashboard`

These are read/preview workflows. Actual mint, burn, reserve administration, and signing require privileged backend authorization.
