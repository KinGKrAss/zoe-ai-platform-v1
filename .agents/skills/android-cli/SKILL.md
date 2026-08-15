---
name: android-cli
description: Android CLI integration for Z1/Zoë Android development, device testing, SDK management, documentation lookup, and installation of official Android skills.
license: Apache-2.0; see android/skills LICENSE.txt
metadata:
  source: https://github.com/android/skills/tree/main/devtools/android-cli
  maintainer: Google LLC
---

# Android CLI integration for Z1

Use the official Android CLI for Android project creation, SDK management, emulator/device interaction, APK installation, UI layout inspection, screenshots, documentation lookup, and Android skill management.

## Required workflow

1. Prefer `android docs` for current Android API/library guidance.
2. Use `android describe` before manipulating an unfamiliar Android project.
3. Use `android run` for build/deploy/launch validation.
4. Use `android layout` and `android screen` for UI debugging.
5. Use `android skills add --all --project=.` to install the official Android skill set into this repository when the environment supports it.
6. Never place secrets, wallet keys, seed phrases, or financial credentials in Android source, resources, logs, or AppFunctions.

## Z1/PPT application boundary

The Android client is a presentation and controlled-action surface for Z1. PPT signing, minting, burning, reserve administration, and other privileged financial operations must remain behind authenticated backend APIs and explicit user confirmation. Android AppFunctions may expose read-only or low-risk workflows, but must not silently authorize destructive or financial actions.

## Official source

https://github.com/android/skills/tree/main/devtools/android-cli
