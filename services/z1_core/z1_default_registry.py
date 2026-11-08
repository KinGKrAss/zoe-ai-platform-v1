"""Default Z1 namespace registry."""

from .namespace_adapters import (
    resolve_3d,
    resolve_agents,
    resolve_documents,
    resolve_finance,
    resolve_memory,
    resolve_ppt,
)
from .z1_resolver import Z1ResolverRegistry


def build_core_registry() -> Z1ResolverRegistry:
    registry = Z1ResolverRegistry()
    registry.register("3d", resolve_3d)
    registry.register("ppt", resolve_ppt)
    registry.register("finance", resolve_finance)
    registry.register("memory", resolve_memory)
    registry.register("documents", resolve_documents)
    registry.register("agents", resolve_agents)
    return registry
