"""Governed Z1 plugin installation/update manager.

Plugins are installed only when they are explicitly allowlisted, signed, and
approved by the Z1 authorization boundary. The manager never executes plugin
code merely because a package is discoverable on the network.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
import shutil
import tempfile
import zipfile


class PluginPolicyError(RuntimeError):
    pass


@dataclass(frozen=True)
class PluginSpec:
    plugin_id: str
    version: str
    archive: Path
    sha256: str
    signature_verified: bool


class Z1PluginManager:
    def __init__(self, manifest_path: Path, install_root: Path) -> None:
        self.manifest_path = manifest_path
        self.install_root = install_root
        self.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    def _policy_allows(self, spec: PluginSpec, *, z1_authorized: bool) -> None:
        policy = self.manifest["policy"]
        if not policy.get("auto_install", False):
            raise PluginPolicyError("automatic plugin installation is disabled")
        if policy.get("require_allowlist", True) and not any(
            p.get("plugin_id") == spec.plugin_id and p.get("version") == spec.version
            for p in self.manifest.get("plugins", [])
        ):
            raise PluginPolicyError(f"plugin {spec.plugin_id}@{spec.version} is not allowlisted")
        if policy.get("require_signature", True) and not spec.signature_verified:
            raise PluginPolicyError("plugin signature has not been verified")
        if policy.get("require_z1_authorization", True) and not z1_authorized:
            raise PluginPolicyError("Z1 authorization is required")

    @staticmethod
    def _digest(path: Path) -> str:
        digest = sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def install(self, spec: PluginSpec, *, z1_authorized: bool) -> Path:
        self._policy_allows(spec, z1_authorized=z1_authorized)
        if self._digest(spec.archive) != spec.sha256:
            raise PluginPolicyError("plugin archive checksum mismatch")
        if spec.archive.suffix.lower() != ".zip":
            raise PluginPolicyError("only ZIP plugin bundles are supported")

        target = self.install_root / spec.plugin_id / spec.version
        self.install_root.mkdir(parents=True, exist_ok=True)
        if target.exists():
            return target

        with tempfile.TemporaryDirectory(prefix="z1-plugin-") as tmp:
            staging = Path(tmp) / "plugin"
            staging.mkdir()
            with zipfile.ZipFile(spec.archive) as archive:
                members = archive.infolist()
                for member in members:
                    destination = (staging / member.filename).resolve()
                    if not str(destination).startswith(str(staging.resolve()) + "/"):
                        raise PluginPolicyError("unsafe plugin archive path")
                archive.extractall(staging)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(staging), str(target))

        return target
