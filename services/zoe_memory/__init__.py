"""Compatibility package for the legacy hyphenated Zoë Memory directory."""

from pathlib import Path

__path__ = [str(Path(__file__).resolve().parent.parent / "zoe-memory")]
