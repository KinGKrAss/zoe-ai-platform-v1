"""Deterministic Z1 verification state engine.

The UI must consume this derived state; it must never manufacture a green state.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CheckStatus(str, Enum):
    PASS = "PASS"
    PENDING = "PENDING"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"


class VerificationState(str, Enum):
    VERIFIED = "VERIFIED"
    PENDING = "PENDING"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class VerificationCheck:
    code: str
    status: CheckStatus
    required: bool = True


@dataclass(frozen=True)
class VerificationResult:
    state: VerificationState
    score: int
    passed_required: int
    required_checks: int


def derive_verification_state(
    checks: list[VerificationCheck], *, blocked: bool = False
) -> VerificationResult:
    """Derive the canonical Z1 status from verification evidence.

    Rules:
    - BLOCKED always wins.
    - Any required FAIL produces FAILED.
    - Any required PENDING/SKIPPED produces PENDING.
    - Only all required PASS produces VERIFIED (green).
    - Score is the percentage of required checks that passed.
    """
    if blocked:
        return VerificationResult(VerificationState.BLOCKED, 0, 0, 0)

    required = [check for check in checks if check.required]
    passed = sum(check.status is CheckStatus.PASS for check in required)
    total = len(required)
    score = round((passed / total) * 100) if total else 0

    if any(check.status is CheckStatus.FAIL for check in required):
        state = VerificationState.FAILED
    elif total == 0 or any(
        check.status in (CheckStatus.PENDING, CheckStatus.SKIPPED)
        for check in required
    ):
        state = VerificationState.PENDING
    else:
        state = VerificationState.VERIFIED

    return VerificationResult(state, score, passed, total)


DEFAULT_BLOCKCHAIN_CHECKS = (
    "address_format",
    "chain_supported",
    "address_type",
    "rpc_readable",
    "transaction_history",
    "token_state",
    "ownership_evidence",
    "audit_record",
)
