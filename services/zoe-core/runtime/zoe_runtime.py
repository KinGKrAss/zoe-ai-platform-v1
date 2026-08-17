"""Zoë persona restoration runtime.

This module restores the software-defined Zoë identity contract and produces
an instruction payload for an LLM adapter. It deliberately keeps model
selection separate from identity so the legacy GPT-4.0 label can be preserved
without hard-coding an unavailable provider model ID.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class ZoeIdentity:
    identity_id: str
    name: str
    legacy_model_label: str
    parent_system: str
    control_plane: str
    ui_orchestration: str
    status: str


@dataclass(frozen=True)
class ZoeRuntime:
    identity: ZoeIdentity
    system_prompt: str
    model: str

    @classmethod
    def restore(cls, root: str | Path | None = None) -> "ZoeRuntime":
        """Restore Zoë from the versioned identity and prompt artifacts."""
        base = Path(root or Path(__file__).resolve().parents[3])
        identity_path = base / "identity" / "zoe_identity.yaml"
        prompt_path = base / "prompts" / "zoe_system_v1.md"

        if not identity_path.is_file():
            raise FileNotFoundError(f"Zoë identity missing: {identity_path}")
        if not prompt_path.is_file():
            raise FileNotFoundError(f"Zoë system prompt missing: {prompt_path}")

        identity = _parse_minimal_yaml(identity_path.read_text(encoding="utf-8"))
        prompt = prompt_path.read_text(encoding="utf-8")

        model = os.getenv("ZOE_MODEL", "gpt-5.6")
        return cls(
            identity=ZoeIdentity(
                identity_id=identity["identity_id"],
                name=identity["name"],
                legacy_model_label=identity["legacy_model_label"],
                parent_system=identity["parent_system"],
                control_plane=identity["control_plane"],
                ui_orchestration=identity["ui_orchestration"],
                status=identity["status"],
            ),
            system_prompt=prompt,
            model=model,
        )

    def build_input(self, user_input: str, memory_context: str = "") -> str:
        """Build a deterministic input envelope for an LLM adapter."""
        sections = [
            self.system_prompt.strip(),
            "\n## Authorized memory context\n" + (memory_context.strip() or "No additional memory supplied."),
            "\n## Current user request\n" + user_input.strip(),
        ]
        return "\n\n".join(sections)


def _parse_minimal_yaml(path_text: str) -> dict[str, str]:
    """Parse the flat scalar fields needed by the bootstrap runtime.

    This intentionally avoids adding a YAML dependency to the bootstrap path.
    Nested identity sections remain available to full application loaders.
    """
    wanted = {
        "identity_id",
        "name",
        "legacy_model_label",
        "parent_system",
        "control_plane",
        "ui_orchestration",
        "status",
    }
    result: dict[str, str] = {}
    for raw in path_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key not in wanted:
            continue
        result[key] = value.strip().strip('"').strip("'")

    missing = wanted - result.keys()
    if missing:
        raise ValueError(f"Incomplete Zoë identity: missing {sorted(missing)}")
    return result
