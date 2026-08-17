"""Compatibility package for the legacy hyphenated Z1 Core directory.

The implementation remains in ``services/z1-core`` for backward compatibility,
while this importable package exposes it under the valid Python name
``services.z1_core``.
"""

from pathlib import Path

__path__ = [str(Path(__file__).resolve().parent.parent / "z1-core")]
