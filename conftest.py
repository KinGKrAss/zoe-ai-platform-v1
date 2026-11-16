"""Expose the Z1 core directory as ``services.z1_core`` for pytest."""

import importlib.util
import sys
import types
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_Z1_CORE = _ROOT / "services" / "z1_core"
if not _Z1_CORE.is_dir():
    _Z1_CORE = _ROOT / "services" / "z1-core"


def _register_z1_core() -> None:
    if "services.z1_core" in sys.modules:
        return
    services = sys.modules.get("services")
    if services is None:
        services = types.ModuleType("services")
        services.__path__ = [str(_ROOT / "services")]
        sys.modules["services"] = services
    spec = importlib.util.spec_from_file_location(
        "services.z1_core",
        _Z1_CORE / "__init__.py",
        submodule_search_locations=[str(_Z1_CORE)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["services.z1_core"] = module
    services.z1_core = module
    spec.loader.exec_module(module)


_register_z1_core()
