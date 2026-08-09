# Zoë Council of 33 — Reconstruction V1.0

**System:** Z1 Real Estate Command Center  
**Platform:** Zoë AI Platform  
**Version:** 1.0  
**Status:** Registry implemented; historical reconstruction remains versioned

## Purpose

This document establishes the Council of 33 as a first-class architectural component of Zoë. Zoë is the central AI Queen / orchestrator. The remaining 32 positions are specialist agents that Zoë can delegate work to.

## Provenance policy

The repository distinguishes between:

- **confirmed** — present in the existing Z1/Zoë design or previously established project material;
- **reconstructed** — a best-effort reconstruction from the available project traces;
- **proposed** — a future design choice not yet supported by historical evidence.

No reconstructed identity should be presented as an original historical record without supporting source material.

## Architecture

```text
                         ZOË — GOD-001
                  AI QUEEN / ORCHESTRATOR
                            |
                            v
                    COUNCIL OF 33
                            |
       +--------------------+--------------------+
       |                    |                    |
    Finance              Real Estate          Legal
    Finyra                 Gaia              Jurena
       |                    |                    |
       +--------------------+--------------------+
                            |
                       Z1 / Zoë Core
```

## Runtime contract

Zoë decomposes a user request into specialist tasks. Each task contains the task description, execution context, and effective permissions. A specialist returns a result, confidence score, and source references. Zoë then validates and synthesizes the results.

```text
User request
    -> Zoë intent/context/planning
    -> specialist task(s)
    -> permissioned tools
    -> specialist result(s)
    -> Zoë synthesis
    -> response / report / approved action
```

## Persistence

The registry is persisted through:

- `council_agents` — agent identity and domain metadata;
- `council_agent_tools` — tool permissions;
- `agent_tasks` — delegation and execution history;
- `audit_log` — system-wide action history.

## Next implementation boundary

The registry is now complete enough to freeze the **Council-of-33 contract**. Individual agent implementations remain separate work items and should implement the shared interface rather than inventing independent protocols.
