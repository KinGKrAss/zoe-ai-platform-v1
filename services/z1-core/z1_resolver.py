"""Z1 URI resolver registry.

The resolver layer deliberately separates URI identity from resource access.
A handler receives a canonical Z1 URI and is responsible for resolving it to
an application-specific resource. No backend or transport semantics are
embedded in the URI itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping
from urllib.parse import urlsplit

from .z1_uri import Z1URI, parse_z1_uri


class Z1ResolutionError(RuntimeError):
    """Base error for resolver failures."""


class Z1NamespaceNotRegistered(Z1ResolutionError):
    """Raised when no handler exists for a URI namespace."""


class Z1ResourceNotFound(Z1ResolutionError):
    """Raised when a registered handler cannot resolve a resource."""


@dataclass(frozen=True)
class Z1Resource:
    """Normalized resolver result."""

    uri: str
    namespace: str
    resource_type: str
    resource_id: str
    value: Any
    metadata: Mapping[str, Any] | None = None


ResolverHandler = Callable[[Z1URI], Z1Resource | Any]


class Z1ResolverRegistry:
    """Registry mapping Z1 namespaces to backend adapters.

    Registration is explicit so new Z1 domains can be added without changing
    the URI parser. Handlers must accept the parsed/canonical Z1URI object.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, ResolverHandler] = {}

    def register(self, namespace: str, handler: ResolverHandler) -> None:
        namespace = namespace.strip().lower()
        if not namespace or "/" in namespace or " " in namespace:
            raise ValueError("Invalid Z1 namespace")
        if namespace in self._handlers:
            raise ValueError(f"Z1 namespace already registered: {namespace}")
        self._handlers[namespace] = handler

    def unregister(self, namespace: str) -> None:
        self._handlers.pop(namespace.strip().lower(), None)

    def namespaces(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))

    def resolve(self, uri: str | Z1URI) -> Z1Resource | Any:
        parsed = parse_z1_uri(uri) if isinstance(uri, str) else uri
        handler = self._handlers.get(parsed.namespace)
        if handler is None:
            raise Z1NamespaceNotRegistered(parsed.namespace)
        return handler(parsed)


def namespace_of(uri: str) -> str:
    """Return the namespace without resolving the resource."""
    parsed = parse_z1_uri(uri)
    return parsed.namespace


def default_registry() -> Z1ResolverRegistry:
    """Return an empty registry ready for application adapters."""
    return Z1ResolverRegistry()
