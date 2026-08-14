# Zoë AI Platform – Architecture Blueprint V1.0
**System:** Z1 Real Estate Command Center
**Date:** 2026-08-14
**Status:** Approved & Finalized

## 1. Executive Summary
This document defines the core architecture of the Zoë AI Platform V1.0. The architecture is built on a 5-pillar foundation that ensures strict separation of identity, permissions, persistent memory, financial data, and security orchestration.

## 2. Platform Architecture Overview

```text
                 ┌─────────────────────┐
                 │   Zoë Identity      │
                 │  "Wer ist Zoë?"     │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │    Tool Contracts   │
                 │ "Was darf Zoë?"     │
                 └──────────┬──────────┘
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
    ┌─────────────────┐          ┌─────────────────┐
    │   Memory Core   │          │     FORTUNA     │
    │ "Was weiß Zoë?" │          │ Finanz-/Marktdaten│
    └────────┬────────┘          └────────┬────────┘
             │                            │
             └──────────────┬─────────────┘
                            ▼
                 ┌─────────────────────┐
                 │       Z1 API        │
                 │ Security + Routing  │
                 │ + Orchestration     │
                 └──────────┬──────────┘
                            │
                            ▼
                      Z1 Android
```

## 3. The 5 Core Pillars

### 3.1. Zoë Identity

**Core Question:** *Wer ist Zoë?*
The immutable source of identity. It describes Zoë as the central coordination intelligence and defines her role, functions, values, and council structure.

**Structure:**

```text
Identity
├── version
├── role
├── functions
├── values
├── network
└── status
```

*Note: Version 1.0 remains immutable and versioned.*

### 3.2. Memory Core

**Core Question:** *Was darf als Wissen von Zoë dauerhaft gespeichert werden?*
The persistent memory layer. It ensures strict ownership and prevents volatile data from polluting the long-term database.

**Lifecycle / Pipeline:**
`Observation` ➔ `Memory Candidate` ➔ `Review / Policy` ➔ `Durable Memory`

**Separation of Concerns:**

* Short-term API data
* Observations
* Candidates
* Confirmed Memories
* Archived Memories

### 3.3. Tool Contracts

**Core Question:** *Was darf Zoë?*
The strict permission and interface layer. Zoë cannot execute arbitrary functions; every action is bound by a contract.

**Contract Schema:**

```text
Tool
├── name
├── permission
├── description
├── input_schema
├── output_schema
└── audit_required
```

*Example (CMC_MARKET_DATA): Requires specific permission (`ZOEUSETOOL_CMC_MARKET_DATA`), defined inputs (asset, quote_currency), and expected outputs.*

### 3.4. FORTUNA

**Core Question:** *Welche Finanz-/Marktdaten stehen zur Verfügung?*
The financial and asset intelligence layer, managing real estate portfolios, gold reserves, and crypto market data.

**Structure:**

```text
FORTUNA
│
├── Portfolio
├── Financial Intelligence
├── Asset Data
└── CryptoMarketData
       │
       └── CoinMarketCap
```

*Security Note: API keys (e.g., COINMARKETCAP_API_KEY) live exclusively in the Backend Secret Store, explicitly separated from Android, Memory, and Tool definitions.*

### 3.5. Z1 API

**Core Question:** *Wer darf was auf welche Weise ausführen?*
The security, routing, and orchestration layer.

**Execution Pipeline:**
`Request` ➔ `JWT` ➔ `Authentication` ➔ `Authorization` ➔ `PolicyEngine` ➔ `Orchestrator` ➔ `Tool / Service` ➔ `Audit` ➔ `Response`

## 4. The Critical Safeguard (Data Flow Isolation)

The Memory Core and FORTUNA must **never** fuse directly.
Live data streams (e.g., a Bitcoin price fluctuation from CoinMarketCap) remain volatile within FORTUNA. They only enter the Memory Core if the `Zoë Analysis` process explicitly deems the movement strategically relevant, generating a `Memory Candidate` that passes policy review.

**Client Integration:**
The Z1 Android Client sits securely on top of the Z1 API, interacting through the Orchestrator to access Zoë, the Memory Core, or FORTUNA.
