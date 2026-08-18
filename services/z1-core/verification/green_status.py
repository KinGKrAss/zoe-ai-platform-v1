"""Deterministic Z1 verification status evaluation.

This module contains no UI concerns. The Control Plane derives status from checks;
the Command Center should consume the resulting status only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping


class VerificationStatus(StrEnum):
    VERIFIED = "VERIFIED"
    PENDING = "PENDING"
    INVALID = "INVALID"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class VerificationResult:
    status: VerificationStatus
    reason: str


EVM_REQUIRED_CHECKS = frozenset(
    {
        "ADDRESS_FORMAT",
        "CHAIN_SUPPORTED",
        "ADDRESS_TYPE",
        "RPC_READ",
        "BALANCE_READ",
        "TRANSACTION_READ",
        "TOKEN_STATE_READ",
    }
)


def evaluate_evm_status(
    checks: Mapping[str, bool],
    *,
    invalid: bool = False,
    blocked: bool = False,
) -> VerificationResult:
    """Derive authoritative EVM status from verification evidence."""
    if blocked:
        return VerificationResult(VerificationStatus.BLOCKED, "policy block")
    if invalid:
        return VerificationResult(VerificationStatus.INVALID, "invalidity established")

    missing = sorted(code for code in EVM_REQUIRED_CHECKS if code not in checks)
    failed = sorted(code for code in EVM_REQUIRED_CHECKS if checks.get(code) is False)

    if missing:
        return VerificationResult(
            VerificationStatus.PENDING,
            f"missing required checks: {', '.join(missing)}",
        )
    if failed:
        return VerificationResult(
            VerificationStatus.PENDING,
            f"failed required checks: {', '.join(failed)}",
        )

    return VerificationResult(VerificationStatus.VERIFIED, "all required checks passed")
