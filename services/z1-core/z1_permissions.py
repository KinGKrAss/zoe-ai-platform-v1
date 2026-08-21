"""Minimal deny-by-default authorization for Z1 resources."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from z1_identity import Z1Identity


class Z1Action(str, Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"


@dataclass(frozen=True)
class Z1Policy:
    subject: str
    actions: frozenset[Z1Action]
    namespaces: frozenset[str] = frozenset()
    resource_types: frozenset[str] = frozenset()

    def permits(self, subject: str, action: Z1Action, identity: Z1Identity) -> bool:
        if self.subject != subject or action not in self.actions:
            return False
        if self.namespaces and identity.uri.split("://", 1)[1].split("/", 1)[0] not in self.namespaces:
            return False
        if self.resource_types and identity.resource_type not in self.resource_types:
            return False
        return True


class Z1Authorizer:
    """Evaluates explicit policies; no policy means deny."""

    def __init__(self, policies: Iterable[Z1Policy] = ()) -> None:
        self._policies = list(policies)

    def add_policy(self, policy: Z1Policy) -> None:
        self._policies.append(policy)

    def is_allowed(self, subject: str, action: Z1Action, identity: Z1Identity) -> bool:
        return any(policy.permits(subject, action, identity) for policy in self._policies)

    def require(self, subject: str, action: Z1Action, identity: Z1Identity) -> None:
        if not self.is_allowed(subject, action, identity):
            raise PermissionError(
                f"Z1 access denied: subject={subject!r} action={action.value!r} uri={identity.uri!r}"
            )
