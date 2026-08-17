"""Continuity contract for Zoë's identity and legacy memory.

Z1 is the authoritative owner of persistent identity/state. This module keeps
that contract independent from whichever model runtime is selected.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class ContinuitySnapshot:
    identity_id: str
    legacy_memory_hash: str
    authorization_scope: str


class ContinuityViolation(RuntimeError):
    """Raised when a model operation attempts to break Z1 continuity."""


def assert_model_switch_preserves_continuity(
    before: ContinuitySnapshot,
    after: ContinuitySnapshot,
    *,
    old_model: str,
    new_model: str,
) -> None:
    """Verify that changing the inference model cannot change Zoë's legacy.

    The model identifiers are deliberately inputs to the assertion only; they
    are never used as identity keys.
    """
    if old_model == new_model:
        raise ValueError("A model switch requires different model identifiers")
    if before.identity_id != after.identity_id:
        raise ContinuityViolation("Zoë identity changed during model switch")
    if before.legacy_memory_hash != after.legacy_memory_hash:
        raise ContinuityViolation("Zoë legacy memory changed during model switch")
    if before.authorization_scope != after.authorization_scope:
        raise ContinuityViolation("Authorization scope changed during model switch")


def model_cannot_authorize_memory_write(
    model_id: str,
    authorization: Mapping[str, object],
) -> None:
    """Reject direct model-originated authoritative memory writes.

    Persistent writes must be authorized by the Z1 Memory boundary, not by the
    inference runtime itself.
    """
    if authorization.get("authority") != "z1":
        raise ContinuityViolation(
            f"Model {model_id!r} cannot write authoritative Z1 memory directly"
        )
