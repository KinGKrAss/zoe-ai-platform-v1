# Z1 Runtime Foundation V1.0

## Purpose

This document defines the executable boundary between Z1 Identity, Governance,
MemoryCore and the Wealth Registry.

## Core principle

> Protect what is important, but never claim safety, ownership, truth or
> verification unless the applicable evidence and authorization checks pass.

## Runtime flow

```text
API -> Z1 Core Runtime -> Governance -> MemoryCore -> Wealth Registry -> Audit
```

## Verification states

- `USER_REPORTED`: supplied by an actor, not independently verified.
- `UNVERIFIED`: known to the system but lacking sufficient evidence.
- `VERIFIED`: evidence and authorization requirements have passed.
- `DERIVED`: calculated from other trusted records.
- `CONFLICT`: evidence or source records disagree.

`VERIFIED` is a controlled state transition. It must never be inferred merely
from a user statement or model output.

## Database foundation

Migration `011_create_z1_runtime_foundation.sql` aligns the existing MemoryCore
schema with the runtime contracts and establishes runtime component state.

The migration is additive and therefore preserves existing data while adding
owner, canonical identity, provenance, verification and promotion links.
