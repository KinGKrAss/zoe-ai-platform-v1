"""Minimal Z1 Core runtime lifecycle and truth/safety policy."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone


class RuntimeStatus(str, Enum):
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    STOPPED = "STOPPED"


class VerificationStatus(str, Enum):
    USER_REPORTED = "USER_REPORTED"
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    DERIVED = "DERIVED"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class RuntimeComponent:
    name: str
    version: str = "1.0.0"
    status: RuntimeStatus = RuntimeStatus.INITIALIZING


@dataclass
class Z1Runtime:
    """Lifecycle controller for the Z1 Core runtime.

    This layer intentionally contains no database driver. Persistence is supplied
    by adapters so policy and lifecycle remain independently testable.
    """

    components: dict[str, RuntimeComponent] = field(default_factory=dict)
    started_at: datetime | None = None

    def register(self, name: str, version: str = "1.0.0") -> RuntimeComponent:
        component = RuntimeComponent(name=name, version=version)
        self.components[name] = component
        return component

    def start(self) -> None:
        if not self.components:
            raise RuntimeError("Z1 runtime cannot start without registered components")
        self.components = {
            name: RuntimeComponent(name=c.name, version=c.version, status=RuntimeStatus.READY)
            for name, c in self.components.items()
        }
        self.started_at = datetime.now(timezone.utc)

    def status(self) -> RuntimeStatus:
        if not self.components:
            return RuntimeStatus.STOPPED
        statuses = {component.status for component in self.components.values()}
        if statuses == {RuntimeStatus.READY}:
            return RuntimeStatus.READY
        if RuntimeStatus.DEGRADED in statuses:
            return RuntimeStatus.DEGRADED
        if RuntimeStatus.STOPPED in statuses:
            return RuntimeStatus.STOPPED
        return RuntimeStatus.INITIALIZING


def can_mark_verified(*, evidence_verified: bool, authorized_actor: bool) -> bool:
    """Verification is a controlled state transition, never a default."""
    return evidence_verified and authorized_actor
