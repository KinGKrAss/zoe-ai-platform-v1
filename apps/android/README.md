# Zoë / Z1 Android client

The Android app is a client-only adapter for Z1.

## Architecture

`Android → Z1 API → internal Z1 services`

The Android client must not access PostgreSQL directly and must not contain provider or model API secrets.

## Local build

Use Java 17, Android SDK 35 and Gradle 8.9:

```bash
gradle -p apps/android assembleDebug
```

For a connected Z1 API, pass the HTTPS endpoint as a Gradle property:

```bash
gradle -p apps/android -PZ1_API_BASE_URL=https://your-z1-host assembleDebug
```

The app rejects non-HTTPS Z1 API endpoints.

## Session credentials

Session tokens are stored using an AES-GCM key held by the Android Keystore. The app does not put credentials into source code or the Android manifest.
