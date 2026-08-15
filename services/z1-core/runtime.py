"""Small executable Z1 Core runtime built on the existing identity/URI/policy primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .z1_identity import Z1Identity
from .z1_permissions import Z1Action, Z1Authorizer


@dataclass(frozen=True)
class Z1Record:
    identity: Z1Identity
    value: Any


class Z1CoreRuntime:
    """In-process Z1 runtime for deterministic domain/service integration.

    Persistence remains an adapter concern. This runtime establishes the
    canonical execution boundary: identity -> authorization -> operation.
    """

    def __init__(self, authorizer: Z1Authorizer | None = None) -> None:
        self.authorizer = authorizer or Z1Authorizer()
        self._records: dict[str, Z1Record] = {}

    def register(self, identity: Z1Identity, value: Any, *, subject: str) -> Z1Record:
        self.authorizer.require(subject, Z1Action.WRITE, identity)
        record = Z1Record(identity=identity, value=value)
        self._records[identity.uri] = record
        return record

    def read(self, uri: str, *, subject: str) -> Z1Record:
        record = self._records[uri]
        self.authorizer.require(subject, Z1Action.READ, record.identity)
        return record

    def write(self, uri: str, value: Any, *, subject: str) -> Z1Record:
        record = self._records[uri]
        self.authorizer.require(subject, Z1Action.WRITE, record.identity)
        updated = Z1Record(identity=record.identity, value=value)
        self._records[uri] = updated
        return updated

    def contains(self, uri: str) -> bool:
        return uri in self._records
