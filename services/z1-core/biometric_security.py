"""Z1 biometric identity and security policy primitives.

This module deliberately does not store biometric samples. It models policy,
consent, purpose limitation, retention, and audit requirements around an
external biometric authenticator or platform credential.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet


class BiometricModality(str, Enum):
    FACE = "face"
    FINGERPRINT = "fingerprint"
    IRIS = "iris"
    VOICE = "voice"
    OTHER = "other"


class BiometricPurpose(str, Enum):
    AUTHENTICATION = "authentication"
    IDENTITY_VERIFICATION = "identity_verification"
    ACCESS_CONTROL = "access_control"


class BiometricDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class BiometricPolicy:
    """Default-deny policy for biometric operations."""

    enabled: bool = False
    allowed_modalities: FrozenSet[BiometricModality] = frozenset()
    allowed_purposes: FrozenSet[BiometricPurpose] = frozenset()
    consent_required: bool = True
    raw_samples_allowed: bool = False
    template_storage_allowed: bool = False
    external_credential_only: bool = True
    retention_days: int | None = None

    def validate(self) -> None:
        if self.retention_days is not None and self.retention_days < 0:
            raise ValueError("retention_days must be non-negative or None")
        if self.raw_samples_allowed:
            raise ValueError("raw biometric samples are prohibited by Z1 policy")
        if not self.external_credential_only and self.template_storage_allowed:
            raise ValueError(
                "stored biometric templates require an explicitly reviewed security design"
            )


@dataclass(frozen=True)
class BiometricRequest:
    actor_id: str
    modality: BiometricModality
    purpose: BiometricPurpose
    consent_granted: bool


class BiometricPolicyEngine:
    """Evaluate biometric access requests without handling biometric material."""

    def __init__(self, policy: BiometricPolicy | None = None) -> None:
        self.policy = policy or BiometricPolicy()
        self.policy.validate()

    def evaluate(self, request: BiometricRequest) -> BiometricDecision:
        if not request.actor_id:
            return BiometricDecision.DENY
        if not self.policy.enabled:
            return BiometricDecision.DENY
        if request.modality not in self.policy.allowed_modalities:
            return BiometricDecision.DENY
        if request.purpose not in self.policy.allowed_purposes:
            return BiometricDecision.DENY
        if self.policy.consent_required and not request.consent_granted:
            return BiometricDecision.DENY
        return BiometricDecision.ALLOW
