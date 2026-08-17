from services.z1_core.z1_default_registry import build_core_registry
from services.z1_core.z1_resolver import Z1NamespaceNotRegistered, Z1ResolverRegistry


def test_core_namespaces_are_registered():
    registry = build_core_registry()
    assert registry.namespaces() == (
        "3d",
        "agents",
        "documents",
        "finance",
        "memory",
        "ppt",
    )


def test_resolver_returns_canonical_resource_descriptor():
    result = build_core_registry().resolve("z1://finance/accounts/main")
    assert result.uri == "z1://finance/accounts/main"
    assert result.namespace == "finance"
    assert result.resource_id == "accounts/main"
    assert result.metadata["status"] == "unbound"


def test_unknown_namespace_is_explicit():
    registry = Z1ResolverRegistry()
    try:
        registry.resolve("z1://unknown/resource")
    except Z1NamespaceNotRegistered as exc:
        assert str(exc) == "unknown"
    else:
        raise AssertionError("Expected Z1NamespaceNotRegistered")
