# Android Skills Integration — Z1 / Zoë / PPT

This repository integrates Google's official Android Skills workflow into the Z1 platform.

## Upstream

- Repository: https://github.com/android/skills
- Android skills documentation: https://developer.android.com/tools/agents/android-skills
- Android CLI documentation: https://developer.android.com/tools/agents/android-cli

The upstream repository describes Android Skills as modular, AI-optimized `SKILL.md` instructions following the open Agent Skills standard. It supports installing one skill or the complete set through the Android CLI.

## Installation

From the repository root:

```bash
./tools/install-android-skills.sh
```

Equivalent Android CLI command:

```bash
android skills add --all --project=.
```

## Z1 integration policy

Android is the client layer for Z1. Zoë remains the orchestration/intelligence layer and FORTUNA remains the financial control layer.

```text
Android / Z1 UI
      │
      ├── official Android Skills
      │
      ├── read-only device capabilities
      │
      └── authenticated API calls
             │
             ▼
          Z1 Core
             │
       ┌─────┴─────┐
       ▼           ▼
     Zoë        FORTUNA
                   │
                   ▼
                  PPT
```

### Security boundary

Do not expose private keys, seed phrases, signing credentials, reserve credentials, or privileged financial operations through Android UI metadata, logs, AppFunctions, or agent-discoverable functions.

AppFunctions should initially expose safe workflows such as:

- view PPT balance
- view PPT token metadata
- view reserve status
- view transaction history
- request a quote/preview
- open the PPT/FORTUNA dashboard

Privileged operations such as minting, burning, reserve administration, or signing must require backend authorization and explicit confirmation.

## Included local skill adapter

`.agents/skills/android-cli/SKILL.md` provides the Z1-specific policy layer while keeping Google's official Android Skills repository as the upstream source of Android-specific technical guidance.

## License

Google's Android Skills repository is Apache-2.0 licensed. This repository does not claim ownership of Google's upstream material.
