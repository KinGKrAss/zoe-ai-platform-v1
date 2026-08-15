# Z1 Biometric Identity & Security V1.0

## Purpose

Z1 may integrate biometric authentication, but biometric material is treated as highly sensitive identity data and is **not** part of ordinary Zoë MemoryCore storage.

## Security principles

1. **Deny by default** — biometric operations are disabled unless explicitly enabled by policy.
2. **Purpose limitation** — an approved biometric operation must declare its purpose.
3. **Explicit consent** — consent is required by default.
4. **No raw samples** — Z1 must not persist raw face, fingerprint, iris, or voice samples in MemoryCore or the ordinary Z1 database.
5. **External authenticator preferred** — use OS/platform authentication or a dedicated identity provider and retain only the minimum credential/reference needed by Z1.
6. **Least privilege** — biometric authorization is separate from ordinary application permissions.
7. **Auditability** — authorization decisions and security events may be audited, but biometric material itself must not be written to logs.
8. **Retention minimization** — biometric data and references must have an explicit retention policy where applicable.

## Architecture

```text
ZOE Identity
     |
     v
Governance Policy
     |
     v
Biometric Policy Engine
     |
     +----> External biometric authenticator / platform credential
     |
     v
Z1 Identity + RBAC
     |
     v
MemoryCore / Z1 Core
```

## Boundary with MemoryCore

MemoryCore may store a security event or a non-sensitive credential reference when permitted. It must not be used as a biometric sample store.

A biometric authentication result should be represented as an authorization event, for example:

- actor identity
- authentication method
- purpose
- decision
- timestamp
- policy/version identifier
- external credential reference (if required)

Do **not** store the biometric template, raw image, raw audio, fingerprint image, or equivalent biometric sample in ordinary MemoryCore records.

## Current implementation

`services/z1-core/biometric_security.py` provides:

- modality and purpose enums
- explicit biometric policy
- default-deny evaluation
- consent enforcement
- prohibition of raw biometric samples
- tests for the security boundary

This is a policy layer, not a biometric capture or matching engine.

## Future integration

The production implementation should integrate with platform-native credentials (for example Android device authentication) or a dedicated identity provider. Z1 should receive a success/failure assertion rather than the underlying biometric sample.

## Governance

Any future change that permits biometric template storage, raw sample processing, or biometric matching inside Z1 requires a separate security review and must not be enabled by changing a default flag alone.
