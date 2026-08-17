"""Pytest bootstrap for legacy service layouts.

The Zoë Memory implementation lives under a historical ``zoe-memory``
service directory. Its Python package is ``zoe_memory`` beneath that
service root, so expose that root during test collection without changing
the production package layout.
"""

from pathlib import Path
import sys


ZOe_MEMORY_ROOT = Path(__file__).resolve().parent / "services" / "zoe-memory"

if str(ZOe_MEMORY_ROOT) not in sys.path:
    sys.path.insert(0, str(ZOe_MEMORY_ROOT))
