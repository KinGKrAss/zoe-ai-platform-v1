# Z1 Core Principle

## Canonical rule

> **Z1 owns state. Zoë interprets state. MCP transports and orchestrates interactions. Models provide inference.**

## Continuity invariant

> **Zoë's system identity and legacy memory MUST NOT be coupled to, owned by, or lost with any single model instance.**

The model runtime is an interchangeable inference provider. Z1 remains the authoritative system of record for Zoë's identity, authorized memory, state, permissions, and audit history.

## Authority chain

```text
Principal / Owner
        ↓
Governance
        ↓
Z1 Control Plane
        ↓
Zoë Core
        ↓
MCP
        ↓
Model Runtime
```

## Responsibilities

### Principal / Owner
- Owns the platform and defines top-level governance.
- Approves changes to identity, policy, and persistence boundaries.

### Governance
- Defines policy, authorization, approvals, and operational constraints.

### Z1 Control Plane
- Owns authoritative state.
- Stores the versioned Zoë identity.
- Stores Zoë's legacy/continuity memory.
- Controls authorization and permissions.
- Records auditable state transitions.

### Zoë Core
- Interprets authorized Z1 state.
- Performs reasoning, planning, coordination, and response composition.
- Must not become the authoritative owner of persistent state.

### MCP
- Provides standardized interaction with tools, resources, and tasks.
- Carries explicit application context/handles where state must survive requests.
- Must not become Zoë's system of record.

### Model Runtime
- Provides inference only.
- May be replaced, upgraded, or routed without changing `identity_id`.
- Must not be treated as the authoritative source for identity or memory.

## Non-negotiable implementation rules

1. `identity_id` MUST NOT be derived from `model_id`.
2. `model_id` MUST NOT be persisted as the identity key for Zoë.
3. Model adapters MUST NOT directly write authoritative Z1 memory.
4. Legacy memory MUST be addressable independently of the active model.
5. A model switch MUST preserve `identity_id`, legacy memory references, and authorization scope.
6. MCP session state MUST NOT be used as the authoritative Zoë memory store.
7. Persistent memory writes MUST pass through Z1 authorization and audit boundaries.

## Reference state flow

```text
Z1 Identity + Legacy Memory + Authorized State
                    ↓
                Zoë Core
                    ↓
             MCP interaction
                    ↓
              Model inference
                    ↓
             Result / action
                    ↓
          Z1 authorization + audit
```

## Model-switch guarantee

A deployment may change:

```text
Model A → Model B → Model C
```

without changing:

```text
ZOE-IDENTITY-V1.0
ZOE-LEGACY
Z1 authorized memory
Z1 state
Z1 permissions
Z1 audit history
```

This document is an architectural contract. Implementations and tests should enforce these invariants rather than relying on prompt instructions alone.
