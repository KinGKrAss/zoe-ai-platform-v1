#!/usr/bin/env bash
set -euo pipefail

# Install Google's official Android skills into this repository.
# Requires the Android CLI to be installed and available as `android`.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v android >/dev/null 2>&1; then
  echo "ERROR: Android CLI not found. Install it first:"
  echo "https://developer.android.com/tools/agents/android-cli"
  exit 1
fi

android skills add --all --project="$ROOT_DIR"
echo "Android skills installed for the Z1/Zoë project."
