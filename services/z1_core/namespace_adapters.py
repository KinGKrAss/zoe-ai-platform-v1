"""Reference adapters for the first Z1 namespaces.

These adapters intentionally return structured resource descriptors rather
than pretending that a database, API, blockchain or file store exists. Real
connectors can replace them through Z1ResolverRegistry.register().
"""

from __future__ import annotations

from .z1_resolver import Z1Resource


def _resource(uri, resource_type: str, resource_id: str) -> Z1Resource:
    return Z1Resource(
        uri=uri.canonical,
        namespace=uri.namespace,
        resource_type=resource_type,
        resource_id=resource_id,
        value=None,
        metadata={"status": "unbound", "resolver": "reference-adapter"},
    )


def resolve_3d(uri):
    return _resource(uri, "3d-resource", "/".join(uri.path_segments))


def resolve_ppt(uri):
    return _resource(uri, "ppt-resource", "/".join(uri.path_segments))


def resolve_finance(uri):
    return _resource(uri, "financial-resource", "/".join(uri.path_segments))


def resolve_memory(uri):
    return _resource(uri, "memory-resource", "/".join(uri.path_segments))


def resolve_documents(uri):
    return _resource(uri, "document-resource", "/".join(uri.path_segments))


def resolve_agents(uri):
    return _resource(uri, "agent-resource", "/".join(uri.path_segments))
