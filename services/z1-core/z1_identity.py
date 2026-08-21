"""Identity primitives for Z1 resources."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from z1_uri import Z1URI, parse_z1_uri


@dataclass(frozen=True)
class Z1Identity:
    """Stable identity and governance metadata for a Z1 resource."""

    uri: str
    resource_type: str
    owner: str
    version: str = "1"
    integrity: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        uri: str | Z1URI,
        resource_type: str,
        owner: str,
        *,
        version: str = "1",
        integrity: str | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> "Z1Identity":
        parsed = parse_z1_uri(uri) if isinstance(uri, str) else uri
        if not owner.strip():
            raise ValueError("Z1 resource owner must not be empty")
        if not resource_type.strip():
            raise ValueError("Z1 resource type must not be empty")
        return cls(
            uri=parsed.canonical,
            resource_type=resource_type.strip(),
            owner=owner.strip(),
            version=version.strip() or "1",
            integrity=integrity,
            metadata=dict(metadata or {}),
        )
