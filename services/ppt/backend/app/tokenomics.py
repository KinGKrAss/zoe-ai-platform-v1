from __future__ import annotations

import base64
import hashlib
import logging
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

LOGGER = logging.getLogger("ppt.tokenomics")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _default_path(name: str) -> Path:
    return _repo_root() / "docs" / "tokenomics" / name


class TokenomicsError(RuntimeError):
    pass


class FeeAllocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    safety_reserve: int = Field(ge=0, le=10_000)
    operations: int = Field(ge=0, le=10_000)
    ecosystem: int = Field(ge=0, le=10_000)


class TokenDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    symbol: str = Field(min_length=1)
    decimals: int = Field(ge=0, le=30)
    initial_supply_wei: str

    @field_validator("initial_supply_wei")
    @classmethod
    def validate_initial_supply(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("initial_supply_wei must be an unsigned integer string")
        return value


class CollateralDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reserve_currency: str = Field(min_length=1)
    reserve_unit: str = Field(min_length=1)
    min_collateral_ratio_e18: str
    target_collateral_ratio_e18: str

    @field_validator("min_collateral_ratio_e18", "target_collateral_ratio_e18")
    @classmethod
    def validate_e18(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("ratio must be an unsigned integer string")
        return value


class LimitsDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_daily_mint_bps: int = Field(ge=0, le=10_000)
    max_daily_redeem_outflow_bps: int = Field(ge=0, le=10_000)


class FeesDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mint_fee_bps: int = Field(ge=0, le=2_000)
    redeem_fee_bps: int = Field(ge=0, le=2_000)
    allocation_bps: FeeAllocation


class RiskControls(BaseModel):
    model_config = ConfigDict(extra="forbid")

    peg_deviation_threshold_bps: int = Field(ge=0, le=10_000)
    reserve_staleness_max_seconds: int = Field(ge=0)
    oracle_staleness_max_seconds: int = Field(ge=0)
    circuit_breaker_enabled: bool
    guarded_redeem_mode_enabled: bool


class RateLimitDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    write_per_minute: int = Field(gt=0, le=10_000)


class ApiDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    require_jwt: bool
    require_idempotency_on_write: bool
    rate_limit: RateLimitDef


class GovernanceDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timelock_seconds: int = Field(ge=0)
    emergency_pause_allowed: bool


class TokenomicsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str = Field(min_length=1)
    token: TokenDef
    collateral: CollateralDef
    limits: LimitsDef
    fees: FeesDef
    risk_controls: RiskControls
    api: ApiDef
    governance: GovernanceDef

    @field_validator("fees")
    @classmethod
    def validate_allocation_sum(cls, value: FeesDef) -> FeesDef:
        total = value.allocation_bps.safety_reserve + value.allocation_bps.operations + value.allocation_bps.ecosystem
        if total != 10_000:
            raise ValueError(f"fees.allocation_bps must sum to 10000, got {total}")
        return value


@dataclass(frozen=True)
class RuntimeTokenomics:
    raw: TokenomicsConfig
    min_collateral_ratio: Decimal
    target_collateral_ratio: Decimal
    mint_fee_ratio: Decimal
    redeem_fee_ratio: Decimal


class TokenomicsManager:
    def __init__(
        self,
        config_path: Path | None = None,
        sha256_path: Path | None = None,
        signature_path: Path | None = None,
        public_key_path: Path | None = None,
        enforce_integrity: bool | None = None,
    ) -> None:
        self.config_path = config_path or Path(os.getenv("TOKENOMICS_CONFIG_PATH", _default_path("parameters-v1.0.yaml")))
        self.sha256_path = sha256_path or Path(os.getenv("TOKENOMICS_SHA256_PATH", _default_path("parameters-v1.0.sha256")))
        self.signature_path = signature_path or Path(os.getenv("TOKENOMICS_SIGNATURE_PATH", _default_path("parameters-v1.0.sig")))
        self.public_key_path = public_key_path or Path(os.getenv("TOKENOMICS_PUBLIC_KEY_PATH", _default_path("parameters-v1.0.pub")))

        if enforce_integrity is None:
            enforce_env = os.getenv("TOKENOMICS_ENFORCEMENT", "true").strip().lower()
            self.enforce_integrity = enforce_env not in {"0", "false", "no"}
        else:
            self.enforce_integrity = enforce_integrity

        self._runtime: RuntimeTokenomics | None = None
        self._watch_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.RLock()
        self._last_fingerprint: dict[Path, tuple[int, int]] = {}
        self._audit_events: list[dict[str, str]] = []

    def load_initial(self) -> RuntimeTokenomics:
        runtime = self._load_runtime()
        with self._lock:
            self._runtime = runtime
        return runtime

    def current(self) -> RuntimeTokenomics:
        with self._lock:
            if self._runtime is None:
                return self.load_initial()
            return self._runtime

    def audit_events(self) -> list[dict[str, str]]:
        with self._lock:
            return list(self._audit_events)

    def start_watcher(self, *, poll_interval_seconds: float = 0.5, debounce_seconds: float = 1.0) -> None:
        if self._watch_thread and self._watch_thread.is_alive():
            return
        self._stop_event.clear()
        self._detect_changes()
        self._watch_thread = threading.Thread(
            target=self._watch_loop,
            kwargs={"poll_interval_seconds": poll_interval_seconds, "debounce_seconds": debounce_seconds},
            name="tokenomics-watcher",
            daemon=True,
        )
        self._watch_thread.start()

    def close(self) -> None:
        self._stop_event.set()
        if self._watch_thread and self._watch_thread.is_alive():
            self._watch_thread.join(timeout=2.0)

    def _watched_paths(self) -> list[Path]:
        return [self.config_path, self.sha256_path, self.signature_path, self.public_key_path]

    def _watch_loop(self, *, poll_interval_seconds: float, debounce_seconds: float) -> None:
        pending_since: float | None = None
        while not self._stop_event.wait(poll_interval_seconds):
            changed = self._detect_changes()
            if changed:
                pending_since = pending_since or time.time()
            if pending_since and (time.time() - pending_since) >= debounce_seconds:
                pending_since = None
                try:
                    runtime = self._load_runtime()
                except Exception as exc:  # noqa: BLE001
                    self._audit("tokenomics_reload_failed", str(exc), level="error")
                    LOGGER.exception("Tokenomics reload failed; keeping last-known-good config")
                else:
                    with self._lock:
                        self._runtime = runtime
                    self._audit("tokenomics_reloaded", "tokenomics config reloaded", level="info")

    def _detect_changes(self) -> bool:
        changed = False
        for path in self._watched_paths():
            try:
                stat = path.stat()
                fingerprint = (stat.st_mtime_ns, stat.st_size)
            except FileNotFoundError:
                fingerprint = (-1, -1)
            previous = self._last_fingerprint.get(path)
            if previous is None:
                self._last_fingerprint[path] = fingerprint
                continue
            if fingerprint != previous:
                changed = True
                self._last_fingerprint[path] = fingerprint
        return changed

    def _audit(self, event: str, message: str, *, level: str) -> None:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "level": level,
            "message": message,
        }
        with self._lock:
            self._audit_events.append(payload)
            self._audit_events = self._audit_events[-100:]

    def _load_runtime(self) -> RuntimeTokenomics:
        data = self.config_path.read_bytes()

        if self.enforce_integrity:
            self._verify_sha256(data)
            self._verify_signature(data)

        raw_yaml: Any = yaml.safe_load(data)
        try:
            config = TokenomicsConfig.model_validate(raw_yaml)
        except ValidationError as exc:
            raise TokenomicsError(f"tokenomics validation failed: {exc}") from exc

        min_ratio = Decimal(config.collateral.min_collateral_ratio_e18) / Decimal(10**18)
        target_ratio = Decimal(config.collateral.target_collateral_ratio_e18) / Decimal(10**18)

        return RuntimeTokenomics(
            raw=config,
            min_collateral_ratio=min_ratio,
            target_collateral_ratio=target_ratio,
            mint_fee_ratio=Decimal(config.fees.mint_fee_bps) / Decimal(10_000),
            redeem_fee_ratio=Decimal(config.fees.redeem_fee_bps) / Decimal(10_000),
        )

    def _verify_sha256(self, data: bytes) -> None:
        expected = self.sha256_path.read_text(encoding="utf-8").strip().split()[0].lower()
        actual = hashlib.sha256(data).hexdigest().lower()
        if expected != actual:
            raise TokenomicsError("tokenomics sha256 mismatch")

    def _verify_signature(self, data: bytes) -> None:
        signature = base64.b64decode(self.signature_path.read_text(encoding="utf-8").strip())
        public_key_raw = base64.b64decode(self.public_key_path.read_text(encoding="utf-8").strip())
        if len(public_key_raw) != 32:
            raise TokenomicsError("tokenomics public key must be 32-byte Ed25519 key")
        verifier = Ed25519PublicKey.from_public_bytes(public_key_raw)
        try:
            verifier.verify(signature, data)
        except Exception as exc:  # noqa: BLE001
            raise TokenomicsError("tokenomics signature invalid") from exc
